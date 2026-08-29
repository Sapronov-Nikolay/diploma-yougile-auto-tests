# key_manager.py
"""
Утилита для управления API-ключами YouGile.
Позволяет:
- Посмотреть список всех ключей
- Удалить старые ключи, оставив один актуальный
- Автоматически обновить YOUGILE_CURRENT_KEY в .env

Важно: чувствительные данные (логин, пароль, URL) не хранятся в коде,
а берутся из файла .env через os.getenv → .
"""
import os, sys, requests
from dotenv import load_dotenv, set_key   # Загрузка .env и запись в него# Загрузка .env и запись в него

# Загружаем переменные из файла .env (например, YOUGILE_LOGIN, YOUGILE_PASSWORD и т.д.)
# Если файла нет или он не настроен — переменные будут None
load_dotenv()

# ------------------------------------------------------------------
# Чтение конфигурации из переменных окружения
# ------------------------------------------------------------------
BASE_URL = os.getenv("YOUGILE_URL")                 # Базовый URL API (например, https://yougile.com/api-v2)
LOGIN = os.getenv("YOUGILE_LOGIN")                  # Логин для получения/удаления ключей
PASSWORD = os.getenv("YOUGILE_PASSWORD")            # Пароль (лучше не хранить в открытом месте поэтому .env в .gitignore)
COMPANY_ID = os.getenv("YOUGILE_COMPANY_ID")        # ID компании в YouGile
CURRENT_KEY = os.getenv("YOUGILE_CURRENT_KEY")      # Текущий активный ключ (чтобы не удалить его случайно)

# Проверка: если чего-то не хватает, дальше работать нельзя
if not all([BASE_URL, LOGIN, PASSWORD, COMPANY_ID]):
    print("❌ Ошибка: не все переменные окружения заданы в .env")
    sys.exit(1)

def get_all_keys():
    """
        Получает список всех API-ключей для компании.
        Возвращает JSON-ответ в виде списка словарей.
    """
    url = f"{BASE_URL}/api-v2/auth/keys/get"
    # Тело запроса: передаём логин, пароль и companyId
    payload ={
        "login": LOGIN,
        "password": PASSWORD,
        "companyId": COMPANY_ID
    }
    resp = requests.post(url, json=payload)
    # Если сервер вернул ошибку (4xx, 5xx), сразу выбросит исключение
    resp.raise_for_status()
    return resp.json()

def delete_key(key_value, current_key):
    """
        Удаляет один выбранный API-ключ по его значению
        key-value: с самим ключом, который хотим удалить
        current_key: ключ, от имени которого делаем удаление (должен быть активным)
        Возвращает True, если удаление прошло успешно (HTTP 200), иначе False.
    """
    # URL вида: /api-v2/auth/keys/<key>
    url = f"{BASE_URL}/api-v2/auth/keys/{key_value}"
    # Авторизация через Bearer-токен (текущий активный ключ)
    headers = {"Authorization": f"Bearer {current_key}"}
    resp = requests.delete(url, headers=headers)
    # Успешным считаем только статус 200

def list_keys():
    """
        Выводит читаемый список всех API-ключей.
        Помечает текущий ключ пометкой "← ТЕКУЩИЙ".
    """
    try:
        keys = get_all_keys()
    except Exception as e:
        print(f"❌ Ошибка при получении списка ключей: {e}")
        return

    print("\n" + "=" * 70)
    print("🔑 СПИСОК ВСЕХ API-КЛЮЧЕЙ")
    print("=" * 70)
    print(f"📊 Всего ключей: {len(keys)}")
    print("=" * 70)

    for i, key_data in enumerate(keys, 1):
        # .get() безопаснее, чем key_data["key"], если ключа вдруг нет
        key_value = key_data.get("key", "НЕТ ЗНАЧЕНИЯ")
        timestamp = key_data.get("timestamp", "неизвестно")
        # Проверяем, совпадает ли этот ключ с текущим (из .env)
        is_current = "← ТЕКУЩИЙ" if CURRENT_KEY and key_value == CURRENT_KEY else ""
        print(f"{i:2}. КЛЮЧ: {key_value}")
        print(f"   ДАТА: {timestamp}({is_current})")
        print("=" * 70)

    print("=" * 70)
    print("💡 Для очистки введите команду: python key_manager.py --clean")
    print("=" * 70 + "\n")

