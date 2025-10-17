import json
import datetime
import re
import requests
import csv

API_URL = "http://localhost:8000/search"
QUESTIONS_FILE = "./golden_questions.json"
LOG_FILE = "./rag_test_log.csv"


def get_rag_answer(question: str) -> str:
    """
    Отправляет запрос к локальному RAG сервису и возвращает текст ответа.
    """
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"query": question},
            timeout=100,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result")
    except Exception as e:
        print(f"❌ Ошибка при запросе: {e}")
        return ""


def evaluate_answer(answer: str, keywords: list[str]) -> tuple[bool, float]:
    """
    Проверка наличия ключевых слов в ответе и оценка полноты.
    """
    found = 0
    for kw in keywords:
        if re.search(re.escape(kw), answer, re.IGNORECASE):
            found += 1
    if not keywords:
        return False, 0.0
    recall = found / len(keywords)
    return found > 0, recall


def run_test():
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as log:
        writer = csv.writer(log)
        writer.writerow(
            ["id", "question", "expected", "answer", "found", "recall", "timestamp"]
        )

        for q in questions:
            qid = q["id"]
            question = q["question"]
            expected = q["expected_answer"]
            keywords = q["keywords"]

            print(f"🧪 Вопрос {qid}: {question}")
            answer = get_rag_answer(question)

            found, recall = evaluate_answer(answer, keywords)
            ts = datetime.datetime.now().isoformat()

            writer.writerow(
                [qid, question, expected, answer, found, f"{recall:.2f}", ts]
            )

            if found:
                print(f"✅ Найдено | полнота {recall:.2f}")
                print(f"Правильный ответ: {expected}")
            else:
                print(f"❌ Не найдено | полнота {recall:.2f}")

    print(f"\n📊 Тестирование завершено. Результаты сохранены в {LOG_FILE}")


if __name__ == "__main__":
    run_test()
