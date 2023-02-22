import logging
from typing import Callable, List

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from helpers.selenium_helpers import (wait_for_element,
                                      wait_for_element_to_not_exist,
                                      wait_until_page_load)
from school.school_ratings import filter_low_rated_schools

logger = logging.getLogger(__name__)


class PropertySearch:
    def __init__(self, username, password, **kwargs):
        """
        Initializes the PropertySearch object with search parameters.

        :param username: MLS username
        :param password: MLS password
        :param kwargs: search parameters (beds, baths, sqft, style, price, county, garage, sewer)
        """

        # Store search parameters
        self.username = username
        self.password = password
        self.beds = kwargs.get('beds', 3)
        self.baths = kwargs.get('baths', 2)
        self.sqft = kwargs.get('sqft', 1000)
        self.style = kwargs.get('style', 'Single Family Residence')
        self.price = kwargs.get('price', '500-')
        self.county = kwargs.get('county', 'Orange,Seminole,Lake,Osceola,Volusia,Polk')
        self.garage = kwargs.get('garage', True)
        self.sewer = kwargs.get('sewer', ['26289', '26293', '26294'])

        # Configure ChromeDriver
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # Log in to MLS
        self.__login()

    def __login(self):
        """
        Logs in to the Stellar MLS website with the provided username and password.
        """
        try:
            # Load the login page
            self.driver.get("https://central.stellarmls.com/")

            # Wait for the page to fully load
            wait_until_page_load(self.driver)

            # Find the username input field and enter the username
            username_input = self.driver.find_element(by=By.ID, value="loginId")
            username_input.send_keys(self.username)

            # Find the password input field and enter the password
            password_input = self.driver.find_element(by=By.ID, value="password")
            password_input.send_keys(self.password)

            # Click the login button
            login_button = self.driver.find_element(by=By.ID, value="btn-login")
            login_button.click()

            # Wait for the login button to disappear and the billboard to appear
            wait_for_element_to_not_exist(self.driver, By.ID, "btn-login")
            wait_for_element(self.driver, By.ID, "billboard")

            # Check if the login was successful by searching for the "Welcome to Stellar Central" text on the page
            success_msg = "Welcome to Stellar Central"
            if success_msg in self.driver.page_source:
                logger.info("Login successful")
                logger.info("Current window title: %s", self.driver.title)
            else:
                logger.error("Login failed")
                logger.error("Current window title: %s", self.driver.title)

        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"An error occurred during login: {e}")

    from typing import Callable, List

    def search_properties(self) -> None:
        """
        Searches for properties that match the search criteria and applies various filters to the resulting dataframe.
        Generates an Excel file with the resulting properties and sends it via email.
        """
        # Perform the search
        self.__residential_search()

        # Apply filters to the search results
        filters: List[Callable[[], None]] = [
            self.__clean_properties_df,
            self.__calculate_hoa,  # Filter properties with high HOA fees. Caches results for 6 hours.
            self.__recalculate_tax,  # Recalculate property taxes based on estimated property value
            self.__filter_properties_with_no_schools,  # Remove properties with no school data. No caching.
            filter_low_rated_schools,  # Remove properties with low rated schools. No caching.
            self.__calculate_rent,  # Estimate monthly rent for each property. Caches results for 6 hours.
            self.__filter_by_cap_rate,  # Filter properties with a cap rate below a specified threshold.
        ]

        # Apply each filter to the dataframe
        for f in filters:
            f()

        # Export the filtered search results to Excel
        self.__to_excel()

        # Email the Excel file
        self.__email()


