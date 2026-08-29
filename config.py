# config.py
import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    BASE_URL = os.getenv("YOUGILE_URL", "https://api.yougille.com")
    LOGIN = os.getenv("YOUGILLE_LOGIN")
    PASSWORD = os.getenv("YOUGILLE_PASSWORD")
    COMPANY_ID = os.getenv("YOUGILLE_COMPANY_ID")
    CURRENT_KEY = os.getenv("YOUGILLE_CURRENT_KEY")

    @classmethod
    def ensure_dirs(cls):
        for d in ["screen_ui", "allure-results"]:
            os.makedirs(d, exist_ok=True)
