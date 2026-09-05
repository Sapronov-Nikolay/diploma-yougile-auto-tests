# src/ui/pages/project_page.py
"""
    Страница проектов в YouGile (UI-слой).

    Page Object для работы с проектами: создание, выбор, проверка наличия и получения ID.

    Ключевые особенности реализации:
        - Обработка ситуации с дублированием названия: если система показывает ошибку,
        автоматически генерируется уникальное имя с рондомным суфиксом.
        - Использование явных ожиданий (wait.untill) вместо жёстких пауз.
        - Детальная разбивка действий на детальные шаги дляпонятных отчётов Allure.
        - Получение ID проекта из атрибута data-itemid в DOM — это надёжнее, чем парсить URL,
        и не зависит от формата адресной строки.
"""

from typing import Optional
import random, allure
from src.ui.base_page import BasePage
from src.ui.locators import locators

class ProjectPage(BasePage):

    """
        Создать новый проект в YouGile с заданным именем.

        Сценарий учитывает реальную ситуацию: если имя уже занято, автоматически подставляется уникальный суффикс.
        Возвращает фактическое название проекта (может быть изменено при дубликате ID).
        Это делает тест устойчивым к повторным запускам на одном и том же стенде.
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
                # Генерируем случайный суффикс 1000–9999, чтобы снизить риск коллизий
                unique_name = f"{name}_{random.randint(1000, 9999)}"
                name_field.clear()
                name_field.send_keys(unique_name)
                # Ждём, пока ошибка исчезнет - значит, имя стало уникальным
                self.wait.until(lambda d: not self.is_visible('ошибка_дубликата_id'))
                # Обновляем переменную name, чтобы дальше проверять именно это имя
                name = unique_name

        with allure.step("5. Проверить, что кнопка активна и кликнуть"):
            # Явное ожидание кликабельности защищает от ошибок, когда кнопка ещё не готова из-за валидации.
            self.wait.until(lambda d: self.is_clickable('кнопка_добавить_проект_с_задачами'))
            self.click('кнопка_добавить_проект_с_задачами')

        with allure.step("6. Дождаться появления проекта в шапке"):
            # Ищем элемент с названием проекта и проверяем его текст.
            # *locators[...] распаковывает кортеж (By, selector) в два аргумента.
            self.wait.until(lambda d: name in d.find_element(*locators['название_проекта_в_шапке']).text)
        return name  # Возвращаем фактическое имя

    """
        Проверить, отображается ли проект с указанным названием в списке проектов.

        Логика:
        1. Находим все элементы списка проектов по локатору.
        2. Проверяем, есть ли среди их текстов искомое название.
    """
    @allure.step("Проверить наличие проекта {name}")
    def is_project_present(self, name: str) -> bool:
        return any(name in elem.text for elem in self.driver.find_elements(*locators['проект_в_списке']))

    """
        Выбрать проект из списка, кликнув по его названию.

        Извлекает ID проекта напрямую из атрибута data-itemid элемента в DOM.
        Ищет именно элемент с указанным названием, чтобы не зацепить чужие проекты.
    """
    @allure.step("Выбрать проект {name}")
    def select_project(self, name: str) -> None:
        project = self.wait.until(lambda d: next(
            (elem for elem in d.find_elements(*locators['проект_в_списке']) if elem.text == name),None))

        project.click()
        self.wait.until(lambda d: d.find_elements(*locators['кнопка_плюс_создать_доску']))

    """
        Извлечь ID проекта напрямую из атрибута data-itemid элемента в DOM.

        Извлекает ID проекта напрямую из атрибута data-itemid элемента в DOM.
        Ищет именно элемент с указанным названием, чтобы не зацепить чужие проекты.
    """
    @allure.step("Получить ID проекта из DOM по имени {name}")
    def get_project_id_from_dom(self, name: str) -> Optional[str]:
        projects = self.driver.find_elements(*locators['проект_в_списке_с_id'])
        for project in projects:
            if project.text.strip() == name:
                return project.get_attribute("data-itemid")
        return None
