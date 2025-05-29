# Устранение проблем CI/CD 🔧

Руководство по решению часто встречающихся проблем в CI/CD пайплайне.

## Ошибки GitHub Actions

### 1. "Error: missing server host"

**Проблема:** Не настроен секрет `DEPLOY_HOST` для SSH деплоя.

**Решение:**
```bash
# Добавьте в Settings → Secrets and variables → Actions
DEPLOY_HOST=your-server.com
DEPLOY_USER=deploy  
DEPLOY_SSH_KEY=<your-private-ssh-key>
DEPLOY_PORT=22
```

**Альтернатива:** Если деплой не нужен, workflow автоматически пропустит этот шаг.

### 2. "Error: Specify secrets.SLACK_WEBHOOK_URL"

**Проблема:** Не настроен секрет для Slack уведомлений.

**Решение:**
```bash
# Создайте Slack Webhook и добавьте в секреты
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

**Альтернатива:** Уведомления автоматически отключатся, если секрет не настроен.

### 3. Kubernetes деплой не работает

**Проблема:** Не настроены секреты для Kubernetes.

**Решение:**
```bash
# Для staging
STAGING_KUBECONFIG=<base64_encoded_kubeconfig>
STAGING_DB_HOST=staging-db.example.com
STAGING_DB_PASSWORD=password
STAGING_SECRET_KEY=secret-key
STAGING_URL=https://staging.example.com

# Для production
PROD_KUBECONFIG=<base64_encoded_kubeconfig>
PROD_DB_HOST=prod-db.example.com
PROD_DB_PASSWORD=password
PROD_SECRET_KEY=secret-key
PROD_URL=https://example.com
```

### 4. Docker Hub push не работает

**Проблема:** Не настроены Docker Hub учетные данные.

**Решение:**
```bash
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-access-token
```

## Локальные ошибки

### 1. Poetry lock конфликты

**Проблема:** Конфликты в `poetry.lock`

**Решение:**
```bash
rm poetry.lock
poetry lock
poetry install
```

### 2. Ошибки линтинга

**Проблема:** Код не соответствует стандартам форматирования.

**Решение:**
```bash
# Автоматическое исправление
poetry run black src tests
poetry run isort src tests

# Проверка
./scripts/check-local.sh
```

### 3. Ошибки тестов

**Проблема:** Тесты не проходят локально.

**Решение:**
```bash
# Запуск тестов с подробным выводом
poetry run pytest -v

# С покрытием
poetry run pytest --cov=src/access_manager --cov-report=html
```

### 4. Ошибки безопасности

**Проблема:** Safety находит уязвимости.

**Решение:**
```bash
# Обновление зависимостей
poetry update

# Игнорирование известных уязвимостей (если необходимо)
poetry run safety check --ignore 70716 --ignore 70715
```

## Проверки перед коммитом

Используйте скрипт для проверки:

```bash
./scripts/check-local.sh
```

Или выполните проверки вручную:

```bash
# Форматирование
poetry run black src tests
poetry run isort src tests

# Линтинг
poetry run flake8 src tests --max-line-length=88 --extend-ignore=E203,W503

# Тесты
poetry run pytest

# Безопасность
poetry run safety check
```

## Отладка workflow

### Просмотр логов

1. Перейдите в **Actions** в GitHub
2. Выберите неудачный workflow
3. Откройте failed job
4. Изучите логи конкретного шага

### Локальный запуск с act

```bash
# Установка act (для Ubuntu/WSL)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Запуск CI локально
act -j lint-and-format
act -j test
```

## Мониторинг

### Health Check

```bash
curl https://your-app.com/health
```

### Метрики

```bash
curl https://your-app.com/metrics
```

### Логи в Kubernetes

```bash
kubectl logs -f deployment/access-manager -n production
```

### Логи в Docker Compose

```bash
docker-compose logs -f backend
```

## Получение помощи

1. 📖 Читайте [документацию](../README_CICD.md)
2. 🔍 Проверьте [GitHub Actions логи](../../actions)
3. 🆘 Создайте [Issue](../../issues/new)
4. 💬 Обратитесь к команде DevOps

## Полезные команды

```bash
# Локальная разработка
poetry install
poetry run uvicorn src.access_manager.main:app --reload

# Docker
docker-compose up -d
docker-compose logs -f

# Kubernetes
kubectl get pods -n production
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production

# Git
git status
git add .
git commit -m "fix: исправление проблемы"
git push origin main
```

---

**Если проблема не решена, создайте Issue с:**
- Полным текстом ошибки
- Шагами для воспроизведения
- Логами из GitHub Actions
- Версией Poetry и Python 