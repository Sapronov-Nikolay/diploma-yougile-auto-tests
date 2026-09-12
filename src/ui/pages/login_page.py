# src/ui/pages/login_page.py
"""
    Страница авторизации YouGile (UI-слой).

    Page Object для экрана входа в систему.
    Отвечает за открытие страницы логина и выполнение авторизации по email и паролю.

    Всё, что связано с локаторами (поля, кнопки), спрятано в словаре LOCATORS,
    а вся низкоуровневая логика (ожидания, клики, ввод) — в BasePage.
    Здесь остаётся только сценарий: «открыть → ввести логин → ввести пароль → нажать войти».
"""

import allure, time
from config import Config
from src.ui.base_page import BasePage
from src.ui.locators import locators
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

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
    @allure.step("Ввести логин {email} и пароль, нажать Войти")
    def login(self, email: str, password: str) -> None:
        self.find_element('поле_почты') # Ждём появления полей
        self.send_keys('поле_почты', email)
        self.send_keys('поле_пароля', password)
        self.click('кнопка_войти')

    def is_mainpage(self) -> bool:
        """Ждём появления 'Моя компания'. При потере контекста — ретрай."""
        for attempt in range(3):
            try:
                self.wait.until(
                    EC.presence_of_element_located(locators['заголовок_моя_компания'])
                )
                return True
            except WebDriverException as e:
                if 'no such execution context' in str(e) and attempt < 2:
                    # Перезагружаем страницу и пробуем снова
                    try:
                        self.driver.refresh()
                    except WebDriverException:
                        pass
                    time.sleep(2)
                    continue
                return False
        return False

    def is_errorpassword(self):
        return self.wait.until(
                lambda d: d.find_element(*locators['сообщение_ошибки'])
            ), "Ошибка входа не отобразилась"