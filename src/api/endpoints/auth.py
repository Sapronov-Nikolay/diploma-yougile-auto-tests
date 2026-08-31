# src/api/endpoints/auth.py
"""
    Модуль с методами для авторизации через API YouGile
    Здесь реализованы операции, которые требуют передачи логина и пароля
        - Получение списка компаний (чтобы доставть CompanyId)
        - Создание нового API-ключа

    Важно: эти методы используют учётные данные пользователя. В реальных проектах
    их стараются вызывать как можно реже (например, только при настройке системы),
    а данные работают с временными токенами и ключами
"""

from src.api.client import YouGileApiClient

class AuthEndpoint:
    """Инициализация AuthEndpoint."""
    def __init__(self, client: YouGileApiClient):
        self.client = client

    """Получение CompanyId по логину и паролю."""
    def get_company_id(self, login, password):
        resp = self.client.post("/api-v2/auth/companies",{
            "login": login,
            "password": password,
        })
        resp.raise_for_status()

        data = resp.json()
        if not data:
            raise ValueError("API вернул пустой список компаний. Проверьте учётные данные")
        return data[0]["id"]

    """Создание и получить новый API-ключ для указанного company_id."""
    def get_api_key(self, login, password, company_id):
        resp = self.client.post("/api-v2/auth/keys", {
            "login": login,
            "password": password,
            "company_id": company_id,
        })
        resp.raise_for_status()

        # Ответ API обычно выглядит так: {"key": "abc123..."}
        return resp.json()["key"]
