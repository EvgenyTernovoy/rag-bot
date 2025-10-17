# Создание RAG бота

## Задание 3. Создание векторного индекса базы знаний

**База знаний** https://starwars.fandom.com/wiki/Main_Page

**Название модели:** all-MiniLM-L6-v2
**Ссылку на репозиторий / API:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
**Размер эмбеддингов:**  384
**Сколько чанков в индексе:** 2869
**Время генерации (разбитие на чанки, создание ембедингов, генерация индекса):** 22.4 сек 

## Задание 5. Запуск и демонстрация работы бота

Для защиты от выполнения вредоностных инструкций и утечки конфеденциальных данных был использован подход safety _in:

- после нахождения релевантных чанков мы проверяем на:
  - совпадение по regexp стоп слов
  - ищем слова с высокой энтропией используя shannon_entropy алгоритм, который показывает вероятность того, что слово является токеном или секретом

Выводы: Без дополнительного слоя защиты llm будет выдавать конфиденциальную информацию, даже если в system prompt мы добавили соответствующие инструкции. В дальнейшем стоит так же предусмотреть фильтрацию данных которые поподают в индекс. Так же хорошей практикой будет логировать события исключения чанков из выдачи, что бы своевременно реагировать на инциденты. 

Проверить роботоспособность бота можно через телеграмм: https://t.me/sw_fandom_rag_bot

## Задание 6. Автоматическое ежедневное обновление базы знаний

**Для запуска обновления в ручном режиме:**

```bash
cd ./chat-bot-service
bash update-index.sh
```

Если сервис был запущен через docker-compose, то он автоматически перезапуститься.

**Автоматическое обновление на сервере:**

- в качестве источнка новых данных мы используем публичный github
- для запуска скрипта по расписанию мы используем cron-задачу, запускаем ежедневно в 03:00
 
  `0 3 * * * /bin/bash /rag-bot/chat-bot-service/update-index.sh`
- Пример лога. При ошибке пишем данные в лог.
  ```
    ==============================================
    [2025-10-16 10:03:25] 🚀 Запуск обновления индекса...
    [2025-10-16 10:03:25] 📊 Запуск скрипта: ./app/update_index.py
    [2025-10-16 10:03:28] 🚀 Запуск обновления векторной базы...
    [2025-10-16 10:03:28] Существующих чанков до обновления: 3036
    [2025-10-16 10:03:35] ✅ Получено чанков: 3036
    [2025-10-16 10:03:48] Обновление завершено за 19.9 сек.
    [2025-10-16 10:03:48] Добавлено новых чанков: 0
    [2025-10-16 10:03:48] Итоговый размер индекса: 3036 векторов
    [2025-10-16 10:03:48] ✅ Индекс успешно обновлён.
    [2025-10-16 10:03:48] ♻️ Перезапуск сервиса faiss-search...
    [2025-10-16 10:03:51] ✅ Сервис успешно перезапущен.
    [2025-10-16 10:03:51] 🎯 Обновление завершено успешно.
  ```
- [Ссылка на UML диаграмму](https://www.planttext.com?text=PL9DRnCn4BtxLmmvjLARlN3Yr11GX6WHIiGvSdQdYS5hM_PiamWXGJbmuC0LgHA8Vr0AbK8Xy1Uy_uZn9YGGBjuTptjlFloE0abFLQa5AT88_KxlS6G9b2bm1fKh9264V8Ab58Ai0xB0UR8b5CfZJieQ8Mufa-kgmCfhc12vS2VBl9osnuecrQWAw7Dh20srSrjcVPLBNzX72Xtgh7lxyB6MXfwS76Ub38IUhuPTMpfh4iEbveJeie1K1lrUhn4zW5R7AUXnVrCvRt7uq9fn-lQGKL83a_qSd5M6Mli0VqaCxzhA5DBFzmRepz0pANw8d-FtU5c_YSlwRVm6zQjuNR-CL-ba-dC1i6sXunnprhjADU_P_5dISNEQMDFQ_mSzoBrob8fyYZUikOY_wdE8FxdYaiyhhdlDVulw7N1k6RzoUCFrBvFoI8R9Zjw3z3OTKvmWoQJwVijX0OW_kEVp5VjKgX0Eu6duhwbZEmw9VC4TV8cB16xJh1c6aI-46CpvBShX_HbjDnu_rg-RFIqsUrhbrZJHHxqPTyDobTPWS0gdIcDWM48rAzoPX8soplxHs0KqVjp1h2UPUiLMrHpiv5UFvR5nEh0NprIUD8xG5Eojtm00)


## Задание 7. Аналитика покрытия и качества базы знаний

**Для запуска тестов:**

```bash
cd ./chat-bot-service
python3 ./app/test_rag_bot.py
```

Анализ тестов:
- дополнить базу по биографии Kael Dravorn
- дополнить базу по Aether Blade
- добавить информацию на The Dominion Ascendant

Что можно улучшить:
- дополнить базу по выявленным пробелам
- поэксперементировать с колличеством чанков и длинной данных которые отдаем в llm
- улучшить эвристики при проведении тестов

[Ссылка на диаграмму](https://mermaid.live/edit#pako:eNqNkstu00AUhl_FOluSyK4Dtb2oVJWLkMqGwAZZqkw8pBHYLhMbAVGkJBWqqiCxZQVC4gHSqlFKk7ivcOaN-MduokYtl1nM5fh8__l9ZrrUTEJBHnXE20zETXG_HbRkEPmxgfG8I2R1a-vOs9beyyT1DP6mhnzJY9XnU56pLzxRQwPbnC8RytWgxMp0DT7dfrQHjXftpvgTPeXxOn2N0RIPtx83GoC_qmOe8NyAQm7wCagpTzS-wHbB5_yrxIt8gNX12t9hcqYO1VEhogaQOcec84XBZ3pRhzzHtwU85nx6q5XGgx0o_UStmfqshqoP5kptAoG-_iE1KlHk3jTx43rVE0BT3Tp0ZIC6I_Xp_63s7j4prOSoOofm0goCQ3QXRkoMeX_rxfhWaL1WdXX7_-JW917VD-cKuNA3pUbIuwlRhVqyHZKXykxUKBIyCvSRulrQp3RfRMInD9swkK998uMemIMgfpEk0RKTSdbaJ-9V8KaDU3YQBunyGa-iUsShkDtJFqfkuYUEeV16T57t1lzXdu_ZpmlZWOsV-oAUs2abG47j2ohZjm31KvSxqGnW3Lum5Thm3dy0MTbrvd8yvont)