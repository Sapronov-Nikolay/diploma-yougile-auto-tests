# src/ui/pages/project_page.py
"""
    Страница проектов в YouGile (UI-слой).

    Page Object для работы с проектами: создание, выбор, проверка наличия и получения ID.
    Также работа с архивом проектов (открытие архива и удаление проектов по ID).
    Особенности реализации физического удаления:
        Удаляет архивированные проекты, чьи ID совпадают с переданными в список.
"""

from typing import Optional, List
import random, allure
from src.ui.base_page import BasePage
from src.ui.locators import locators

class ProjectPage(BasePage):

    """
        Создать новый проект в YouGile с заданным именем.

        Сценарий учитывает реальную ситуацию: если имя уже занято, автоматически подставляется уникальный суффикс.
        Возвращает фактическое название проекта (может быть изменено при дубликате ID).
    """
    @allure.step("Создать проект через UI: название = {name}")
    def create_project(self, name: str) -> str:
        with allure.step("1. Открыть модальное окно проекта"):
            self.click('кнопка_добавить_проект_в_меню')

        with allure.step("2. Выбрать тип «Проект с задачами»"):
            self.click('пункт_меню_проект_с_задачами')

        name_field = self.find_element('поле_название_проекта')
        with allure.step("3. Ввести название {name}"):
            name_field.clear()
            name_field.send_keys(name)

        if self.is_visible('ошибка_дубликата_id'):
            with allure.step("4. Генерируем уникальное имя (ID занят)"):
                unique_name = f"{name}_{random.randint(1000, 9999)}"
                name_field.clear()
                name_field.send_keys(unique_name)
                self.wait.until(lambda d: not self.is_visible('ошибка_дубликата_id'))
                name = unique_name

        with allure.step("5. Проверить, что кнопка активна и кликнуть"):
            self.wait.until(lambda d: self.is_clickable('кнопка_добавить_проект_с_задачами'))
            self.click('кнопка_добавить_проект_с_задачами')

        with allure.step("6. Дождаться появления проекта в шапке"):
            self.wait.until(lambda d: name in d.find_element(*locators['название_проекта_в_шапке']).text)
        return name

    """
        Проверить, отображается ли проект с указанным названием в списке проектов (с ожиданием).
    """
    @allure.step("Проверить наличие проекта {name}")
    def is_project_present(self, name: str) -> bool:
        try:
            self.wait.until(lambda d: any(name in elem.text for elem in d.find_elements(*locators['проект_в_списке'])))
            return True
        except:
            return False

    """
        Выбрать проект из списка, кликнув по его названию.
    """
    @allure.step("Выбрать проект {name}")
    def select_project(self, name: str) -> None:
        project = self.wait.until(lambda d: next(
            (elem for elem in d.find_elements(*locators['проект_в_списке']) if elem.text == name), None
        ))
        project.click()
        self.wait.until(lambda d: d.find_elements(*locators['кнопка_плюс_создать_доску']))

    """
        Извлечь ID проекта напрямую из атрибута data-itemid элемента в DOM.
    """
    @allure.step("Получить ID проекта из DOM по имени {name}")
    def get_project_id_from_dom(self, name: str) -> Optional[str]:
        projects = self.driver.find_elements(*locators['проект_в_списке_с_id'])
        for project in projects:
            if project.text.strip() == name:
                return project.get_attribute("data-itemid")
        return None

    @allure.step("Открыть блок «Архивированные проекты»")
    def open_archive(self) -> None:
        archive_header = self.driver.find_element(*locators['архивный_заголовок'])
        archive_header.click()
        self.wait.until(lambda d: d.find_elements(*locators['проект_в_архиве']))

    @allure.step("Удалить архивированные проекты по ID {project_ids}")
    def delete_archived_projects_by_ids(self, project_ids: List[str]) -> None:
        cards = self.driver.find_elements(*locators['проект_в_архиве'])
        for card in cards:
            card_id = card.get_attribute("data-itemid")
            if card_id in project_ids:
                menu = card.find_element(*locators['проект_три_точки'])
                menu.click()
                delete_option = self.driver.find_element(*locators['пункт_меню_удалить'])
                delete_option.click()
                confirm = self.driver.find_element(*locators['кнопка_подтвердить_удаление'])
                confirm.click()
                self.wait.until(lambda d: card not in d.find_elements(*locators['проект_в_архиве']))
