# CI/CD для Access Manager 🚀

Полноценный CI/CD пайплайн для FastAPI приложения управления доступом с автоматическим тестированием, безопасностью и мониторингом.

## 🌟 Особенности

- ✅ **Непрерывная интеграция**: автоматическое тестирование, линтинг, сканирование безопасности
- 🚀 **Непрерывная доставка**: автоматический деплой в staging/production  
- 🐳 **Контейнеризация**: Docker и Kubernetes поддержка
- 📊 **Мониторинг**: Health checks, метрики Prometheus, алерты
- 🔒 **Безопасность**: сканирование уязвимостей, проверка секретов
- 📈 **Масштабируемость**: HPA, load balancing, резервное копирование

## ⚠️ Важно: Настройка секретов

**CI/CD будет работать частично без настройки секретов**, но для полной функциональности необходимо настроить GitHub Secrets.

### Обязательные секреты для деплоя

Настройте в **Settings → Secrets and variables → Actions**:

#### Для Kubernetes деплоя:
```bash
# Staging окружение
STAGING_KUBECONFIG=<base64_encoded_kubeconfig>
STAGING_DB_HOST=staging-db.your-domain.com
STAGING_DB_PASSWORD=your-staging-password
STAGING_SECRET_KEY=your-staging-secret-key
STAGING_URL=https://staging.your-domain.com

# Production окружение  
PROD_KUBECONFIG=<base64_encoded_kubeconfig>
PROD_DB_HOST=prod-db.your-domain.com
PROD_DB_PASSWORD=your-prod-password
PROD_SECRET_KEY=your-prod-secret-key
PROD_URL=https://your-domain.com
```

#### Для Docker Compose деплоя:
```bash
# SSH доступ к серверу
DEPLOY_HOST=your-server.com
DEPLOY_USER=deploy
DEPLOY_SSH_KEY=<private_ssh_key>
DEPLOY_PORT=22

# Переменные приложения
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-production-secret-key
POSTGRES_PASSWORD=your-postgres-password
```

#### Для Docker Hub:
```bash
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-token
```

#### Для уведомлений (опционально):
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Что работает без секретов:

- ✅ Линтинг и форматирование (Black, isort, flake8)
- ✅ Тестирование с покрытием кода
- ✅ Сканирование безопасности (Safety, GitLeaks)
- ✅ Сборка Docker образов
- ✅ Интеграционные тесты

### Что требует секреты:

- ❌ Деплой в Kubernetes
- ❌ Деплой через Docker Compose
- ❌ Slack уведомления
- ❌ Мониторинг внешних URL

## 🚀 Быстрый старт

### 1. Настройка GitHub Secrets

```bash
# Docker Hub
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-token

# Production окружение
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
PROD_URL=https://your-domain.com

# Уведомления (опционально)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### 2. Создание веток

```bash
git checkout -b develop
git push origin develop

git checkout -b main  
git push origin main
```

### 3. Запуск пайплайна

Просто сделайте commit в `develop` или `main` ветку - пайплайн запустится автоматически!

```bash
git add .
git commit -m "feat: добавил новую функциональность"
git push origin develop  # Деплой в staging
```

## 📋 Структура пайплайнов

### CI Pipeline (`.github/workflows/ci.yml`)
- 🔍 Линтинг (Black, isort, flake8)
- 🧪 Тестирование с покрытием кода  
- 🔒 Сканирование безопасности
- 🐳 Сборка Docker образов
- ✅ Интеграционные тесты

### CD Pipeline (`.github/workflows/cd.yml`)
- 🎯 Staging деплой (`develop` ветка)
- 🚀 Production деплой (`main` ветка)
- 📦 Создание релизов (теги `v*`)
- 🔄 Rollback поддержка

### Monitoring (`.github/workflows/monitoring.yml`)
- ❤️ Health checks каждые 5 минут
- 📊 Performance тестирование
- 🔐 SSL сертификаты мониторинг
- 💾 Проверка бэкапов

## 🎯 Окружения деплоя

| Окружение | Ветка | URL | Автодеплой |
|-----------|-------|-----|------------|
| **Staging** | `develop` | staging-app.com | ✅ Автоматический |
| **Production** | `main` | app.com | ⚠️ Ручное подтверждение |

## 🛠️ Локальная разработка

```bash
# Клонирование
git clone https://github.com/your-org/access-manager.git
cd access-manager

# Настройка окружения
cp env.example .env
# Отредактируйте .env файл

# Запуск с Docker Compose
docker-compose up -d

# Или локально с Poetry
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.access_manager.main:app --reload
```

## 📊 Мониторинг

### Health Check
```bash
curl https://your-app.com/health
```

### Метрики Prometheus
```bash
curl https://your-app.com/metrics
```

### Логи
```bash
# Kubernetes
kubectl logs -f deployment/access-manager -n production

