from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def wait_until_page_load(driver):
    """
    Waits for the page to fully load before proceeding.

    :param driver: The Selenium WebDriver instance.
    """
    WebDriverWait(driver, timeout=10).until(
        lambda x: x.execute_script("return document.readyState === 'complete'")
    )


def wait_for_element(driver, by, value, timeout=10):
    """
    Waits for an element to appear on the page.

    :param driver: The Selenium WebDriver instance.
    :param by: The method used to locate the element (e.g. By.ID, By.CLASS_NAME, etc.).
    :param value: The value of the identifier used to locate the element.
    :param timeout: The maximum amount of time to wait for the element to appear (in seconds).
    """
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


def wait_for_element_to_not_exist(driver, by, value, timeout=10):
    """
    Waits for an element to disappear from the page.

    :param driver: The Selenium WebDriver instance.
    :param by: The method used to locate the element (e.g. By.ID, By.CLASS_NAME, etc.).
    :param value: The value of the identifier used to locate the element.
    :param timeout: The maximum amount of time to wait for the element to disappear (in seconds).
    """
    WebDriverWait(driver, timeout).until(EC.invisibility_of_element_located((by, value)))


def wait_until_text_present(driver, by, value, text, timeout=10):
    """
    Waits for specific text to appear in an element on the page.

    :param driver: The Selenium WebDriver instance.
    :param by: The method used to locate the element (e.g. By.ID, By.CLASS_NAME, etc.).
    :param value: The value of the identifier used to locate the element.
    :param text: The text to wait for.
    :param timeout: The maximum amount of time to wait for the text to appear (in seconds).
    """
    WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element((by, value), text))
