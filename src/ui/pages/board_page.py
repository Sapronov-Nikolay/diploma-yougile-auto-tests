
# src/ui/pages/board_page.py
"""
    Страница досок YouGile (UI-слой).

    Этот Page Object реализует сценарии работы с досками: создание и проверку наличия.
    Мы не ждём смены URL, а ждём появления названия доски прямо в HTML-коде страницы
    не по «размазанному» тексту на странице, а по конкретным элементам-вкладкам.
    Мы ищем элементы с data-testid='board-tab' и сверяем их атрибут title с ожидаемым именем.
    Это важно, потому что в YouGile при создании доски URL может не меняться — обновление происходит динамически.

    Такой подход делает тест устойчивым к изменениям верстки: даже если текст доски
    переедет в другое место, но сама вкладка останется — тест продолжит работать.
"""

import allure
from selenium.webdriver.common.keys import Keys
from src.ui.base_page import BasePage
from src.ui.locators import locators

"""
    Page Object для страницы досок в YouGile.
    Реализует сценарии создания и проверки досок с учётом специфики SPA-интерфейса.
"""
class BoardPage(BasePage):

    """
        Создать новую доску с указанным названием.
        Сценарий соответствует реальному поведению пользователя в YouGile:
        1. Клик по кнопке «плюс» для открытия меню создания.
        2. Выбор пункта «Доска с задачами» из выпадающего меню.
        3. Ввод названия доски в поле ввода.
        4. Отправка формы нажатием Enter (вместо клика по кнопке «Сохранить»).
        5. Ожидание появления названия доски на странице через явное ожидание.
    """
    @allure.step("Создать доску через UI: название = {name}")
    def create_board(self, name: str) -> None:

        with allure.step("1. Открыть меню создания доски"):
            self.click('кнопка_плюс_создать_доску')

        with allure.step("2. Выбрать «Доска с задачами»"):
            self.click('пункт_меню_доска_с_задачами')

        with allure.step("3. Ввести название доски"):
            self.send_keys('поле_название_доски', name)
            field = self.find_element('поле_название_доски')
            field.send_keys(Keys.ENTER)

        with allure.step("4. Дождаться появления вкладки"):
            self.wait.until(
                lambda d: any(
                    name in tab.get_attribute("title")
                    for tab in d.find_elements(*locators['вкладка_доски'])
                    if tab.get_attribute("title")
                )
            )

    @allure.step("Открыть доску с названием {name}")
    def open_board(self, name: str) -> None:
        """Кликнуть по вкладке доски с указанным названием."""
        tabs = self.driver.find_elements(*locators['вкладка_доски'])
        for tab in tabs:
            if tab.get_attribute('title') == name:
                tab.click()
                return
        raise AssertionError(f"Доска с названием '{name}' не найдена")

    @allure.step("Проверить, что доска с названием '{name}' отображается на странице")
    def is_board_present(self, name: str) -> bool:
        """
            Проверка наличия доски по вкладке (data-testid='board-tab').
            Используем атрибут title, который всегда содержит название доски.
        """
        tabs = self.driver.find_elements(*locators['вкладка_доски'])
        return any(name in tab.get_attribute("title") for tab in tabs if tab.get_attribute("title"))
