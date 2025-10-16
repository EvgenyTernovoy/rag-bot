import os
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from .utils import (
    create_message_to_llm,
    format_results,
    get_model,
    get_index_and_metadata,
    run_llm,
)

from .security import sanitize_for_runtime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне вопрос, и я поищу ответ в документах."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    model = get_model()
    index, metadata = get_index_and_metadata()

    q_vec = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_vec, 10)

    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx == -1:
            continue
        item = metadata[idx].copy()
        item["score"] = float(dist)
        results.append(item)

    safe_results = sanitize_for_runtime(results)
    documents = format_results(safe_results)
    message_to_llm = create_message_to_llm(documents, query)

    llm_response_text = run_llm(message_to_llm)

    # Отправляем пользователю ответ
    await update.message.reply_text(llm_response_text)


# Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
