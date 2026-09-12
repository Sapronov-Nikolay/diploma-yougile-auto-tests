# src/ui/pages/project_page.py
"""
    Страница проектов в YouGile (UI-слой).

    Page Object для работы с проектами: создание, выбор, проверка наличия и получения ID.
    Также работа с архивом проектов (открытие архива и удаление проектов по ID).
    Особенности реализации физического удаления:
        Удаляет архивированные проекты, чьи ID совпадают с переданными в список.
"""

from typing import Optional
import random, allure, re

from selenium.webdriver.support.wait import WebDriverWait
from config import Config
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
            self.click('карточка_добавить_проект')

        with allure.step("2. Выбрать тип «Проект с задачами»"):
            self.click('пункт_меню_проект_с_задачами')

        name_field = self.find_element('поле_название_проекта')
        with allure.step("3. Ввести название {name}"):
            name_field.clear()
            name_field.send_keys(name)

        if self.is_visible('ошибка_дубликата_id'):
            with allure.step("ID занят, генерируем уникальное имя"):
                unique_name = f"{random.randint(1000, 9999)}_{name}"
                name_field.clear()
                name_field.send_keys(unique_name)
                self.wait.until(lambda d: not self.is_visible('ошибка_дубликата_id'))
                name = unique_name

        with allure.step("4. Дождаться активации кнопки и кликнуть"):
            self.wait.until(lambda d: self.is_clickable('кнопка_добавить_проект_с_задачами'))
            self.click('кнопка_добавить_проект_с_задачами')

        with allure.step("5. Дождаться появления кнопки добавления доски"):
            self.wait.until(EC.presence_of_element_located(locators['кнопка_плюс_создать_доску']))
        return name

    @allure.step("Открыть любой существующий проект (клик по первой карточке)")
    def open_any_project(self) -> None:
        cards = self.driver.find_elements(*locators['проект_карточка'])
        if not cards:
            # Карточек нет — создаём проект через большую кнопку
            self.create_project(f"{random.randint(1000, 9999)}_Auto_Project")
            return
        cards[0].click()
        self.wait.until(EC.presence_of_element_located(locators['кнопка_плюс_создать_доску']))

    @allure.step("Открыть проект по ID: {project_id}")
    def open_by_id(self, project_id: str) -> None:
        self.driver.get(f"{Config.BASE_URL}/team/projects/{project_id}")
        # Ждём, пока загрузится страница проекта – по кнопке создания доски
        self.wait.until(
            EC.presence_of_element_located(locators['кнопка_плюс_создать_доску'])
        )

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
        # Ждём появления карточек проектов
        self.wait.until(EC.presence_of_element_located(locators['проект_карточка']))
        # Ищем карточку по названию и кликаем
        for card in self.driver.find_elements(*locators['проект_карточка']):
            title_elem = card.find_element(*locators['проект_карточка_название'])
            if name in title_elem.text:
                card.click()
                # Ждём загрузки проекта – по кнопке добавления доски
                self.wait.until(EC.presence_of_element_located(locators['кнопка_плюс_создать_доску']))
                return
        raise AssertionError(f"Проект '{name}' не найден")

    """
        Извлечь ID проекта напрямую из атрибута data-itemid элемента в DOM.
    """
    @allure.step("Получить ID проекта из DOM по имени {name}")
    def get_project_id_from_dom(self, name: str) -> Optional[str]:
        projects = self.driver.find_elements(*locators['проект_карточка'])
        for project in projects:
            title_elem = project.find_element(*locators['проект_карточка_название'])
            if title_elem.text.strip() == name:
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

    # ---------- Уборка тестовых проектов (для UI-07) ----------

    @allure.step("Собрать имена тестовых проектов на странице /team/")
    def collect_test_project_names(self) -> list:
        # Без driver.get — работаем на текущей странице.
        # Ждём панели и карточек, которые уже есть в DOM.
        self.wait.until(
            EC.presence_of_element_located(locators['панель_проектов_компании'])
        )
        try:
            self.wait.until(
                lambda d: d.find_elements(*locators['проект_карточка'])
            )
        except Exception:
            return []

        pattern = re.compile(r"^\d{4}_(Test_Project_UI|Auto_Project)$")
        names = []
        for card in self.driver.find_elements(*locators['проект_карточка']):
            try:
                title = card.find_element(*locators['проект_карточка_название']).text.strip()
            except Exception:
                continue
            if pattern.match(title):
                names.append(title)
        return names

    @allure.step("Удалить проект через UI: {name}")
    def delete_project_by_name(self, name: str) -> None:
        target = name.strip()

        with allure.step("1. Найти карточку проекта"):
            def _find(d):
                for c in d.find_elements(*locators['проект_карточка']):
                    try:
                        title = c.find_element(*locators['проект_карточка_название']).text.strip()
                    except Exception:
                        continue
                    if title == target:
                        return c
                return False
            card = self.wait.until(_find)

        with allure.step("2. Открыть меню (три точки)"):
            card.find_element(*locators['проект_карточка_меню']).click()

        with allure.step("3. Кликнуть «Удалить» в меню"):
            self.click('пункт_меню_удалить_проект')

        with allure.step("4. Дождаться модалки «Удалить проект?»"):
            self.wait.until(
                EC.visibility_of_element_located(locators['заголовок_модалки_удаления_проекта'])
            )

        with allure.step("5. Кликнуть «Удалить» в модалке"):
            self.click('кнопка_подтвердить_удаление_проекта')

        with allure.step("6. Дождаться закрытия модалки"):
            self.wait.until(
                EC.invisibility_of_element_located(locators['заголовок_модалки_удаления_проекта'])
            )

        with allure.step(f"7. Дождаться исчезновения карточки '{target}' из DOM"):
            def _gone(d):
                for c in d.find_elements(*locators['проект_карточка']):
                    try:
                        title = c.find_element(*locators['проект_карточка_название']).text.strip()
                    except Exception:
                        continue
                    if title == target:
                        return False
                return True
            self.wait.until(_gone)
