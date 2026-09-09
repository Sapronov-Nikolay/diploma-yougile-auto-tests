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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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

        # Если возникла ошибка дубликата ID — меняем имя так, чтобы изменились первые символы (ID‑префикс)
        if self.is_visible('ошибка_дубликата_id'):
            with allure.step("ID занят, генерируем уникальное имя"):
                # Вставляем случайное число в начало названия, чтобы ID стал другим
                unique_name = f"{random.randint(1000, 9999)}_{name}"
                name_field.clear()
                name_field.send_keys(unique_name)
                # Ждём, пока ошибка исчезнет (система примет новый ID)
                self.wait.until(lambda d: not self.is_visible('ошибка_дубликата_id'))
                name = unique_name

        with allure.step("4. Дождаться активации кнопки и кликнуть"):
            # Явное ожидание кликабельности защищает от ошибок, когда кнопка ещё не готова
            self.wait.until(lambda d: self.is_clickable('кнопка_добавить_проект_с_задачами'))
            self.click('кнопка_добавить_проект_с_задачами')

        with allure.step("5. Дождаться появления проекта в шапке"):
            self.wait.until(lambda d: name in d.find_element(*locators['название_проекта_в_шапке']).text)
        return name

    @allure.step("Открыть проект по ID: {project_id}")
    def open_by_id(self, project_id: str) -> None:
        """Перейти на страницу проекта напрямую по его ID."""
        from config import Config
        self.driver.get(f"{Config.BASE_URL}/team/projects/{project_id}")
        # Дожидаемся появления шапки проекта
        self.wait.until(lambda d: d.find_elements(*locators['название_проекта_в_шапке']))

    """
        Проверить, отображается ли проект с указанным названием в списке проектов (с ожиданием).
    """
    @allure.step("Проверить наличие проекта {name} в списке")
    def is_project_present(self, name: str) -> bool:
        try:
            self.wait.until(lambda d: any(name in elem.text for elem in d.find_elements(*locators['проект_в_списке'])))
            return True
        except:
            return False

    """
        Выбрать проект из списка, кликнув по его названию.
        Ищет по частичному вхождению (учитывает возможные суффиксы вроде "(2)").
    """
    @allure.step("Выбрать проект {name} (клик по карточке)")
    def select_project(self, name: str) -> None:
        # Ждём появления хотя бы одного проекта в списке
        self.wait.until(lambda d: len(d.find_elements(*locators['проект_в_списке_с_id'])) > 0)
        # Ищем проект по тексту и кликаем по родительскому элементу
        project_item = None
        for item in self.driver.find_elements(*locators['проект_в_списке_с_id']):
            title_elem = item.find_element(*locators['проект_в_списке'])
            if name in title_elem.text:
                project_item = item
                break
        if project_item is None:
            raise AssertionError(f"Проект '{name}' не найден в списке")
        project_item.click()
        # Ждём загрузки страницы проекта
        self.wait.until(lambda d: d.find_elements(*locators['кнопка_плюс_создать_доску']))

    """
        Извлечь ID проекта напрямую из атрибута data-itemid элемента в DOM.
    """
    @allure.step("Получить ID проекта из DOM по имени {name}")
    def get_project_id_from_dom(self, name: str) -> Optional[str]:
        for project in self.driver.find_elements(*locators['проект_в_списке_с_id']):
            if project.text.strip() == name:
                return project.get_attribute("data-itemid")
        return None

    @allure.step("Перейти на страницу проектов компании (/team/)")
    def go_to_company_projects(self) -> None:
        from config import Config
        self.driver.get(Config.BASE_URL + "/team/")
        self.wait.until(lambda d: d.find_elements(*locators['панель_проектов_компании']))

    @allure.step("Удалить проект по ID {project_id} (физически)")
    def delete_project_by_id(self, project_id: str) -> None:
        with allure.step("1. Находим карточку проекта на странице /team/"):
            card_selector = f"[data-testid='project-card'][data-itemid='{project_id}']"
            try:
                card = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, card_selector)))
            except:
            # Карточка не найдена — проект уже удалён, выходим
                return
        with allure.step("2. Открываем меню"):
            menu_btn = card.find_element(*locators['проект_карточка_меню'])
            menu_btn.click()
        with allure.step("3. Выбираем 'Удалить'"):
            delete_option = self.wait.until(EC.element_to_be_clickable(locators['пункт_меню_удалить_проект']))
            delete_option.click()
        with allure.step("4. Подтверждаем удаление"):
            confirm_btn = self.wait.until(EC.element_to_be_clickable(locators['кнопка_подтвердить_удаление_проекта']))
            confirm_btn.click()
        with allure.step("5. Ждём исчезновения карточки"):
            self.wait.until(EC.staleness_of(card))