def clean_keys(keep_key=None):
    """
        Очищает старше API-ключи, оставляя только один (keep_key).
         Если keep_key не передан, то используется CURRENT_KEY из .env.
         Если и его нет - создаётся новый ключ и сохраняется как текущий.
         И обновляет .env: YOUGILE_CURRENT_KEY = <новый ключ>
    """
    # Логика выбора ключа, которую надо оставить
    if keep_key is None:
        keep_key = CURRENT_KEY

    # Если даже текущего ключа нет - создаём новый
    if not keep_key:
        print("🔑 Получаем новый ключ...")
        try:
            resp = requests.post(f"{BASE_URL}/api-v2/auth/keys", json={
                "login": LOGIN,
                "password": PASSWORD,
                "companyId": COMPANY_ID
            })
            resp.raise_for_status()
            # Из ответа берём только сам ключ
            keep_key = resp.json()["key"]
            print(f"✅ Получаем новый ключ: {keep_key[:20]}...")
        except Exception as e:
            print(f"❌ Ошибка при создании нового ключа: {e}")
            return

    print("\n" + "=" * 70)
    print("🧹 ОЧИСТКА СТАРЫХ API-КЛЮЧЕЙ")
    print("=" * 70)

    try:
        keys = get_all_keys()
    except Exception as e:
        print(f"❌ Ошибка при получении списка ключей: {e}")
        return
    print(f"📊 Найдено ключей: {len(keys)}")
    print(f"🔑 Сохранённый: {keep_key[:20]}...")

    deleted = 0
    skipped = 0

    for key in keys:
        key_value = key["key"]
        # Если это тот самый ключ, который мы хотим оставить - то пропускаем
        if key_value == keep_key:
            print(f"⏭️ Пропускаем: {key_value[:20]}...")
            deleted += 1
            continue

        # пробуем удалить
        if delete_key(key_value, keep_key):
            print(f"✅ Удалён: {key_value[:20]}...")
            deleted += 1
        else:
            print(f"⚠️ Не удалось удалить: {key_value[:20]}...")

    print("=" * 70)
    print(f"✅ Удалено: {deleted}")
    print(f"⏭️ Пропущено: {skipped}")
    print(f"📊 Осталось: {len(keys) - skipped}")
    print("=" * 70)

    # Обновляем .env, чтобы сохранить новый текущий ключ
    set_key(".env", "YOUGILE_CURRENT_KEY", keep_key)
    print(f"✅ .env обновлён: YOUGILE_CURRENT_KEY = {keep_key[:20]}...\n")

# Точка входа: когда запускается python key_manager.py ...
if __name__ == "__main__":
    # sys.argv - это список аргументов командной строки
    # Пример: ["key_manager.py", "--list"] или ["key_manager.py", "--clean", "--keep", "abc123"]
    if "--list" in sys.argv:
        list_keys()

    elif "--clean" in sys.argv:
        # поддержка необязательного флага --keep <key>
        keep_key = None
        if "--keep" in sys.argv:
            idx = sys.argv.index("--keep") + 1
            # Проверяем, что после --keep действительно есть значение
            if idx < len(sys.argv):
                keep_key = sys.argv[idx]
            else:
                print("❌ Ошибка: после --keep укажите значение ключа")
                sys.exit(1)
        clean_keys(keep_key)
    else:
        # Если никаких флагов не передано в команде - показываем справку
        print("""
            Использование:
            python key_manager.py --list
                Показать список всех API-ключей
                
            python key_manager.py --clean
                Удалить все ключи, кроме текущего (CURRENT_KEY из .env)
                
            python key_manager.py --clean --keep <key>
                Удалить все, кроме указанного ключа
        """)
