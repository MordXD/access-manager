# Настройка CI/CD для Access Manager

Этот документ описывает полную настройку CI/CD пайплайна для проекта Access Manager.

## Обзор архитектуры CI/CD

### Компоненты пайплайна

1. **Continuous Integration (CI)**
   - Линтинг и форматирование кода (Black, isort, flake8)
   - Запуск тестов с покрытием кода
   - Сканирование безопасности (Safety, GitLeaks)
   - Сборка и тестирование Docker образов
   - Интеграционные тесты

2. **Continuous Deployment (CD)**
   - Автоматический деплой в Staging (ветка develop)
   - Ручной деплой в Production (ветка main)
   - Деплой через Kubernetes (Helm)
   - Деплой через Docker Compose
   - Автоматические релизы по тегам

3. **Мониторинг и алерты**
   - Health checks каждые 5 минут
   - Проверка производительности
   - Мониторинг SSL сертификатов
   - Проверка резервных копий

## Настройка GitHub Secrets

Для корректной работы пайплайнов необходимо настроить следующие секреты в GitHub:

### Docker Hub
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password-or-token
```

### Kubernetes (если используется)
```
STAGING_KUBECONFIG=base64-encoded-kubeconfig-for-staging
PROD_KUBECONFIG=base64-encoded-kubeconfig-for-production
```

### База данных
```
STAGING_DB_HOST=staging-db-host
STAGING_DB_PASSWORD=staging-db-password
PROD_DB_HOST=production-db-host
PROD_DB_PASSWORD=production-db-password
```

### URLs приложений
```
STAGING_URL=https://staging-access-manager.example.com
PROD_URL=https://access-manager.example.com
```

### Деплой через SSH (для Docker Compose)
```
DEPLOY_HOST=your-server-ip
DEPLOY_USER=deploy-user
DEPLOY_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
DEPLOY_PORT=22
```

### Переменные приложения
```
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:password@host:5432/db
POSTGRES_PASSWORD=your-postgres-password
```

### Уведомления
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## Настройка окружений в GitHub

### Создание окружений

1. Перейдите в Settings → Environments в вашем GitHub репозитории
2. Создайте следующие окружения:
   - `staging` - для тестового окружения
   - `production` - для продакшн окружения
   - `docker-compose` - для деплоя через Docker Compose

### Настройка правил защиты

Для production окружения рекомендуется настроить:
- **Required reviewers** - обязательное подтверждение деплоя
- **Wait timer** - задержка перед деплоем
- **Deployment branches** - ограничение на ветки (только main)

## Структура пайплайнов

### CI Pipeline (.github/workflows/ci.yml)

Запускается при:
- Push в ветки `main`, `develop`
- Pull Request в ветки `main`, `develop`

Этапы:
1. **lint-and-format** - проверка кода
2. **test** - запуск тестов с PostgreSQL
3. **security-scan** - сканирование безопасности
4. **docker-build** - сборка Docker образа
5. **integration-test** - интеграционные тесты

### CD Pipeline (.github/workflows/cd.yml)

Запускается при:
- Успешном завершении CI пайплайна
- Push тегов v*

Этапы:
1. **deploy-staging** - деплой в staging (develop ветка)
2. **deploy-production** - деплой в production (main ветка)
3. **docker-compose-deploy** - деплой через Docker Compose
4. **release** - создание GitHub релиза (по тегам)

### Monitoring Pipeline (.github/workflows/monitoring.yml)

Запускается:
- По расписанию каждые 5 минут
- Вручную через workflow_dispatch

Проверки:
- Здоровье API endpoints
- Подключение к базе данных
- Производительность (по запросу)
- SSL сертификаты
- Резервные копии

## Деплой в Kubernetes

### Требования

- Кластер Kubernetes
- Helm 3.x
- kubectl
- Ingress Controller (nginx)
- Cert-manager (для SSL)

### Установка

1. **Добавьте Helm репозиторий для PostgreSQL:**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

2. **Создайте namespace:**
```bash
kubectl create namespace staging
kubectl create namespace production
```

3. **Установите cert-manager (если не установлен):**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

4. **Настройте values файлы:**
   - `helm/access-manager/values-staging.yaml`
   - `helm/access-manager/values-production.yaml`

### Пример деплоя

```bash
# Staging
helm upgrade --install access-manager-staging ./helm/access-manager \
  --namespace staging \
  --values ./helm/access-manager/values-staging.yaml \
  --set image.tag=latest

