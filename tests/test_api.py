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

import allure, pytest, random
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
    @allure.description("Проверка, что API возвращает ID компании")
    @pytest.mark.api
    def test_get_company_id(self, api_client: YouGileApiClient) -> None:
        with allure.step("1. Отправить POST /auth/companies"):
            resp = api_client.post("/api-v2/auth/companies", {
                "login": Config.LOGIN,
                "password": Config.PASSWORD
            })

        with allure.step("2. Проверить статус-код 200"):
            assert resp.status_code == 200

        with allure.step("3. Проверить наличие id в ответе"):
            data = resp.json()
            # API может вернуть список или объект с полем content
            if isinstance(data, dict):
                # Если это словарь, ищем список в 'content' или 'data'
                companies = data.get("content") or data.get("data") or []
            else:
                companies = data

            assert len(companies) > 0, "В ответе нет компаний"
            assert "id" in companies[0], "Компания не содержит id"

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

        with allure.step("1. Создать проект с уникальным именем"):
            unique_name = f"{random.randint(1000,9999)}_API_Test_Project"
            resp = projects.create(unique_name)
            # Сохраняем ID для очистки
            self.created_project_ids.append(resp["id"])
            ALL_CREATED_PROJECT_IDS.append(resp["id"])

        with allure.step("2. Проверить, что проект создан (проверяем наличие id)"):
            assert resp["id"] is not None, "API не вернул id проекта"

        with allure.step("3. Получить проект по ID и проверить название"):
            # API при создании возвращает только id, поэтому название проверяем через GET
            got = projects.get(resp["id"])
            assert got["title"] == unique_name

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
            unique_name = f"{random.randint(1000,9999)}_API_Test_Project"
            created = projects.create(unique_name)
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Получить проект по ID"):
            acquire = projects.get(created["id"])

        with allure.step("3. Проверить совпадение данных"):
            assert acquire["id"] == created["id"]
            assert acquire["title"] == unique_name

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
            unique_name = f"{random.randint(1000,9999)}_Old_name"
            created = projects.create(unique_name)
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Обновить название проекта"):
            new_name = f"{random.randint(1000,9999)}_New_name"
            # API при обновлении возвращает только id, поэтому проверяем через GET
            updated = projects.update(created["id"], title=new_name)
            assert updated["id"] == created["id"]

        with allure.step("3. Проверить, что название изменилось (через GET)"):
            got = projects.get(created["id"])
            assert got["title"] == new_name

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
            unique_name = f"{random.randint(1000,9999)}_API_Delete_Project"
            created = projects.create(unique_name)
            self.created_project_ids.append(created["id"])
            ALL_CREATED_PROJECT_IDS.append(created["id"])

        with allure.step("2. Мягко удалить проект"):
            resp = projects.soft_delete(created["id"])
            assert resp["id"] == created["id"], "API вернул неверный id при удалении"

        with allure.step("3. Проверить флаг deleted через GET"):
            got = projects.get(created["id"])
            assert got["deleted"] is True
