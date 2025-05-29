#!/bin/bash

# Скрипт для проверки локальной среды разработки
# Использование: ./scripts/check-local.sh

set -e

echo "🔍 Проверка локальной среды разработки..."

# Проверка Poetry
echo "📦 Проверка Poetry..."
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry не установлен. Установите Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi
echo "✅ Poetry установлен: $(poetry --version)"

# Проверка Python версии
echo "🐍 Проверка Python..."
python_version=$(python3 --version | cut -d' ' -f2)
echo "✅ Python версия: $python_version"

# Установка зависимостей
echo "📚 Установка зависимостей..."
poetry install --no-interaction

# Проверка форматирования
echo "🎨 Проверка форматирования с Black..."
if poetry run black --check --diff src tests; then
    echo "✅ Форматирование корректно"
else
    echo "❌ Проблемы с форматированием. Запустите: poetry run black src tests"
    exit 1
fi

# Проверка импортов
echo "📋 Проверка импортов с isort..."
if poetry run isort --check-only --diff src tests; then
    echo "✅ Импорты корректны"
else
    echo "❌ Проблемы с импортами. Запустите: poetry run isort src tests"
    exit 1
fi

# Линтинг
echo "🔍 Линтинг с flake8..."
if poetry run flake8 src tests --max-line-length=88 --extend-ignore=E203,W503; then
    echo "✅ Линтинг прошел успешно"
else
    echo "❌ Проблемы с линтингом"
    exit 1
fi

# Проверка безопасности
echo "🔒 Проверка безопасности с Safety..."
if poetry run safety check; then
    echo "✅ Уязвимости не найдены"
else
    echo "⚠️ Найдены потенциальные уязвимости"
fi

# Проверка типов (если установлен mypy)
if poetry run python -c "import mypy" 2>/dev/null; then
    echo "🔍 Проверка типов с mypy..."
    if poetry run mypy src; then
        echo "✅ Типы корректны"
    else
        echo "❌ Проблемы с типами"
    fi
fi

echo ""
echo "🎉 Локальная среда готова к разработке!"
echo ""
echo "Полезные команды:"
echo "  poetry run black src tests          # Автоформатирование"
echo "  poetry run isort src tests          # Сортировка импортов"
echo "  poetry run pytest                   # Запуск тестов"
echo "  poetry run uvicorn src.main:app --reload  # Запуск сервера"
echo "" 