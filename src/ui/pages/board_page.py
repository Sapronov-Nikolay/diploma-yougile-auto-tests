# src/ui/pages/board_page.py
"""
    Страница досок YouGile (UI-слой).
    Page Object для работы с досками: создание и проверка наличия.
"""
import allure
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from src.ui.base_page import BasePage
from src.ui.locators import locators

class BoardPage(BasePage):

    @allure.step("Создать доску через UI: название = {name}")
    def create_board(self, name: str) -> None:
        with allure.step("1. Открыть меню создания доски"):
            self.click('кнопка_плюс_создать_доску')

        with allure.step("2. Выбрать «Доска с задачами»"):
            self.click('пункт_меню_доска_с_задачами')

        with allure.step("3. Ввести название доски"):
            # Ожидаем появления поля ввода
            field = self.wait.until(EC.visibility_of_element_located(locators['поле_название_доски']))
            field.clear()
            field.send_keys(name)
            field.send_keys(Keys.ENTER)

        with allure.step("4. Дождаться появления вкладки доски"):
            self.wait.until(
                lambda d: any(
                    name in tab.get_attribute("title")
                    for tab in d.find_elements(*locators['вкладка_доски'])
                    if tab.get_attribute("title")
                )
            )

    @allure.step("Открыть доску с названием {name}")
    def open_board(self, name: str) -> None:
        tabs = self.driver.find_elements(*locators['вкладка_доски'])
        for tab in tabs:
            if tab.get_attribute('title') == name:
                tab.click()
                return
        raise AssertionError(f"Доска с названием '{name}' не найдена")

    @allure.step("Проверить, что доска с названием '{name}' отображается")
    def is_board_present(self, name: str) -> bool:
        tabs = self.driver.find_elements(*locators['вкладка_доски'])
        return any(name in tab.get_attribute("title") for tab in tabs if tab.get_attribute("title"))
