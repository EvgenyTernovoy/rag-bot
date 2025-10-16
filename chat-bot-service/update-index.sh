#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="faiss-search"
LOG_FILE="./update_index.log"
INDEX_SCRIPT="./app/update_index.py"
ERROR_LOG="/tmp/update_index_error.log"

# ===== Функция логирования =====
log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# ===== Обработчик ошибок =====
error_handler() {
    local exit_code=$?
    local line_number=$1
    local failed_command="${BASH_COMMAND}"

    log "❌ Ошибка!"
    log "   📍 Строка: $line_number"
    log "   🧾 Команда: $failed_command"
    log "   💥 Код выхода: $exit_code"

    if [[ -f "$ERROR_LOG" ]]; then
        log "   📜 Подробности ошибки:"
        sed 's/^/   │ /' "$ERROR_LOG" | tee -a "$LOG_FILE"
        rm "$ERROR_LOG"
    fi

    log "🚨 Скрипт завершён с ошибкой."
    exit $exit_code
}
trap 'error_handler $LINENO' ERR

# ===== Очистка старого лог-файла ошибок =====
> "$ERROR_LOG"

log "=============================================="
log "🚀 Запуск обновления индекса..."

# ===== 1. Генерация индекса =====
log "📊 Запуск скрипта: $INDEX_SCRIPT"
python3 "$INDEX_SCRIPT" 2>>"$ERROR_LOG"
PY_EXIT_CODE=$?
if [[ $PY_EXIT_CODE -ne 0 ]]; then
    log "❌ Скрипт Python завершился с ошибкой (код $PY_EXIT_CODE)."
    exit $PY_EXIT_CODE
fi

# ===== 2. Проверка файлов =====
if [[ ! -f "faiss.index" || ! -f "metadata.json" ]]; then
    log "❌ Файлы faiss.index или metadata.json не найдены."
    exit 1
fi

# ===== 3. Перезапуск сервиса =====
log "♻️ Перезапуск сервиса $SERVICE_NAME..."
docker-compose restart "$SERVICE_NAME" 2>>"$ERROR_LOG"
log "✅ Сервис успешно перезапущен."

log "🎯 Обновление завершено успешно."
