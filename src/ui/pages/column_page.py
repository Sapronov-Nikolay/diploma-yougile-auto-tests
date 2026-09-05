# src/ui/pages/column_page.py
"""
    Страница колонок внутри доски YouGile (UI-слой).

    Page Object для работы с колонками: создание и проверка наличия.

    Ключевые особенности реализации:
        - Подтверждение создания колонки через нажатие Enter (как делает реальный пользователь).
        - Ожидание появления заголовка колонки на странице вместо проверки URL.
        - Поиск колонки по точному совпадению текста в заголовке.
"""

import allure
from selenium.webdriver.common.keys import Keys
from src.ui.base_page import BasePage
from src.ui.locators import locators

"""
   Page Object для работы с колонками на доске YouGile.

   Наследует базовую логику (клики, ввод, ожидания) из BasePage.
   Здесь описан сценарий создания колонки и проверки её отображения.
"""
class ColumnPage(BasePage):

    """Создать новую колонку на доске с заданным названием."""
    def create_column(self, name: str) -> None:
        with allure.step("1. Нажать «Создать колонку»"):
            self.click('кнопка_создать_колонку')

        with allure.step("2. Ввести название колонки"):
            self.send_keys('поле_название_колонки')
            field = self.find_element('поле_название_колонки')
            field.send_keys(Keys.ENTER)

        with allure.step('3. Дождаться появления заголовка'):
            self.wait.until(lambda d: any(
                name == header.text for header in d.find_elements(*locators['заголовок_колонки'])
            ))

    """Проверить, отображается ли колонка с указанным названием на доске."""
    @allure.step('Проверить, что колонка с названием {name} отображается')
    def is_column_present(self, name: str) -> bool:
        headers = self.driver.find_elements(*locators['заголовок_колонки'])
        return any(name == header.text for header in headers)
 в