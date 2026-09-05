# tests/test_api.py
"""
    Тесты API YouGile: авторизация и работа с проектами.

    Реализованы позитивные сценарии: получение CompanyId и API‑ключа,
    создание/получение/обновление/удаление проектов.

    Особенности:
        - Для очистки тестовых данных используется autouse‑фикстура с мягким удалением.
        - Все проверки сделаны через assert без дополнительных библиотек — это просто и понятно.
        - Allure‑метки (epic, story, feature, id и т.д.) помогают структурировать отчёт и быстро находить нужные тесты.
"""

import allure, pytest
from config import Config
from typing import Any, Generator
from src.api.client import YouGileApiClient
from src.api.endpoints.auth import AuthEndpoint
from src.api.endpoints.projects import ProjectsEndpoint
from conftest import ALL_CREATED_PROJECT_IDS

"""Тесты для проверки авторизации и получения ключей API."""
@allure.epic("API")
@allure.severity(allure.severity_level.NORMAL)
class TestAuthAPI:

    """Отправить запрос на получение списка компаний и проверить ответ."""
    @allure.id("API-01")
    @allure.story("Авторизация")
    @allure.feature("Получение CompanyId")
    @allure.title("Успешное получение CompanyId")
    @allure.description("проверка, что API возвращает ID компании")
    @pytest.mark.api
    def test_get_company_id(self, api_client: YouGileApiClient) -> None:
        with allure.step("1. Отправить POST /auth/companies"):
            resp = api_client.post("/api-v2/auth/companies", {
                "login": Config.LOGIN,
                "password": Config.PASSWORD
            })

        with allure.step("2. проверяем статус-код 200"):
            assert resp.status_code == 200

        with allure.step("3. Проверить наличие id вответе"):
            assert len(resp.json()) > 0
            assert "id" in resp.json()[0]

    """Запросить API‑ключ через вспомогательный endpoint и проверить его наличие."""
    @allure.id("API-02")
    @allure.story("Авторизация")
    @allure.feature("Получение API-ключа")
    @allure.title("Успешное получение API-ключа")
    @allure.description("Проверка создания ключа для компании")
    @pytest.mark.api
    def test_get_api_key(self, api_client: YouGileApiClient) -> None:
        auth = AuthEndpoint(api_client)

        with allure.step("1. Запросить API-ключ"):
            key = auth.get_api_key(Config.LOGIN, Config.PASSWORD, Config.COMPANY_ID)

        with allure.step("2. Проверить, что ключ не пустой"):
            assert key is not None
            assert len(key) > 0

"""Тесты CRUD‑операций над проектами через API."""
@allure.epic("API")
@allure.severity(allure.severity_level.NORMAL)
class TestProjectsAPI:

    """Фикстура для подготовки и очистки тестовых данных."""
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, api_client: YouGileApiClient) -> Generator[None, Any, None]:

        self.created_project_ids = []
        yield

        # После всех тестов удаляем созданные проекты через soft_delete.
        with allure.step("Очистка созданных тестами проектов через API"):
            projects = ProjectsEndpoint(api_client)
            for pid in self.created_project_ids:
                projects.soft_delete(pid)

    """Создать проект и проверить, что он успешно создан."""
    @allure.id("API-03")
    @allure.story("Проекты")
    @allure.feature("Создание")
    @allure.title("Создание проекта (позитивный)")
    @allure.description("Создание проекта с валидным названием")
    @pytest.mark.api
    def test_create_project(self, api_client: YouGileApiClient) -> None:
        projects = ProjectsEndpoint(api_client)

        with allure.step("1. Создать проект"):
            resp = projects.create("API_Test_Project")
            self.created_project_ids.append(resp["id"])
            ALL_CREATED_PROJECT_IDS.append(resp["id"])

        with allure.step("2. Проверить, что проект создан"):
            assert resp["id"] is not None
            assert resp["title"] == "API_Test_Project"

    """Создать проект, получить его по ID и проверить совпадение данных."""
    @allure.id("API-04")
    @allure.story("Проекты")
    @allure.feature("Получение")
    @allure.title("Получение проекта по ID")
    @allure.description("Проверка GET запроса на получение проекта")
    @pytest.mark.api
    def test_get_project(self, api_client: YouGileApiClient) -> None:
        projects = ProjectsEndpoint(api_client)

        with allure.step("1. Создать проект для проверки"):
            created = projects.create("API_Test_Project")
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Получить проект по ID"):
            acquire = projects.get(created["id"])

        with allure.step("3. Проверить совпадение данных"):
            assert acquire["id"] == created["id"]
            assert acquire["title"] == "API_Test_Project"

    """Обновить название проекта и убедиться, что изменение применилось."""
    @allure.id("API-05")
    @allure.story("Проекты")
    @allure.feature("Обновление")
    @allure.title("Обновление названия проекта")
    @allure.description("Проверка изменения title проекта")
    @pytest.mark.api
    def test_update_project(self, api_client: YouGileApiClient) -> None:
        projects = ProjectsEndpoint(api_client)

        with allure.step("1. Создать проект"):
            created = projects.create("Old_name_035")
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Обновить название проекта"):
            updated = projects.update(created["id"], title="New_name_036")

        with allure.step("3. проверить, что название изменилось"):
            assert updated["title"] == "New_name_036"

    """Удалить проект и проверить, что флаг deleted установлен в True."""
    @allure.id("API-06")
    @allure.story("Проекты")
    @allure.feature("Удаление")
    @allure.title("Мягкое удаление продукта")
    @allure.description("Проверка флага deleted=true")
    @pytest.mark.api
    def test_soft_delete_project(self, api_client: YouGileApiClient) -> None:
        projects = ProjectsEndpoint(api_client)

        with allure.step("1. Создать проект для удаления"):
            created = projects.create("API_Delete_Project")
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Мягко удалить проект"):
            resp = projects.soft_delete(created["id"])

        with allure.step("Проверить флаг deleted - deleted=true"):
            assert resp["deleted"] is True
