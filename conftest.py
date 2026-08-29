# conftest.py
import pytest
from selenium import webdriver
from config import Config
from src.api.client import YouGileApiClient
from src.ui.pages.login_page import LoginPage

def pytest_configure(config):
    config.addinivalue_line("markers", "ui: UI-тесты")
    config.addinivalue_line("markers","api: API-тесты")

@pytest.fixture(scope="session")
def api_client():
    return YouGileApiClient()

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture
def authorized_driver(driver):
    """
        Возвращает драйвер с уже выполненным входом через UI.
        Это надёжный способ авторизации, так как YouGile использует SSO через Яндекс
        и HttpOnly куки, которые невозможно подделать через Selenium.
    """
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(Config.LOGIN, Config.PASSWORD)
    return driver
