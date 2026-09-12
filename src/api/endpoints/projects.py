# src/api/endpoints/projects.py
"""
    Модуль с методами для работы с проектами через API YouGile.
    Это 'слой абстракции' над сырыми HTTP-запросами: вместо того чтобы в каждом тесте
    писать self.client.post("/api-v2/projects", {...}), мы вызываем понятный метод:
        projects.create("Мой проект", users={...})

    Такой подход делает тесты читаемыми, а логику работы с API — централизованной.
    Если API изменится (например, поменяется URL или формат полей), мы правим код
    только в этом файле, а не в десятках тестов.

    Класс ProjectsEndpoint реализует CRUD-операции для проектов в YouGile (Create, Read, Update, Deleted).
    Все методы работают через клиент YouGileApiClient и возвращают JSON-ответы API.
    Важная особенность — метод update отправляет только те поля, которые реально изменились, что снижает риск побочных эффектов.
    Метод soft_delete — удобная обёртка над update(..., deleted=True):
        он делает код тестов чище и отражает бизнес-логику YouGile (мягкое удаление вместо жёсткого).
    Такой подход соответствует принципам чистого кода и упрощает поддержку автотестов.
"""

import allure
from typing import Any, Dict, Optional
from src.api.client import YouGileApiClient

"""Класс обёртка для операций с проектами"""
class ProjectsEndpoint:
    def __init__(self, client: YouGileApiClient):
        self.client = client

    """Создать новый проект в YouGile."""
    @allure.step("Создать проект с названием {title}")
    def create(self, title: str, users: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"title": title}
        if users:
            payload["users"] = users
        resp = self.client.post("/api-v2/projects", payload)
        resp.raise_for_status()
        return resp.json()

    """Получить данные проекта по его ID."""
    @allure.step("Получить проект с ID {project_id}")
    def get(self, project_id: str) -> Dict[str, Any]:
        resp = self.client.get(f"/api-v2/projects/{project_id}")
        resp.raise_for_status()
        return resp.json()

    """Обновить проект: поменять название и/или пометить как удалённый."""
    @allure.step("Обновить проект {project_id}")
    def update(self, project_id: str, title: Optional[str] = None, deleted: Optional[bool] = None) -> Dict[str, Any]:
        payload = {}
        if title is not None:
            payload["title"] = title
        if deleted is not None:
            payload["deleted"] = deleted
        resp = self.client.put(f"/api-v2/projects/{project_id}", payload)
        resp.raise_for_status()
        return resp.json()

    """Мягко удалить проект (пометить как deleted=True)"""
    @allure.step("Мягко удалить проект {project_id}")
    def soft_delete(self, project_id: str) -> Dict[str, Any]:
        return self.update(project_id, deleted=True)
