# conftest.py
"""
    Центральный файл для pytest.
        Здесь определяются:
        - маркеры (теги) для группировки тестов (ui/api);
        - фикстуры (ресурсы), которые переиспользуются во всех тестах;
        - логика подготовки и очистки окружения.

    Это специальный файл для pytest: в нём определяют фикстуры (fixtures) и настраивает поведение тестов.
    pytest автоматически подхватывает этот файл, если он лежит в корне тестовой директории.
"""

import pytest
from selenium import webdriver
from config import Config
from src.api.client import YouGileApiClient
from src.ui.pages.login_page import LoginPage

"""
    Эта функция вызывается pytest при старте сессии.
    Она нужна, чтобы зарегистрировать кастомные маркеры - метки для группировки тестов.
    
    Здесь мы добавляем два маркера:
        - "ui": чтобы помечать UI-тесты (тесты через браузер)
        - "api": чтобы помечать API-тесты (тесты запросов к серверу)
    
    Пример использования тестов:
        @pytest.mark.ui
        def test_some_ui_feature(): ...
        
    Потом можно запускать только нужные тесты, например:
        `pytest -m ui` или `pytest -m api`
"""
def pytest_configure(config):
    config.addinivalue_line("markers", "ui: UI-тесты")
    config.addinivalue_line("markers","api: API-тесты")

"""
    Фикстура для создания экземпляра API-клиента.
    scope="session" означает, объект создаётся один раз на всю тестовую сессию.
    Это полезно, если создание API-клиента дорогое (например, требует системных вызовов),
    
    Возвращает: экземпляр YouGileApiClient, который можно использовать в тестах.
"""
@pytest.fixture(scope="session")
def api_client():
    """
        Пример использования:
        def setup_and_teardown(self, api_client: YouGileApiClient) -> None:
        ... ...
            projects = ProjectsEndpoint(api_client)
            for pid in self.created_project_ids:
                projects.soft_delete(pid)
    """
    return YouGileApiClient()

"""
    Фикстура, которая создаёт и возвращает экземпляр драйвера браузера (chrome).
    По умолчанию фикстуры имеют scope="function", то есть создаются заново для каждого теста.
    
    Логика работы:
        1. Создаём драйвер: webdriver.Chrome()
        2. Разворачиваем окно браузера на весь экран: maxmize_window()
        3. yield driver - отдаём драйвер тесту (код после yield выполняется после теста)
        4. driver.quit() - корректно закрываем браузер после завершения теста.
        
    Использование yield вместо return позволяет выполнить "очистку" (quit) даже если тест упал.
"""
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

"""
    Фикстура, возвращает уже авторизованный в системе браузер.
    Зависит от фикстуры `driver`: сначала возвращается обычный драйвер, а затем выполняется вход через UI.
    
    Зачем это нужно:
        - YouGile использует SSO через Яндекс, а сессии хранятся в HttpOnly-куках.
        - HttpOnly-куки нельзя установить напрямую через Selenium (браузер их не примет).
        - Поэтому единственный надёжный способ получить валидную сессию - реально пройти экран входа
        
    Шаги:
        1. Инициализируем страницу входа: LoginPage(driver)
        2. Открываем страницу: login_page.open()
        3. Выполняем вход: login_page.login(Config.LOGIN, Config.PASSWORD)
        4. Возвращает тот же driver, но уже с активной сессией.
        
    Теперь тесты, которые использует authorized_driver, сразу начинают с авторизованного состояния.
    Важно: это делает тесты медленнее (каждый раз происходит реальный вход), но зато они максимально близки к реальному поведению пользователя.
"""
@pytest.fixture
def authorized_driver(driver):
    """
        Пример использования в тесте:
        def test_create_board(self, authorized_driver) -> None:
            # Здесь уже не нужно логиниться — сессия активна
            assert board.is_board_present("Тестовая доска")
    """
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(Config.LOGIN, Config.PASSWORD)
    return driver
