from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ChromeDriver:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def get_driver(self) -> webdriver.Chrome:
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
