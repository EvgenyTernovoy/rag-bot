# FAISS Search Service


HTTP сервис для поиска по FAISS индексу с фильтрацией секретов и prompt injection. Оснавная модель yandexgpt


## 🚀 Установка и запуск

Добавить .env

```bash
FAISS_INDEX_PATH=/app/faiss.index
METADATA_PATH=/app/metadata.json
RELOAD_TOKEN=123qwe123qwe
YANDEX_FOLDER_ID=
YANDEX_AUTH=
```

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --env-file .env
```

или


```bash
docker-compose up -d --build
```

📡 API

GET /health — проверка статуса.

POST /search — тело: { "query": "..."}.

🧠 Безопасность

Сервис исключает или редактирует чанки, содержащие признаки prompt injection или секреты.

Логика вынесена в app/security.py.

📎 Пример запроса

```bash
curl -X POST http://localhost:8000/search \
-H "Content-Type: application/json" \
-d '{"query":"ваш запрос"}'
```

Ответ:

```json
{
    "results": "Ответ в текстовом виде"
}
```