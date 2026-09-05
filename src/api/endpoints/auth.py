# src/api/endpoints/auth.py
"""
    Модуль с методами для авторизации через API YouGile
    Здесь реализованы операции, которые требуют передачи логина и пароля
        - Получение списка компаний (чтобы достать CompanyId)
        - Создание нового API-ключа

    Важно: эти методы используют учётные данные пользователя. В реальных проектах
    их стараются вызывать как можно реже (например, только при настройке системы),
    а данные работают с временными токенами и ключами.
"""

import allure
from src.api.client import YouGileApiClient

class AuthEndpoint:
    """Инициализация AuthEndpoint."""
    def __init__(self, client: YouGileApiClient):
        self.client = client

    """Получение CompanyId по логину и паролю."""
    @allure.step("Получить CompanyId для пользователя {login} и {password}")
    def get_company_id(self, login: str, password: str) -> str:
        resp = self.client.post("/api-v2/auth/companies",{
            "login": login,
            "password": password,
        })
        resp.raise_for_status()

        data = resp.json()
        if not data:
            raise ValueError("API вернул пустой список компаний. Проверьте учётные данные")
        return data[0]["id"]

    """Создание и получить новый API-ключ для указанного companyId."""
    @allure.step("Создать API-ключ для компании {company_id}")
    def get_api_key(self, login: str, password: str, company_id: str) -> str:
        resp = self.client.post("/api-v2/auth/keys", {
            "login": login,
            "password": password,
            "companyId": company_id,
        })
        resp.raise_for_status()

        # Ответ API обычно выглядит так: {"key": "abc123..."}
        return resp.json()["key"]
