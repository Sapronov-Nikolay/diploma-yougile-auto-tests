# src/ui/base_page.py
"""
    Базовый класс для всех Page Object в проекте.

    Его главная задача — убрать из тестов и конкретных страниц всю «рутину» Selenium:
    ожидания элементов, проверки видимости/кликабельности, очистку полей и т.д.

    Вместо низкоуровневых конструкций вроде:
        wait.until(EC.element_to_be_clickable(...)).click()
    в тестах и страницах будет просто:
        self.click('кнопка_создать')

    Это делает код чище, а тесты — понятнее. Если позже понадобится поменять таймаут
    или добавить логирование, то править нужно будет только этот файл, а не весь проект.
"""
import allure
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.ui.locators import LOCATORS

class BasePage:
    """Базовый класс-помощник для работы с UI-элементами"""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def find_element(self, locator_key):
        return self.wait.until(EC.visibility_of_element_located(LOCATORS[locator_key]))

    @allure.step("Кликнуть по элементу: {locator_key}")
    def click(self, locator_key):
        self.wait.until(EC.element_to_be_clickable(LOCATORS[locator_key])).click()

    @allure.step("Ввести текст в поле: {locator_key}")
    def send_keys(self, locator_key, text):
        elem = self.find_element(locator_key)
        elem.clear()
        elem.send_keys(text)

    @allure.step("Проверить видимость элемента: {locator_key}")
    def is_visible(self,locator_key):
        try:
            return self.find_element(locator_key).is_displayed()
        except:
            return False

    @allure.step("Проверить кликабельность элемента: {locator_key}")
    def is_clickable(self,locator_key) -> bool:
        try:
            self.wait.until(EC.element_to_be_clickable(LOCATORS[locator_key]))
            return True
        except:
            return False
