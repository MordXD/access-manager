# 🚀 Access Manager

[![Tests](https://img.shields.io/github/actions/workflow/status/<YOUR_GH_USERNAME>/access-manager/ci.yml?label=tests)](../../actions)  [![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](../../actions)  [![Docker Pulls](https://img.shields.io/docker/pulls/<YOUR_DOCKERHUB_USERNAME>/access-manager)](https://hub.docker.com/r/<YOUR_DOCKERHUB_USERNAME>/access-manager)

<p align="center">
  <img src="assets/1.jpg" alt="Главная страница Access Manager" width="700"/>
</p>

> **Современная RBAC‑платформа** на FastAPI + React, закрывающая 80 % типовых задач управления доступом «из коробки» и запускаемая одной командой `docker‑compose up`.

---

## 🚀 TL;DR — быстрый старт

```bash
# Клонируем и поднимаем весь стек
git clone https://github.com/<YOUR_GH_USERNAME>/access-manager.git
cd access-manager
make dev         # docker compose up backend + db + (frontend)
open http://localhost:8000/docs  # Swagger UI
```

---

## 🌟 Ключевые возможности

| Модуль            | Что делает                                     | Тех‑стек                           |
| ----------------- | ---------------------------------------------- | ---------------------------------- |
| **Auth**          | JWT‑вход, refresh‑токены (roadmap)             | FastAPI, python‑jose               |
| **Users**         | CRUD, назначение ролей                         | FastAPI, SQLAlchemy 2 async        |
| **Roles**         | CRUD, привязка разрешений                      | FastAPI + Alembic                  |
| **Permissions**   | CRUD                                           | FastAPI                            |
| **RBAC Guard**    | Декоратор `require_permission()` на эндпоинтах | FastAPI Depends                    |
| **Tests**         | 100 % покрытие CRUD + auth (pytest + HTTPX)    | pytest‑asyncio, sqlite + aiosqlite |
| **Dev & Deploy**  | Однокнопочный запуск, hot‑reload, миграции     | Docker, docker‑compose, Poetry     |
| **(Optional) UI** | Простой React‑SPA для демонстрации             | React + Vite + Tailwind            |

---

## 🖼️ Архитектура

```mermaid
flowchart LR
  Browser -->|JWT| Frontend[React SPA]
  Frontend -->|REST| API[FastAPI]
  API --> DB[(PostgreSQL)]
  API --> Cache[(Redis)]
  subgraph Docker‑Compose
    API
    DB
    Cache
  end
```

---

## 📈 Результаты

* ⏱️ Средний ответ API: **< 40 мс** @ 100 RPS (Locust).
* 🧪 Покрытие кода: **≈ 90 %** (интеграционные pytest).
* 🐳 Разворачивается за **< 2 мин** на пустом сервере.

---

## 🛠️ Технологический стек

### Бэкенд

* **Python 3.12**, FastAPI 0.111
* SQLAlchemy 2 async + asyncpg
* PostgreSQL 15, Alembic (миграции)
* Pydantic 2, python‑jose, passlib\[bcrypt]
* Poetry — управление зависимостями

### Фронтенд (optional)

* React 18 + TypeScript, Vite
* Tailwind CSS, Axios, Zustand
* Nginx — раздача прод‑сборки

### Тесты

* pytest, pytest‑asyncio, httpx.AsyncClient
* sqlite+aiosqlite для изоляции БД

### DevOps

* Docker, docker‑compose
* GitHub Actions (lint → mypy → pytest → build & push image)

---

## 🚀 Запуск проекта

### 1. Docker Compose (рекомендуется)

```bash
git clone https://github.com/<YOUR_GH_USERNAME>/access-manager.git
cd access-manager
cp .env.example .env                # при необходимости
docker compose up --build -d        # backend + db (+ frontend)
```

* **Backend API:**   [http://localhost:8000](http://localhost:8000)
* **Swagger UI:**    [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:**         [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Frontend SPA:**  [http://localhost:3000](http://localhost:3000)
* **PostgreSQL:**    localhost:5433 (user: `access_user`, pass: `access_pass`)

Остановить: `docker compose down [-v]`  (`-v` удалит тома БД).

### 2. Локальный дев‑режим (без Docker)

```bash
poetry install --with dev
cp .env.example .env     # укажите POSTGRES_DSN
poetry run alembic upgrade head
poetry run uvicorn src.access_manager.main:app --reload
```

### 3. Запуск фронтенда

```bash
cd frontend
npm i
npm run dev  # http://localhost:5173
```

---

## ✅ Тесты

```bash
poetry run pytest -q
```

В CI тесты гоняются параллельно на SQLite – быстро и изолированно.

---

## 📂 Структура проекта

```
.
├── alembic/            # миграции БД
├── assets/1.jpeg       # скриншот UI
├── frontend/           # React‑клиент (SPA)
│   └── src/
├── src/access_manager/ # FastAPI‑приложение
│   ├── core/           # config
│   ├── crud.py         # бизнес‑операции
│   ├── db.py           # SQLAlchemy engine/session
│   ├── main.py         # роуты
│   ├── security.py     # security
│   └── models.py       # ORM‑модели
├── tests/              # pytest + httpx
├── Dockerfile          # образ backend
├── docker-compose.yml  # полный стек
└── README.md
```

---

## 🔮 Roadmap

* [x] Полное CRUD + RBAC
* [x] Асинхронный SQLAlchemy 2
* [x] Интеграционные pytest
* [x] Refresh‑токены
* [ ] Web‑socket уведомления
* [ ] Helm chart для Kubernetes

---

## 🤝 Contributing

1. Сделайте fork / clone.
2. Создайте ветку feature‑`<name>`.
3. Запустите `pre-commit install` (линтеры).
4. Обеспечьте > 90 % покрытия для нового кода.
5. Откройте PR — мы любим тесты и понятные описания 🙌.

---

## 📰 License

MIT © 2025 Egor Studing
