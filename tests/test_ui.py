# tests/test_ui.py
"""
    UI-тесты для YouGile: авторизация и полный цикл создания объектов (проект → доска → колонка → задача).

    Структура:
        - TestLoginUI: тесты авторизации (успешный вход и неверный пароль).
        - TestCreationUI: тесты создания объектов на UI-слое.
          Для подготовки окружения часть объектов создаётся через API (чтобы ускорить тесты и не зависеть от UI-состояния),
          а финальный объект создаётся именно через UI — это и проверяется.
"""

import allure, pytest
from config import Config
from typing import Any, Generator
from src.ui.pages.login_page import LoginPage
from src.ui.pages.project_page import ProjectPage
from src.ui.pages.board_page import BoardPage
from src.ui.pages.column_page import ColumnPage
from src.ui.pages.task_page import TaskPage
from src.ui.locators import locators
from src.api.client import YouGileApiClient
from src.api.endpoints.projects import ProjectsEndpoint

@allure.epic("UI")
@allure.severity(allure.severity_level.CRITICAL)
class TestLoginUI:
    """Тесты для проверки авторизации пользователя в системе."""

    @allure.id("UI-01")
    @allure.story("Авторизация")
    @allure.feature("Успешный вход")
    @allure.title("Успешная авторизация")
    @allure.description("Проверка входа с валидными данными")
    @pytest.mark.ui
    def test_login_success(self, driver) -> None:
        """Проверить, что пользователь успешно авторизуется с корректными логином и паролем."""
        login = LoginPage(driver)

        with allure.step("1. Открыть страницу логина"):
            login.open()
        with allure.step("2. Выполнить вход"):
            login.login(Config.LOGIN, Config.PASSWORD)
        with allure.step("3. Дождаться появления раздела 'Моя компания'"):
            assert login.wait.until(
                lambda d: d.find_element(*locators['заголовок_моя_компания'])
            ), "Не удалось войти в систему"

    @allure.id("UI-02")
    @allure.story("Авторизация")
    @allure.feature("Неверный пароль")
    @allure.title("Авторизация с неверным паролем")
    @allure.description("Проверка отображения ошибки при неверном пароле")
    @pytest.mark.ui
    def test_login_wrong_password(self, driver) -> None:
        """Проверить, что при неверном пароле отображается сообщение об ошибке."""
        login = LoginPage(driver)

        with allure.step("1. Открыть страницу логина"):
            login.open()
        with allure.step("2. Ввести неверные данные"):
            login.login(Config.LOGIN, "wrong_password")
        with allure.step("3. Дождаться появления сообщения об ошибке"):
            assert login.wait.until(
                lambda d: d.find_element(*locators['сообщение_ошибки'])
            ), "Ошибка входа не отобразилась"

@allure.epic("UI")
@allure.severity(allure.severity_level.NORMAL)
class TestCreationUI:
    """Тесты создания объектов через UI-интерфейс."""

    @pytest.fixture(autouse=True)
    def setup_api(self, api_client: YouGileApiClient) -> Generator[None, Any, None]:
        """
            Фикстура для подготовки и очистки тестовых данных.

            Перед каждым тестом:
                - Инициализируем клиент API и endpoint для проектов.
                - Обнуляем ID созданного проекта.
        """
        self.api_client = api_client
        self.projects = ProjectsEndpoint(api_client)
        self.created_project_id = None
        yield

        if self.created_project_id:
            with allure.step("Очистка созданного проекта через API"):
                self.projects.soft_delete(self.created_project_id)

    @allure.id("UI-03")
    @allure.story("Создание объектов")
    @allure.feature("Создание проекта")
    @allure.title("Создание проекта через UI")
    @allure.description("Проверка полного цикла создания проекта")
    @pytest.mark.ui
    def test_create_project(self, authorized_driver) -> None:
        """Создать проект через UI и проверить, что он отображается в списке."""
        project = ProjectPage(authorized_driver)

        with allure.step("1. Создание проекта"):
            created_name = project.create_project("Test_Project_UI")
            # Получаем ID именно созданного проекта по его имени
            self.created_project_id = project.get_project_id_from_dom(created_name)

        with allure.step("2. Проверка наличия проекта"):
            assert project.is_project_present(created_name)

    @allure.id("UI-04")
    @allure.story("Создание объектов")
    @allure.feature("Создание доски")
    @allure.title("Создание доски через UI")
    @allure.description("Проверка создания доски в проекте")
    @pytest.mark.ui
    def test_create_board(self, authorized_driver) -> None:
        """Создать доску через UI и проверить её наличие."""
        with allure.step("1. Создание проекта через API"):
            project_resp = self.projects.create("Проект для доски")
            self.created_project_id = project_resp["id"]

        with allure.step("2. Переход в проект через UI"):
            project = ProjectPage(authorized_driver)
            project.select_project("Проект для доски")

        board = BoardPage(authorized_driver)
        with allure.step("3. Создание доски"):
            board.create_board("TestBoard")
        with allure.step("4. Проверка наличия доски"):
            assert board.is_board_present("TestBoard")

    @allure.id("UI-05")
    @allure.story("Создание объектов")
    @allure.feature("Создание колонки")
    @allure.title("Создание колонки через UI")
    @allure.description("Проверка создания колонки на доске")
    @pytest.mark.ui
    def test_create_column(self, authorized_driver) -> None:
        """Создать колонку через UI и убедиться, что она отображается."""
        with allure.step("1. Создание проекта и доски через API"):
            project_resp = self.projects.create("Проект для колонки")
            self.created_project_id = project_resp["id"]
            board_resp = self.api_client.post("/api-v2/boards", {
                "title": "Доска для колонки",
                "projectId": self.created_project_id
            }).json()

        with allure.step("2. Переход в проект и открытие доски через UI"):
            project = ProjectPage(authorized_driver)
            project.select_project("Проект для колонки")
            board = BoardPage(authorized_driver)
            board.open_board("Доска для колонки")

        column = ColumnPage(authorized_driver)
        with allure.step("3. Создание колонки"):
            column.create_column("Новые задачи")
        with allure.step("4. Проверка наличия колонки"):
            assert column.is_column_present("Новые задачи")

    @allure.id("UI-06")
    @allure.story("Создание объектов")
    @allure.feature("Создание задачи")
    @allure.title("Создание задачи через UI")
    @allure.description("Проверка создания задачи в колонке")
    @pytest.mark.ui
    def test_create_task(self, authorized_driver) -> None:
        """Создать задачу через UI и проверить её отображение."""
        with allure.step("1. Создание проекта, доски, колонки через API"):
            project_resp = self.projects.create("Проект для задачи")
            self.created_project_id = project_resp["id"]
            board_resp = self.api_client.post("/api-v2/boards", {
                "title": "Доска для задачи",
                "projectId": self.created_project_id
            }).json()
            self.api_client.post("/api-v2/columns", {
                "title": "Колонка для задачи",
                "boardId": board_resp["id"]
            }).json()

        with allure.step("2. Переход в проект и открытие доски через UI"):
            project = ProjectPage(authorized_driver)
            project.select_project("Проект для задачи")
            board = BoardPage(authorized_driver)
            board.open_board("Доска для задачи")

        task = TaskPage(authorized_driver)
        with allure.step("3. Создание задачи"):
            task.create_task("Тестовая задача")
        with allure.step("4. Проверка наличия задачи"):
            assert task.is_task_present("Тестовая задача")
