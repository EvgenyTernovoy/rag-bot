import os
import csv
import re
from datetime import datetime

LOG_FILE = "./query_logs.csv"
# Инициализация CSV файла с заголовками
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp",
                "query",
                "chunks_found",
                "answer_length",
                "success_flag",
                "sources",
            ]
        )


def evaluate_success(answer: str) -> bool:
    """
    Улучшенная эвристика для определения успешности ответа.
    """
    text = answer.strip().lower()
    length = len(text)

    # 1) Минимальная длина
    if length < 200:
        return False

    # 2) Проверка на стоп-фразы
    negative_patterns = [
        "не знаю",
        "не найдено",
        "нет данных",
        "нет информации",
        "не могу",
        "не нашёл",
        "информации нет",
        "затрудняюсь",
        "неизвестно",
        "не содержит",
    ]
    for phrase in negative_patterns:
        if phrase in text:
            return False

    # 3) Проверка на ключевые сигнальные слова (глаголы/конструкции)
    positive_keywords = [
        "можно",
        "следует",
        "используется",
        "является",
        "включает",
        "объясняется",
        "описывается",
        "содержит",
        "означает",
        "находится",
        "например",
        "в частности",
    ]
    positive_score = sum(1 for kw in positive_keywords if kw in text)

    # 4) Разнообразие лексики
    words = re.findall(r"\w+", text)
    unique_ratio = len(set(words)) / max(len(words), 1)

    # 5) Количество предложений
    sentences = re.split(r"[.!?]+", text)
    sentence_count = sum(1 for s in sentences if s.strip())

    # Простейшая агрегирующая эвристика:
    if (
        positive_score >= 1
        and unique_ratio > 0.4
        and sentence_count >= 1
        and length > 40
    ):
        return True

    # Допустим, длинные ответы без стоп-фраз тоже ок
    if length > 100 and sentence_count >= 2:
        return True

    return False


def log_request(query: str, results: list, answer: str):
    """
    Записывает информацию о запросе и ответе в CSV.
    """
    timestamp = datetime.utcnow().isoformat()
    chunks_found = bool(results)
    answer_length = len(answer)
    success_flag = evaluate_success(answer)
    sources = "; ".join([r.get("file", "unknown") for r in results]) if results else ""

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [timestamp, query, chunks_found, answer_length, success_flag, sources]
        )
