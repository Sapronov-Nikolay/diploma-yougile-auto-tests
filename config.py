# config.py
"""
    Модуль конфигурации для автотестов.
    Здесь хранятся все настройки проекта: URL, учётные данные, ID компании и т.д.
    Выжно: Чувствительные данные (логин, пароль, ключи) не хранятся в коде, а загружаются из файла .env.
    Это соответствует принципам безопасности и позволяет запускать тесты на разных окружениях без правки кода.
"""
import os       # Модуль для работы с ОС: пути, переменные окружения, создание папок
from dotenv import load_dotenv  # Библиотека для загрузки переменных из файла .env

"""
    Загружает переменные окружения из файла .env в текущей директории.
    Если файла нет или он не настроен, os.getenv вернёт None (или значение по умолчанию).
"""
load_dotenv()
class Config:
    BASE_URL = os.getenv("YOUGILE_URL", "https://ru.yougile.com")
    LOGIN = os.getenv("YOUGILE_LOGIN")
    PASSWORD = os.getenv("YOUGILE_PASSWORD")
    COMPANY_ID = os.getenv("YOUGILE_COMPANY_ID")
    CURRENT_KEY = os.getenv("YOUGILE_CURRENT_KEY")



    """
        Создаёт необхадимые дериктории для артефактов тестов, если их ещё нет.

        Зачем это нужно:
            - screen_url: сюда будут сохраняться скриншоты при падении UI-тестов.
            - allure-results: сюда Allure будет писать JSON-отчёты после каждого прогона.
            - os.makedirs(..., exist_ok=True) - безопасный способ создания папок:
            если папка уже есть, ошибки не возникнет и папка не будет пересоздаваться или создаваться новая.
    """
    @classmethod
    def ensure_dirs(cls):
        for d in ["screenshots", "allure-results"]:
            os.makedirs(d, exist_ok=True)
