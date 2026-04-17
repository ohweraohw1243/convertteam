"""
Модуль для получения статистики из Яндекс.Метрика API отчётов
Документация: https://yandex.ru/dev/metrika/doc/api2/api_v1/intro.html
"""

import requests

METRIKA_API_URL = "https://api-metrika.yandex.net/stat/v1/data"

DEMO_DATA = {
    "Проект А": {"sessions": 980,  "bounceRate": 42.1, "goal_vacancies": 5, "goal_tilda": 3, "goal_phone": 12},
    "Проект Б": {"sessions": 650,  "bounceRate": 38.5, "goal_vacancies": 2, "goal_tilda": 7, "goal_phone": 8},
    "Проект В": {"sessions": 1720, "bounceRate": 35.8, "goal_vacancies": 14, "goal_tilda": 9, "goal_phone": 31},
}


def get_stats(token: str, counter_id: str, date_from: str, date_to: str, goals: dict) -> dict:
    """
    Запрашивает сессии, отказы и КОНКРЕТНЫЕ ЦЕЛИ из Метрики по их ID
    """
    headers = {"Authorization": f"OAuth {token}"}
    
    # Формируем строку метрик для запроса к API Метрики
    # 'ym:s:goal<ID>reaches' - это количество достижений конкретной цели
    metrics_list = ["ym:s:visits", "ym:s:bounceRate"]
    
    if goals.get("vacancies"): metrics_list.append(f"ym:s:goal{goals['vacancies']}reaches")
    if goals.get("tilda"):     metrics_list.append(f"ym:s:goal{goals['tilda']}reaches")
    if goals.get("phone"):     metrics_list.append(f"ym:s:goal{goals['phone']}reaches")

    params = {
        "id":      counter_id,
        "date1":   date_from,
        "date2":   date_to,
        "metrics": ",".join(metrics_list),
        "limit":   1,
    }

    resp = requests.get(METRIKA_API_URL, headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(f"Метрика API ошибка {resp.status_code}: {resp.text}")

    data = resp.json()
    totals = data.get("totals", [0]*len(metrics_list))
    
    result = {
        "sessions":   int(totals[0]) if len(totals) > 0 else 0,
        "bounceRate": round(float(totals[1]), 1) if len(totals) > 1 else 0.0,
    }
    
    # Парсим цели обратно. totals массив идёт в том же порядке, что и metrics_list
    offset = 2
    if goals.get("vacancies"): 
        result["goal_vacancies"] = int(totals[offset])
        offset += 1
    if goals.get("tilda"):
        result["goal_tilda"] = int(totals[offset])
        offset += 1
    if goals.get("phone"):
        result["goal_phone"] = int(totals[offset])
        
    return result


def get_stats_demo(project_name: str) -> dict:
    """Возвращает демо-данные по нужным целям для презентации."""
    return DEMO_DATA.get(project_name, {
        "sessions": 500, "bounceRate": 45.0, "goal_vacancies": 3, "goal_tilda": 2, "goal_phone": 5
    })
