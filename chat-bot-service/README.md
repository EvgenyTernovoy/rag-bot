# FAISS Search Service


HTTP сервис для поиска по FAISS индексу с фильтрацией секретов и prompt injection.


## 🚀 Установка и запуск


```bash
docker build -t chat-bot-service .
````

```bash
docker-compose up -d --build
```

📡 API

GET /health — проверка статуса.

POST /search — тело: { "query": "...", "k": 20 }.

POST /reload — перезагрузка ресурсов. Требует заголовок X-Reload-Token.

🧠 Безопасность

Сервис исключает или редактирует чанки, содержащие признаки prompt injection или секреты.

Логика вынесена в app/security.py.

📎 Пример запроса

```bash
curl -X POST http://localhost:8000/search \
-H "Content-Type: application/json" \
-d '{"query":"ваш запрос","k":10}'
```

Ответ:

```json
{
    "results": [
        {
            "title": "Документ 1",
            "chunk": "Отрывок текста",
            "score": 0.87
        }
    ]
}
```