# CI/CD для Access Manager 🚀

Полноценный CI/CD пайплайн для FastAPI приложения управления доступом с автоматическим тестированием, безопасностью и мониторингом.

## 🌟 Особенности

- ✅ **Непрерывная интеграция**: автоматическое тестирование, линтинг, сканирование безопасности
- 🚀 **Непрерывная доставка**: автоматический деплой в staging/production  
- 🐳 **Контейнеризация**: Docker и Kubernetes поддержка
- 📊 **Мониторинг**: Health checks, метрики Prometheus, алерты
- 🔒 **Безопасность**: сканирование уязвимостей, проверка секретов
- 📈 **Масштабируемость**: HPA, load balancing, резервное копирование

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

---

**Сделано с ❤️ для современной разработки**

Этот CI/CD пайплайн следует лучшим практикам DevOps и готов для production использования! 