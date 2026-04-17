import os
from datetime import date, timedelta
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Токены и доступы
DIRECT_TOKEN = os.getenv("DIRECT_TOKEN", "")
DIRECT_CLIENT_LOGIN = os.getenv("DIRECT_CLIENT_LOGIN", "")
METRIKA_TOKEN = os.getenv("METRIKA_TOKEN", "")
METRIKA_COUNTER_ID = os.getenv("METRIKA_COUNTER_ID", "")

# ID конкретной цели из Метрики, если нужно считать только 1 спец. конверсию.
# Если оставить пустым, будет браться сумма всех целей из Директа
METRIKA_GOAL_ID = os.getenv("METRIKA_GOAL_ID", "")

# Период отчёта (по умолчанию за вчерашний день)
DATE_FROM = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
DATE_TO   = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# Проекты для выгрузки (Название: campaign_id или None для всех)
PROJECTS = {
    "Проект А": None,
    "Проект Б": None,
    "Проект В": None,
}

OUTPUT_PATH = "отчёт_реклама.xlsx"

# Настройки Google Sheets
GOOGLE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "")
