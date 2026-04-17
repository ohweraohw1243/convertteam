"""
Главный скрипт: собирает данные из Яндекс.Директ и Яндекс.Метрики
и выгружает их в Google Таблицу.

Запуск:  python3 generate_report.py
"""

import sys
import os
from datetime import date
import gspread

sys.path.insert(0, os.path.dirname(__file__))
import config
import direct
import metrika

# ── режим: DEMO если токены пустые, LIVE если заполнены ──────────────────────
# Принудительно включен демо-режим для тестирования:
DEMO_MODE = True
GOOGLE_READY = bool(config.GOOGLE_SHEET_URL)

if DEMO_MODE:
    print("⚠️  Токены не заданы — запуск в ДЕМО-режиме с тестовыми данными")
    print("   Заполните DIRECT_TOKEN и METRIKA_TOKEN в config.py для боевого режима\n")
else:
    print(f"✅ Боевой режим | период: {config.DATE_FROM} → {config.DATE_TO}\n")

if not GOOGLE_READY:
    print("⚠️  Ссылка на Google Таблицу (GOOGLE_SHEET_URL) не заполнена в config.py")
    print("   Будут выведены только результаты работы в консоль.\n")


def collect_data() -> list[dict]:
    """Собирает данные по всем проектам из конфига."""
    rows = []
    for project_name in config.PROJECTS:
        print(f"  → {project_name} ...", end=" ")

        if DEMO_MODE:
            d = direct.get_stats_demo(project_name)
            m = metrika.get_stats_demo(project_name)
        else:
            d = direct.get_stats(
                token=config.DIRECT_TOKEN,
                client_login=config.DIRECT_CLIENT_LOGIN,
                date_from=config.DATE_FROM,
                date_to=config.DATE_TO,
            )
            # В боевом режиме запрашиваем конкретные цели через их ID из Метрики
            m = metrika.get_stats(
                token=config.METRIKA_TOKEN,
                counter_id=config.METRIKA_COUNTER_ID,
                date_from=config.DATE_FROM,
                date_to=config.DATE_TO,
                goals=config.METRIKA_GOALS
            )

        rows.append({
            "project":     project_name,
            "impressions": d["impressions"],
            "clicks":      d["clicks"],
            "cost":        d["cost"],
            "conversions": d["conversions"],
            "sessions":    m["sessions"],
            "bounce_rate": m["bounceRate"],
            "goal_vacancies": m.get("goal_vacancies", 0),
            "goal_tilda":     m.get("goal_tilda", 0),
            "goal_phone":     m.get("goal_phone", 0),
        })
        print("OK")

    return rows


def export_to_google_sheets(rows: list[dict]):
    if not GOOGLE_READY:
        print("\n📝 Данные для выгрузки (Google Sheet не настроен):")
        for r in rows:
            print(r)
        return

    print("\nПодключение к Google Таблицам...")
    try:
        gc = gspread.service_account(filename=config.GOOGLE_CREDENTIALS_FILE)
        sh = gc.open_by_url(config.GOOGLE_SHEET_URL)
        ws = sh.sheet1  # Берём первый лист, либо можно по имени: sh.worksheet("Название")
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        print("Убедитесь, что файл credentials.json лежит в папке, а в таблице выдан доступ email'у из этого файла-ключа.")
        return

    export_dt = date.today().strftime('%d.%m.%Y')
    
    # Проверяем, есть ли уже заголовки в таблице. Если таблица пустая - добавляем их.
    existing_data = ws.get_all_values()
    # gspread может вернуть [[]] для пустой таблицы
    if not existing_data or not any(existing_data[0]):
        print("Таблица пустая, добавляем заголовки...")
        headers = [
            "Дата", 
            "Расход, в руб,", 
            "Количество показов", 
            "Кол-во кликов", 
            "CPC", 
            "CTR (количество показов к кликам)", 
            "Заявки по Вакансиям (тильда+клик по номеру телефона)", 
            "Все формы Тильда", 
            "Клик по номеру телефона"
        ]
        ws.append_row(headers)

    print("Добавление новых строк: ")
    # Собираем все строки для выгрузки массивом
    data_to_append = []
    
    for row in rows:
        imp = row["impressions"]
        clk = row["clicks"]
        cost = row["cost"]
        conv = row["conversions"]
        sess = row["sessions"]
        bnc = row["bounce_rate"]

        ctr = round((clk / imp * 100) if imp > 0 else 0, 2)
        cpc = round((cost / clk) if clk > 0 else 0, 2)

        # Новая структура (конкретные цели из вашей Метрики)
        data_to_append.append([
            export_dt,                   # Дата
            f"р.{cost}".replace('.', ','), # Расход, в руб,
            imp,                         # Количество показов
            clk,                         # Кол-во кликов
            f"р.{cpc}".replace('.', ','),  # CPC
            f"{ctr}%".replace('.', ','),   # CTR (количество показов к кликам)
            row.get("goal_vacancies", 0),  # Заявки по Вакансиям (тильда+клик по номеру телефона)
            row.get("goal_tilda", 0),      # Все формы Тильда
            row.get("goal_phone", 0)       # Клик по номеру телефона
        ])

    # Пакетная выгрузка
    ws.append_rows(data_to_append, value_input_option='USER_ENTERED')
    print(f"✅ Успешно выгружено {len(data_to_append)} строк в таблицу: {sh.title}")


if __name__ == "__main__":
    print("Сбор данных...")
    rows = collect_data()
    export_to_google_sheets(rows)
