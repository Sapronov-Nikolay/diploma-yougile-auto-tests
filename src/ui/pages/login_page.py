# src/ui/pages/login_page.py
"""
    Страница авторизации YouGile (UI-слой).

    Page Object для экрана входа в систему.
    Отвечает за открытие страницы логина и выполнение авторизации по email и паролю.

    Всё, что связано с локаторами (поля, кнопки), спрятано в словаре LOCATORS,
    а вся низкоуровневая логика (ожидания, клики, ввод) — в BasePage.
    Здесь остаётся только сценарий: «открыть → ввести логин → ввести пароль → нажать войти».
"""

import allure
from config import Config
from src.ui.base_page import BasePage
from src.ui.locators import LOCATORS

"""Page Object для страницы авторизации YouGile."""
class LoginPage(BasePage):

    """
        Открыть стартовую страницу YouGile (экран авторизации).
        На главной странице есть кнопка "Войти", которая ведёт на /team/
    """
    @allure.step("Открыть страницу входа")
    def open(self) -> None:
        self.driver.get(Config.BASE_URL)
        self.click('кнопка_перейти_к_входу')

    """Выполнить вход в систему по email и паролю."""

    @allure.step("Выполнить вход")
    def login(self, email: str, password: str) -> None:
        self.find_element('поле_почты') # Ждём появления полей
        self.send_keys('поле_почты', email)
        self.send_keys('поле_пароля', password)
        self.click('кнопка_войти')
