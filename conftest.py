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

import pytest, datetime, os, allure
from selenium import webdriver
from config import Config       # Класс с настройками (логины, URL и т.д.)
from src.api.client import YouGileApiClient     # Клиент для API-тестов
from src.ui.locators import locators
from src.ui.pages.login_page import LoginPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ALL_CREATED_PROJECT_IDS = []
"""Глобальный список ID всех проектов, созданных в ходе API-тестов"""

Config.ensure_dirs()  # Создаём папку для скриншотов при старте. Без них если тест отскринит падение, то скрин не сохранится

"""
    Эта функция вызывается pytest при старте сессии.
    Она нужна, чтобы зарегистрировать кастомные маркеры - метки для группировки тестов.
"""
def pytest_configure(config):
    config.addinivalue_line("markers", "ui: UI-тесты")
    config.addinivalue_line("markers","api: API-тесты")


"""
    Фикстура для создания экземпляра API-клиента.
"""
@pytest.fixture(scope="session")
def api_client():
    return YouGileApiClient()


"""
    Фикстура, которая создаёт и возвращает экземпляр драйвера браузера (chrome).
"""
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


"""
    Фикстура, возвращает уже авторизованный в системе браузер.
    Зависит от фикстуры `driver`: сначала возвращается обычный драйвер, а затем выполняется
    авторизация через UI и ожидание появления "Моя компания".
"""
@pytest.fixture
def authorized_driver(driver):
    login_page = LoginPage(driver)
    with allure.step("Открыть страницу входа"):
        login_page.open()
    with allure.step("Выполнить вход"):
        login_page.login(Config.LOGIN, Config.PASSWORD)
    with allure.step("Дождаться появления заголовка 'Моя компания'"):
        assert login_page.is_mainpage()
    driver.get(Config.BASE_URL + "/team/")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(locators['проект_карточка'])
    )
    return driver   # Теперь мы на /team/ с открытым разделом "Моя компания"


"""
    Функция для генерации скриншотов при падении тестов.
    Пишет информативное название файлам: имя упавшего теста и дата_время падения.
"""
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = None
        if "driver" in item.funcargs:
            driver = item.funcargs["driver"]
        elif "authorized_driver" in item.funcargs:
            driver = item.funcargs["authorized_driver"]
        if driver:
            test_name = item.name.replace("[", "_").replace("]", "_")
            timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
            screenshot_path = os.path.join("screenshots", f"{test_name}_{timestamp}.png")
            driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name="Screenshot", attachment_type=allure.attachment_type.PNG)

# # noinspection PyUnusedLocal
# def pytest_sessionfinish(session, exitstatus):
#     """
#         Физическое удаление всех проектов, созданных во время API-тестов.
#         Запускается только после сессии, в которой были API-тесты.
#     """
#     if ALL_CREATED_PROJECT_IDS:
#         from src.ui.pages.project_page import ProjectPage
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#         cleanup_driver = webdriver.Chrome(options=options)
#         cleanup_driver.maximize_window()
#         login_page = LoginPage(cleanup_driver)
#         login_page.open()
#         login_page.login(Config.LOGIN, Config.PASSWORD)
#         # Перейти на страницу проектов компании
#         cleanup_driver.get(Config.BASE_URL + "/team/")
#         WebDriverWait(cleanup_driver, 20).until(
#             EC.presence_of_element_located(locators['панель_проектов_компании'])
#         )
#         project_page = ProjectPage(cleanup_driver)
#         for pid in ALL_CREATED_PROJECT_IDS:
#             try:
#                 project_page.delete_project_by_id(pid)
#                 print(f"✅ Проект {pid} удалён")
#             except Exception as e:
#                 # Если карточка не найдена (проект уже удалён мягко), просто пропускаем
#                 print(f"⚠️ Проект {pid} не найден или уже удалён: {e}")
#         # Удаляем по конкретным ID
#         cleanup_driver.quit()