# Docker Compose  
docker-compose logs -f backend
```

## 🔧 Настройка деплоя

### Kubernetes (рекомендуется)

1. **Создайте кластер** (GKE, EKS, AKS)
2. **Настройте kubeconfig** и добавьте в GitHub Secrets
3. **Обновите values.yaml** с вашими настройками
4. **Commit в main** - автоматический деплой!

### Docker Compose (простой)

1. **Подготовьте сервер** с Docker
2. **Добавьте SSH ключи** в GitHub Secrets  
3. **Настройте .env** файл на сервере
4. **Push в main** - автоматический деплой!

## 🔐 Безопасность

- 🔍 **Сканирование зависимостей** с Safety
- 🕵️ **Поиск секретов** с GitLeaks  
- 🛡️ **Docker образы** сканирование
- 🔒 **SSL сертификаты** мониторинг
- 🚨 **Алерты** в Slack при проблемах

## 📦 Релизы

Создание релиза:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Автоматически создаст:
- 📋 GitHub Release с changelog
- 🐳 Docker образы с тегами
- 📚 Обновление документации

## 🚨 Troubleshooting

### Частые проблемы

**CI падает на тестах:**
```bash
# Запустите тесты локально
poetry run pytest -v
```

**Docker сборка не работает:**
```bash
# Проверьте локально
docker build -t access-manager .
```

**Деплой в Kubernetes не работает:**
```bash
# Проверьте kubeconfig
kubectl cluster-info
helm lint ./helm/access-manager
```

### Получение помощи

1. 📖 Читайте [полную документацию](docs/CICD_SETUP.md)
2. 🔍 Проверьте [GitHub Actions логи](../../actions)
3. 🆘 Создайте [Issue](../../issues/new)
4. 💬 Спросите в Slack канале

## 🎉 Что дальше?

- [ ] Настройте мониторинг с Grafana
- [ ] Добавьте E2E тесты с Playwright
- [ ] Настройте blue-green deployment
- [ ] Интегрируйте с Sentry для error tracking
- [ ] Добавьте database миграции rollback

## Настройка уведомлений

### Отключение email уведомлений от GitHub Actions

Чтобы не получать email уведомления о каждом запуске CI/CD:

1. Перейдите в настройки GitHub: https://github.com/settings/notifications
2. В разделе "Actions" снимите галочку с "Email" для:
   - "Failed workflows only" (только неудачные workflow)
   - "Successful workflows" (успешные workflow)

### Настройка Slack уведомлений

Для настройки Slack уведомлений добавьте секреты в GitHub:

```bash
# В настройках репозитория -> Settings -> Secrets and variables -> Actions
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Типы уведомлений

- **Ошибки линтинга**: отправляются в канал `#ci-cd`
- **Ошибки деплоя**: отправляются в канал `#deployments`
- **Проблемы безопасности**: отправляются в канал `#security`
- **Мониторинг**: отправляются в канал `#alerts`

### Отключение уведомлений

Чтобы полностью отключить Slack уведомления, удалите секрет `SLACK_WEBHOOK_URL` из настроек репозитория.

## Мониторинг и алерты

### Автоматические проверки

- **Health checks**: каждые 5 минут проверяется доступность API
- **Database checks**: проверка подключения к базе данных
- **SSL certificates**: проверка срока действия сертификатов
- **Performance tests**: нагрузочное тестирование (запускается вручную)

### Настройка мониторинга

1. Добавьте URL-адреса ваших сред в секреты:
   ```
   STAGING_URL=https://staging.your-domain.com
   PROD_URL=https://your-domain.com
   ```

2. Настройте доступ к базам данных:
   ```
   STAGING_DB_HOST=staging-db.your-domain.com
   STAGING_DB_PASSWORD=your-staging-password
   PROD_DB_HOST=prod-db.your-domain.com
   PROD_DB_PASSWORD=your-prod-password
   ```

### Ручной запуск мониторинга

Вы можете запустить проверки вручную:
1. Перейдите в Actions -> Monitoring & Alerts
2. Нажмите "Run workflow"
3. Выберите нужные параметры

## Устранение проблем

### Частые ошибки

1. **Poetry lock file conflicts**: 
   ```bash
   rm poetry.lock
   poetry lock
   ```

2. **Dependency version conflicts**:
   ```bash
   poetry update
   ```

3. **Docker build failures**:
   ```bash
   docker system prune -a
   ```

### Логи и отладка

- Логи CI/CD доступны в GitHub Actions
- Логи приложения доступны через `kubectl logs` или `docker logs`
- Для отладки используйте `poetry run python -m pdb your_script.py`

---

**Сделано с ❤️ для современной разработки**

Этот CI/CD пайплайн следует лучшим практикам DevOps и готов для production использования! 