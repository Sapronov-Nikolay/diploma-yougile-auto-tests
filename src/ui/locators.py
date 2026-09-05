# src/ui/locators.py
from selenium.webdriver.common.by import By

locators = {
    # Страница авторизации (главная -> /team/)
    'кнопка_перейти_к_входу': (By.CSS_SELECTOR, "a.sign-in-button"),
    'поле_почты': (By.CSS_SELECTOR, "input[type='email'][autocomplete='email']"),
    'поле_пароля': (By.CSS_SELECTOR, "input[type='password'][autocomplete='current-password']"),
    'кнопка_войти': (By.XPATH, "//div[@role='button' and .//div[text()='Войти']]"),
    'сообщение_ошибки': (By.CSS_SELECTOR, ".login-error"),

    # Заголовок "Моя компания" после успешного входа
    'заголовок_моя_компания': (By.CSS_SELECTOR, "[data-testid='my-company-header']"),

    # Левая панель - проекты (кнопка "+" рядом с "Моя компания")
    'кнопка_добавить_проект_в_меню': (By.CSS_SELECTOR, "[data-testid='add-project-button']"),
    'пункт_меню_проект_с_задачами': (By.CSS_SELECTOR, "[data-testid='menu-item-add-default-project']"),

    # Модальное окно создания проекта
    'поле_название_проекта': (By.CSS_SELECTOR, "input[placeholder='Введите название проекта…']"),
    'поле_id_проекта': (By.CSS_SELECTOR, "div.w-220 input[type='text']"),
    'кнопка_добавить_проект_с_задачами': (By.XPATH, "//div[contains(@class,'bg-action-default') and contains(.,'Добавить проект с задачами')]"),
    'кнопка_добавить_проект_с_задачами_disabled': (By.XPATH, "//div[contains(@class,'pointer-events-none') and contains(.,'Добавить проект с задачами')]"),
    'ошибка_дубликата_id': (By.CSS_SELECTOR, ".text-status-error.micro-regular"),

    # Список проектов слева (сам элемент с data-itemid)
    'проект_в_списке_с_id': (By.CSS_SELECTOR, "[data-testid='project-item']"),
    'проект_в_списке': (By.CSS_SELECTOR, "[data-testid='project-item'] .truncate"),
    'выбранный_проект_в_списке': (By.CSS_SELECTOR, "[data-testid='project-item'][class*='bg-panel-background-active']"),

    # Верхняя панель проекта
    'название_проекта_в_шапке': (By.CSS_SELECTOR, "[data-testid='project-name-upper-panel']"),

    # Доски (вкладки)
    'кнопка_плюс_создать_доску': (By.CSS_SELECTOR, "[data-testid='add-new-board']"),
    'пункт_меню_доска_с_задачами': (By.CSS_SELECTOR, "[data-testid='menu-item-add-board-tasks']"),
    'поле_название_доски': (By.CSS_SELECTOR, "input[placeholder*='Название доски']"),
    'вкладка_доски': (By.CSS_SELECTOR, "[data-testid='board-tab']"),

    # Колонки
    'кнопка_создать_колонку': (By.XPATH, "//span[text()='Создать колонку']"),
    'поле_название_колонки': (By.CSS_SELECTOR, "input[placeholder='Введите имя колонки…']"),
    'заголовок_колонки': (By.CSS_SELECTOR, ".task-group-title-new span"),

    # Задачи
    'кнопка_добавить_задачу': (By.XPATH, "//span[text()='Добавить задачу']"),
    'поле_название_задачи': (By.CSS_SELECTOR, "textarea[data-testid='board-task-input-name']"),
    'заголовок_задачи': (By.CSS_SELECTOR, "[data-testid='board-task-title'] span span"),

    # Архив проектов
    'архивный_заголовок': (By.XPATH, "//div[contains(@class,'min-w-0') and contains(text(), 'Архивированные проекты')]"),
    'проект_в_архиве': (By.CSS_SELECTOR, "[data-testid='project-card']"),
    'проект_три_точки': (By.CSS_SELECTOR, "[data-testid='project-card-menu-button']"),

    # Контекстное меню
    'пункт_меню_удалить': (By.XPATH, "//div[contains(@class,'menu-item') and .//div[text()='Удалить']]"),

    # Модальное окно подтверждения удаления
    'кнопка_подтвердить_удаление': (By.XPATH, "//div[@role='button' and .//div[text()='Удалить']]"),

    # НОВЫЙ ЛОКАТОР (добавлен для поиска карточки по названию)
    'заголовок_проекта_в_карточке': (By.CSS_SELECTOR, "[data-testid='project-title']"),
}
