"""
Модуль для получения статистики из Яндекс.Метрика API отчётов
Документация: https://yandex.ru/dev/metrika/doc/api2/api_v1/intro.html
"""

import requests

METRIKA_API_URL = "https://api-metrika.yandex.net/stat/v1/data"

DEMO_DATA = {
    "Проект А": {"sessions": 980,  "bounceRate": 42.1, "goalConversions": 34},
    "Проект Б": {"sessions": 650,  "bounceRate": 38.5, "goalConversions": 21},
    "Проект В": {"sessions": 1720, "bounceRate": 35.8, "goalConversions": 58},
}


def get_stats(token: str, counter_id: str, date_from: str, date_to: str) -> dict:
    """
    Запрашивает сессии, отказы и конверсии из Яндекс.Метрики.
    Возвращает словарь: sessions, bounceRate, goalConversions
    """
    headers = {"Authorization": f"OAuth {token}"}
    params = {
        "id":      counter_id,
        "date1":   date_from,
        "date2":   date_to,
        "metrics": "ym:s:visits,ym:s:bounceRate,ym:s:goal<id>conversionRate",
        "limit":   1,
    }

    resp = requests.get(METRIKA_API_URL, headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(f"Метрика API ошибка {resp.status_code}: {resp.text}")

    data = resp.json()
    totals = data.get("totals", [0, 0, 0])
    return {
        "sessions":        int(totals[0]) if len(totals) > 0 else 0,
        "bounceRate":      round(float(totals[1]), 1) if len(totals) > 1 else 0.0,
        "goalConversions": int(totals[2]) if len(totals) > 2 else 0,
    }


def get_stats_demo(project_name: str) -> dict:
    """Возвращает демо-данные для презентации без реального токена."""
    return DEMO_DATA.get(project_name, {
        "sessions": 500, "bounceRate": 45.0, "goalConversions": 10
    })
