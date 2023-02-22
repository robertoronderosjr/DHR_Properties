"""
This module contains a class for searching properties on Stellar MLS website.

This module uses the Selenium WebDriver and ChromeDriver to interact with the website,
applies filters to the search results, and generates an Excel file with the resulting properties.

It also sends the file via email.

"""
import logging
from typing import Callable, List

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from config import MLSIDs, MLSPages
from helpers.chrome_driver import ChromeDriver
from helpers.selenium_helpers import (
    wait_for_element,
    wait_for_element_to_not_exist,
    wait_until_page_load,
)

# from school.school_ratings import filter_low_rated_schools

logger = logging.getLogger(__name__)


class PropertySearch:
    """
    This class provides a way to search for properties on Stellar MLS website.

    """

    def __init__(self, username: str, password: str, **kwargs):
        """
        Initializes the PropertySearch object with search parameters.

        :param username: MLS username
        :param password: MLS password
        :param kwargs: any number of keyword arguments for search parameters
        """
        # Store search parameters
        self.username = username
        self.password = password
        self.beds = kwargs.get("beds", 3)
        self.baths = kwargs.get("baths", 2)
        self.sqft = kwargs.get("sqft", 1000)
        self.style = kwargs.get("style", "Single Family Residence")
        self.price = kwargs.get("price", "500-")
        self.county = kwargs.get("county", "Orange,Seminole,Lake,Osceola,Volusia,Polk")
        self.garage = kwargs.get("garage", True)
        self.sewer = kwargs.get("sewer", ["26289", "26293", "26294"])
        self.year_built = kwargs.get("year_built", "1960+")

        # Get a configured Chrome driver instance
        chrome_driver = ChromeDriver(headless=True)
        self.driver = chrome_driver.get_driver()

        # Log in to MLS
        self.__login()

    def __login(self):
        """
        Logs in to the Stellar MLS website with the provided username and password.
        """
        try:
            # Load the login page
            self.driver.get(MLSPages.LOGIN_PAGE)

            # Wait for the page to fully load
            wait_until_page_load(self.driver)

            # Find the username input field and enter the username
            username_input = self.driver.find_element(by=By.ID, value=MLSIDs.LOGIN_ID)
            username_input.send_keys(self.username)

            # Find the password input field and enter the password
            password_input = self.driver.find_element(by=By.ID, value=MLSIDs.PASSWORD)
            password_input.send_keys(self.password)

            # Click the login button
            login_button = self.driver.find_element(by=By.ID, value=MLSIDs.LOGIN_BUTTON)
            login_button.click()

            # Wait for the login button to disappear and the billboard to appear
            wait_for_element_to_not_exist(self.driver, By.ID, MLSIDs.LOGIN_BUTTON)
            wait_for_element(self.driver, By.ID, MLSIDs.BILLBOARD)

            # Check if the login was successful by searching for the
            # "Welcome to Stellar Central" text on the page
            success_msg = MLSIDs.SUCCESS_MESSAGE
            if success_msg in self.driver.page_source:
                logger.info("Login successful")
                logger.info("Current window title: %s", self.driver.title)
            else:
                logger.error("Login failed")
                logger.error("Current window title: %s", self.driver.title)

        except (TimeoutException, NoSuchElementException) as ex:
            logger.error("An error occurred during login: %s", ex)

    def search_properties(self) -> None:
        """
        Searches for properties that match the search criteria and applies various filters
        to the resulting dataframe. Generates an Excel file with the resulting properties
        and sends it via email.
        """
        # Perform the search
        self.__residential_search()

        # Apply filters to the search results
        filters: List[Callable[[], None]] = [
            self.__clean_properties_df,
            # Filter properties with high HOA fees. Caches results for 6 hours.
            self.__calculate_hoa,
            self.__recalculate_tax,  # Recalculate property taxes based on estimated property value
            # Remove properties with no school data. No caching.
            self.__filter_properties_with_no_schools,
            # Remove properties with low rated schools. No caching.
            # filter_low_rated_schools,
            # Estimate monthly rent for each property. Caches results for 6 hours.
            self.__calculate_rent,
            # Filter properties with a cap rate below a specified threshold.
            self.__filter_by_cap_rate,
        ]

        # Apply each filter to the dataframe
        for filter_func in filters:
            filter_func()

        # Export the filtered search results to Excel
        self.__to_excel()

        # Email the Excel file
        self.__email()

    def __residential_search(self):
        # MLS matrix main page
        self.driver.get(MLSPages.MAIN_PAGE)

        # Goto quick search
        wait_for_element(self.driver, By.ID, MLSIDs.YEAR_BUILT)
        self.driver.get(MLSPages.RESIDENTIAL_QUICK_SEARCH)
        logger.info("Current window title: %s", self.driver.title)

        # Year Built
        self.driver.find_element(by=By.ID, value=MLSIDs.YEAR_BUILT).send_keys(f"{self.year_built}+")

        # Total Bedrooms
        self.driver.find_element(by=By.ID, value=MLSIDs.TOTAL_BEDROOMS).send_keys(f"{self.beds}+")

        # Total Full Bathrooms
        self.driver.find_element(by=By.ID, value=MLSIDs.TOTAL_FULL_BATHROOMS).send_keys(
            f"{self.baths}+"
        )

        # Price
        self.driver.find_element(by=By.ID, value=MLSIDs.PRICE).send_keys(f"{self.price}")

        # Sq Ft Heated
        self.driver.find_element(by=By.ID, value=MLSIDs.SQ_FT_HEATED).send_keys(f"{self.sqft}+")

        # Property Style
        property_style_selector = Select(
            self.driver.find_element(by=By.ID, value=MLSIDs.PROPERTY_STYLE)
        )
        property_style_selector.select_by_visible_text(self.style)

        # County
        self.driver.find_element(by=By.ID, value=MLSIDs.COUNTY).send_keys(self.county)

        # Garage or carport
        if self.garage:
            self.driver.find_element(by=By.ID, value=MLSIDs.GARAGE_CARPORT).click()

        # Sewer filters
        sewer_selector = self.driver.find_element(by=By.ID, value=MLSIDs.SEWER)
        options = sewer_selector.find_elements(by=By.TAG_NAME, value="option")
        sewer_values = [option.get_attribute("value") for option in options]
        sewer_input_radios = self.driver.find_elements(
            by=By.NAME, value=MLSIDs.SEWER_INPUT_RADIO_AND
        )
        for value in self.sewer:
            index = sewer_values.index(value)
            ActionChains(self.driver).key_down(Keys.CONTROL).click(
                sewer_input_radios[index]
            ).key_up(Keys.CONTROL).perform()

        # Click Search
        self.driver.find_element(by=By.ID, value="matrixResultsButtons1_lbSearch").click()

        self.__add_all_properties_to_df()

    def __clean_properties_df(self):
        pass

    def __calculate_hoa(self):
        pass

    def __recalculate_tax(self):
        pass

    def __filter_properties_with_no_schools(self):
        pass

    def __calculate_rent(self):
        pass

    def __filter_by_cap_rate(self):
        pass

    def __to_excel(self):
        pass

    def __email(self):
        pass

    def __add_all_properties_to_df(self):
        pass
