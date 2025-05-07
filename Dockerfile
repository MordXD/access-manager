FROM python:3.12-slim

WORKDIR /code

# 1. Устанавливаем системные пакеты для сборки C-расширений и libpq
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# 2. Устанавливаем Poetry
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir poetry==1.7.1 

# 3. Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock* README.md /code/

# 4. Устанавливаем зависимости через Poetry (без проекта)
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# 5. Копируем исходники и миграции
COPY src/ /code/src/
COPY alembic.ini /code/
COPY alembic/ /code/alembic/

# 6. Точка входа
CMD ["uvicorn", "src.access_manager.main:app", "--host", "0.0.0.0", "--port", "8000"]
