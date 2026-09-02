# src/api/client.py
"""
    Базовый API-клиент для YouGile.
    Главная фишка этого класса: он сам заботится об авторизации.
    Не нужно вручную получать токен перед каждым запросом — клиент сделает это
    автоматически при первом вызове (и запомнит токен на всё время работы теста).

    Это сильно упрощает тесты: пишешь projects.create(...), а клиент сам решает,
    надо ли сначала получить токен, и подставляет его в заголовки.
"""

import requests
from config import Config

"""Класс для взаимодействия с API YouGile."""
class YouGileApiClient:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.login = Config.LOGIN
        self.password = Config.PASSWORD
        self.company_id = Config.COMPANY_ID
        self._token = None  # Сейчас его нет, но позже он будет получен при первом запросе.

    """Гарантирует, что у клиента есть валидный токен."""
    def _ensure_auth(self):
        # Если CompanyId не задан в .env, получаем его автоматически
        if self._token is None:
            if not self.company_id:
                resp = requests.post(
                    f"{self.base_url}/api-v2/auth/companies",
                    json={
                        "login": self.login,
                        "password": self.password
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                if not data:
                    raise ValueError("API вернул пустой список компаний. Проверьте логин/пароль.")
                self.company_id = data[0]["id"]

            # Приоритет: если в .env есть CURRENT_KEY, используем его.
            if Config.CURRENT_KEY:
                self._token = Config.CURRENT_KEY
            else:
                # Если токена нет — запрашиваем новый ключ через логин/пароль
                resp = requests.post(
                    f"{self.base_url}/api-v2/auth/keys",
                    json={
                        "login": self.login,
                        "password": self.password,
                        "company_id": self.company_id
                    }
                )
                resp.raise_for_status()
                self._token = resp.json()["key"]
        return self._token

    """Формирует заголовки для фвторизованного запроса."""
    def _headers(self):
        return {
            "content-Type": "application/json",
            "Authorization": f"Bearer {self._ensure_auth()}"
        }

    """Выполнить POST-запрос к API."""
    def post(self, endpoint, payload):
        return requests.post(f"{self.base_url}{endpoint}", json=payload, headers=self._headers())

    """Выполнить GET-запрос."""
    def get(self, endpoint):
        return requests.get(f"{self.base_url}{endpoint}", headers=self._headers())

    """Выполнить PUT-запрос (обычно для обновления ресурсов)."""
    def put(self, endpoint, payload):
        return requests.put(f"{self.base_url}{endpoint}", json=payload, headers=self._headers())

    """Выполнить DELETE-запрос (обычно для удаления ресурсов)."""
    def delete(self, endpoint):
        return requests.delete(f"{self.base_url}{endpoint}", headers=self._headers())
