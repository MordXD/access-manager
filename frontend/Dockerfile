# frontend/Dockerfile

# Этап 1: Сборка приложения
FROM node:18-alpine as builder
WORKDIR /app

# Копируем package.json и lock-файл
COPY package.json package-lock.json ./
# Если используешь yarn:
# COPY package.json yarn.lock ./
# Если используешь pnpm:
# COPY package.json pnpm-lock.yaml ./


# Устанавливаем зависимости (выбери свой менеджер пакетов)
RUN npm install
# RUN yarn install
# RUN pnpm install --frozen-lockfile # pnpm рекомендуется --frozen-lockfile в CI/CD

# Копируем остальные файлы проекта
COPY . .

# Собираем приложение для продакшена
RUN npm run build

# Этап 2: Запуск приложения с использованием Nginx
FROM nginx:1.25-alpine

# Копируем собранные статические файлы из этапа 'builder'
COPY --from=builder /app/dist /usr/share/nginx/html

# (Опционально) Если нужна кастомная конфигурация Nginx (например, для React Router)
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# Пример nginx.conf для SPA с React Router:
# server {
#   listen 80;
#   server_name localhost;
#
#   root /usr/share/nginx/html;
#   index index.html;
#
#   location / {
#     try_files $uri $uri/ /index.html;
#   }
# }


# Открываем порт 80, на котором будет слушать Nginx
EXPOSE 80

# Команда по умолчанию для запуска Nginx
CMD ["nginx", "-g", "daemon off;"]