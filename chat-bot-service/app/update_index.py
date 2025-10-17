import os
import json
import faiss
import uuid
import numpy as np
from pathlib import Path
from datetime import datetime
import tiktoken
from sentence_transformers import SentenceTransformer
import sys
import traceback
import time

LOG_PATH = "./update_index.log"
INPUT_DIR = "../knowledge_base"
INDEX_PATH = "./faiss.index"
METADATA_PATH = "./metadata.json"

MAX_TOKENS = 200
OVERLAP = 32


# ================== UTILS ==================


def log_message(message: str):
    """Пишет сообщение в лог с таймстампом."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(full_message + "\n")


def read_md_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ================== CHUNKING ==================


def chunk_by_tokens(
    text: str, source: str, max_tokens: int = MAX_TOKENS, overlap: int = 32, enc=None
):
    enc = enc or tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    start = 0
    chunks = []
    title = Path(source).stem

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_text = enc.decode(tokens[start:end])
        chunk_id = str(uuid.uuid4())

        chunks.append(
            {
                "chunk_id": chunk_id,
                "file": source,
                "title": title,
                "chunk": chunk_text,
                "start_token": start,
                "end_token": end,
                "start_char": len(enc.decode(tokens[:start])),
                "end_char": len(enc.decode(tokens[:end])),
            }
        )

        if end == len(tokens):
            break
        start = end - overlap

    return chunks


def process_directory(input_dir: str, max_tokens=MAX_TOKENS, overlap=32):
    enc = tiktoken.get_encoding("cl100k_base")
    all_chunks = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if Path(file).suffix.lower() != ".md":
                continue
            file_path = os.path.join(root, file)
            text = read_md_file(file_path)
            if not text:
                continue
            file_chunks = chunk_by_tokens(text, file_path, max_tokens, overlap, enc)
            all_chunks.extend(file_chunks)
    return all_chunks


# ================== FAISS ==================


def embed_chunks(chunks, model):
    texts = [c["chunk"] for c in chunks]
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return vectors


def build_faiss_index(vectors: np.ndarray):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index


def save_faiss_index(index, path=INDEX_PATH):
    faiss.write_index(index, path)


def save_metadata(chunks, path=METADATA_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


# ================== MAIN ==================
def main():
    start_time = time.time()
    try:
        log_message("🚀 Запуск обновления векторной базы...")

        # --- 1. Подсчёт существующих чанков ---
        start_count = 0
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                existing_chunks = json.load(f)
                start_count = len(existing_chunks)
                log_message(f"Существующих чанков до обновления: {start_count}")
        else:
            log_message("metadata.json не найден, начинаем с нуля")

        # --- 2. Обработка файлов и чанков ---
        all_chunks = process_directory(INPUT_DIR)
        log_message(f"✅ Получено чанков: {len(all_chunks)}")

        # --- 3. Генерация эмбеддингов ---
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        vectors = embed_chunks(all_chunks, model)

        # --- 4. Построение FAISS индекса ---
        index = build_faiss_index(vectors)
        save_faiss_index(index, INDEX_PATH)
        save_metadata(all_chunks, METADATA_PATH)

        # --- 5. Логирование метрик ---
        duration = round(time.time() - start_time, 2)
        log_message(f"Обновление завершено за {duration} сек.")
        log_message(f"Добавлено новых чанков: {len(all_chunks) - start_count}")
        log_message(f"Итоговый размер индекса: {index.ntotal} векторов")

        log_message("✅ Индекс успешно обновлён.")

    except Exception as e:
        log_message(f"Ошибка при обновлении индекса: {e}", error=True)
        log_message(traceback.format_exc(), error=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
