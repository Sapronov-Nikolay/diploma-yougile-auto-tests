# tests/test_ui.py
"""
    UI-тесты для YouGile: авторизация и полный цикл создания объектов (проект → доска → колонка → задача).

    Структура:
        - TestLoginUI: тесты авторизации (успешный вход и неверный пароль).
        - TestCreationUI: тесты создания объектов на UI-слое.
          Для подготовки окружения часть объектов создаётся через API (чтобы ускорить тесты и не зависеть от UI-состояния),
          а финальный объект создаётся именно через UI — это и проверяется.
"""

import allure, pytest, random
from config import Config
from typing import Any, Generator
from src.ui.pages.login_page import LoginPage
from src.ui.pages.project_page import ProjectPage
from src.ui.pages.board_page import BoardPage
from src.ui.pages.column_page import ColumnPage
from src.ui.pages.task_page import TaskPage
from src.api.client import YouGileApiClient
from src.api.endpoints.projects import ProjectsEndpoint
from src.ui.locators import locators as ui_locators

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
    def test_login_success(self, driver):
        """Проверить, что пользователь успешно авторизуется с корректными логином и паролем."""
        login = LoginPage(driver)
        with allure.step("1. Открыть страницу логина"):
            login.open()
        with allure.step("2. Выполнить вход"):
            login.login(Config.LOGIN, Config.PASSWORD)
        with allure.step("3. Дождаться появления раздела 'Моя компания'"):
            assert login.is_mainpage()

    @allure.id("UI-02")
    @allure.story("Авторизация")
    @allure.feature("Неверный пароль")
    @allure.title("Авторизация с неверным паролем")
    @allure.description("Проверка отображения ошибки при неверном пароле")
    @pytest.mark.ui
    def test_login_wrong_password(self, driver):
        """Проверить, что при неверном пароле отображается сообщение об ошибке."""
        login = LoginPage(driver)

        with allure.step("1. Открыть страницу логина"):
            login.open()
        with allure.step("2. Ввести неверные данные"):
            login.login(Config.LOGIN, "wrong_password")
        with allure.step("3. Дождаться появления сообщения об ошибке"):
            assert login.is_errorpassword()

@allure.epic("UI")
@allure.severity(allure.severity_level.NORMAL)
class TestCreationUI:
    """Тесты создания объектов через UI-интерфейс."""

    @pytest.fixture(autouse=True)
    def setup_api(self, api_client: YouGileApiClient) -> Generator[None, Any, None]:
        """
            Фикстура для подготовки и очистки тестовых данных.
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
    def test_create_project(self, authorized_driver):
        project = ProjectPage(authorized_driver)
        with allure.step("1. Создать проект через UI"):
            name = f"{random.randint(1000,9999)}_Test_Project_UI"
            project.create_project(name)

    @allure.id("UI-04")
    @allure.story("Создание объектов")
    @allure.feature("Создание доски")
    @allure.title("Создание доски через UI")
    @allure.description("Проверка создания доски в проекте")
    @pytest.mark.ui
    def test_create_board(self, authorized_driver):
        with allure.step("1. Открыть любой существующий проект"):
            project = ProjectPage(authorized_driver)
            project.open_any_project()

        board = BoardPage(authorized_driver)
        with allure.step("2. Создать доску"):
            name = f"Board_{random.randint(100,999)}"
            board.create_board(name)
        with allure.step("3. Проверить наличие доски"):
            assert board.is_board_present(name)

    @allure.id("UI-05")
    @allure.story("Создание объектов")
    @allure.feature("Создание колонки")
    @allure.title("Создание колонки через UI")
    @allure.description("Проверка создания колонки на доске")
    @pytest.mark.ui
    def test_create_column(self, authorized_driver):
        with allure.step("1. Открыть любой существующий проект"):
            project = ProjectPage(authorized_driver)
            project.open_any_project()

        with allure.step("2. Создать доску"):
            board = BoardPage(authorized_driver)
            board_name = f"Board_{random.randint(100,999)}"
            board.create_board(board_name)

        with allure.step("3. Создать колонку"):
            column = ColumnPage(authorized_driver)
            column_name = f"Column_{random.randint(100,999)}"
            column.create_column(column_name)
        with allure.step("4. Проверить наличие колонки"):
            assert column.is_column_present(column_name)

    @allure.id("UI-06")
    @allure.story("Создание объектов")
    @allure.feature("Создание задачи")
    @allure.title("Создание задачи через UI")
    @allure.description("Проверка создания задачи в колонке")
    @pytest.mark.ui
    def test_create_task(self, authorized_driver):
        with allure.step("1. Открыть любой существующий проект"):
            project = ProjectPage(authorized_driver)
            project.open_any_project()

        with allure.step("2. Создать доску"):
            board = BoardPage(authorized_driver)
            board_name = f"Board_{random.randint(100,999)}"
            board.create_board(board_name)

        with allure.step("3. Создать колонку"):
            column = ColumnPage(authorized_driver)
            column_name = f"Column_{random.randint(100,999)}"
            column.create_column(column_name)

        with allure.step("4. Создать задачу"):
            task = TaskPage(authorized_driver)
            task_name = f"Task_{random.randint(100,999)}"
            task.create_task(task_name)
        with allure.step("5. Проверить наличие задачи"):
            assert task.is_task_present(task_name)

    @allure.id("UI-07")
    @allure.story("Удаление объектов")
    @allure.feature("Уборка тестовых данных")
    @allure.title("Удаление тестовых проектов через UI")
    @allure.description(
        "Уборка проектов с маской 'NNNN_Test_Project_UI' и 'NNNN_Auto_Project'. "
        "Если в компании остаётся только один проект — YouGile не даёт его удалить, "
        "это ограничение платформы, тест не падает."
    )
    @pytest.mark.ui
    def test_cleanup_test_projects(self, authorized_driver):
        project = ProjectPage(authorized_driver)

        with allure.step("1. Собрать список тестовых проектов"):
            test_names = project.collect_test_project_names()
            allure.attach(
                "\n".join(test_names) if test_names else "— пусто —",
                name="Найденные тестовые проекты",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("2. Удалить каждый проект по очереди"):
            for name in test_names:
                with allure.step(f"Удалить '{name}'"):
                    project.delete_project_by_name(name)
                    allure.attach(
                        f"Удалён: {name}",
                        name=f"Результат: {name}",
                        attachment_type=allure.attachment_type.TEXT,
                    )

        with allure.step("3. Финальная проверка"):
            remaining = project.collect_test_project_names()
            allure.attach(
                "\n".join(remaining) if remaining else "— всё удалено —",
                name="Остались тестовые проекты",
                attachment_type=allure.attachment_type.TEXT,
            )