# Production  
helm upgrade --install access-manager ./helm/access-manager \
  --namespace production \
  --values ./helm/access-manager/values-production.yaml \
  --set image.tag=v1.0.0
```

## Деплой через Docker Compose

### Подготовка сервера

1. **Установите Docker и Docker Compose:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Клонируйте репозиторий:**
```bash
git clone https://github.com/your-org/access-manager.git /opt/access-manager
cd /opt/access-manager
```

3. **Создайте .env файл:**
```bash
cp env.example .env
# Отредактируйте .env файл с production настройками
```

4. **Запустите приложение:**
```bash
docker-compose up -d
```

## Мониторинг и логирование

### Health Checks

Приложение предоставляет следующие endpoints для мониторинга:

- `GET /health` - проверка здоровья приложения
- `GET /metrics` - метрики в формате Prometheus

### Настройка Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'access-manager'
    static_configs:
      - targets: ['access-manager:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Настройка Grafana

Импортируйте dashboard для мониторинга FastAPI приложений или создайте собственный с метриками:

- `access_manager_users_total`
- `access_manager_roles_total`
- `access_manager_permissions_total`
- `access_manager_cpu_usage_percent`
- `access_manager_memory_usage_percent`

## Резервное копирование

### Автоматическое резервное копирование БД

В Kubernetes создается CronJob для ежедневного резервного копирования:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"  # Каждый день в 2:00
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - pg_dump $DATABASE_URL | gzip > /backup/backup-$(date +%Y%m%d).sql.gz
```

### Восстановление из резервной копии

```bash
# Восстановление из backup файла
gunzip -c backup-20240115.sql.gz | psql $DATABASE_URL
```

## Безопасность

### Сканирование уязвимостей

CI пайплайн включает:

1. **Safety** - проверка Python зависимостей
2. **GitLeaks** - поиск секретов в коде
3. **Docker Scout** - сканирование Docker образов

### Рекомендации по безопасности

1. Регулярно обновляйте зависимости
2. Используйте strong секретные ключи
3. Включите SSL/TLS для всех соединений
4. Ограничьте доступ к API с помощью IP whitelist
5. Настройте rate limiting
6. Используйте мониторинг безопасности

## Отладка проблем

### Частые проблемы

1. **Ошибки сборки Docker образа**
   - Проверьте Dockerfile
   - Убедитесь что все зависимости указаны в pyproject.toml

2. **Ошибки подключения к БД**
   - Проверьте DATABASE_URL
   - Убедитесь что PostgreSQL доступен
   - Проверьте миграции Alembic

3. **Ошибки деплоя в Kubernetes**
   - Проверьте kubeconfig
   - Убедитесь что namespace существует
   - Проверьте Helm values

4. **Проблемы с мониторингом**
   - Проверьте health endpoint
   - Убедитесь что все зависимости доступны

### Логи

```bash
# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/access-manager -n production

# GitHub Actions
# Проверьте вкладку Actions в репозитории
```

## Rollback

### Kubernetes (Helm)

```bash
# Откат к предыдущей версии
helm rollback access-manager -n production

# Откат к конкретной версии
helm rollback access-manager 3 -n production
```

### Docker Compose

```bash
# Откат к предыдущему образу
docker-compose down
git checkout previous-commit
docker-compose up -d
```

## Масштабирование

### Горизонтальное масштабирование

В Kubernetes автоматически настроен HPA:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Вертикальное масштабирование

Увеличьте ресурсы в values.yaml:

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

## Поддержка

Для получения помощи:

1. Проверьте логи приложения
2. Изучите документацию по ошибке
3. Создайте Issue в GitHub репозитории
4. Обратитесь к команде DevOps 