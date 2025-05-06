FROM python:3.12-slim

WORKDIR /code

# Устанавливаем Poetry (единожды)
# Обновляем pip и устанавливаем poetry
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry

# Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock* README.md /code/

# Устанавливаем зависимости БЕЗ установки текущего проекта (root package)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копируем исходники
COPY src/ /code/src/

# Точка входа (будет переопределена docker-compose.yml, но хорошо иметь для самостоятельной сборки)
CMD ["uvicorn", "src.access_manager.main:app", "--host", "0.0.0.0", "--port", "8000"]