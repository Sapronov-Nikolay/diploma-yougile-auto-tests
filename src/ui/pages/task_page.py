# src/ui/pages/task_page.py
"""
    Страница задач на доске YouGile (UI-слой).

    Page Object для работы с задачами: создание и проверка наличия.

    Ключевые особенности реализации:
        - Создание задачи через ввод названия и подтверждение клавишей Enter — имитирует поведение реального пользователя.
        - Ожидание появления заголовка задачи через явное условие (wait.until), без жёстких пауз.
        - Проверка наличия задачи по точному совпадению текста — исключает ложные срабатывания,
        если одно название входит в другое.
"""

import allure
from selenium.webdriver.common.keys import Keys
from src.ui.base_page import BasePage
from src.ui.locators import locators

"""
    Page Object для страницы задач на доске YouGile.

    Наследует базовую логику взаимодействия (клики, ввод, ожидания) из BasePage.
    Здесь реализована бизнес-логика: создание задачи и проверка её отображения.
"""
class TaskPage(BasePage):

    """Создать новую задачу на доске с заданным названием."""
    @allure.step("Создать задачу через UI: название = {name}")
    def create_task(self, name: str) -> None:
        with allure.step("1. Нажать «Добавить задачу»"):
            self.click('кнопка_добавить_задачу')

        with allure.step("2. Ввести название задачи"):
            self.send_keys('поле_название_задачи', name)
            field = self.find_element('поле_название_задачи')
            field.send_keys(Keys.ENTER)

        with allure.step("2. Дождаться появления заголовка задачи"):
            self.wait.until(lambda d: any(
                name == title.text for title in d.find_elements(*locators['заголовок_задачи'])
            ))

    """Проверить, отображается ли задача с указанным названием на доске"""
    @allure.step("Проверить, что задача с названием '{name}' отображается")
    def is_task_present(self, name: str) -> bool:
        titles = self.driver.find_elemetns(*locators['заголовок_задачи'])
        return any(name == title.text for title in titles)
