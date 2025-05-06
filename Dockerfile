# Базовый образ с Python
FROM python:3.12-alpine as base

# Установка переменных окружения
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# Установка необходимых системных зависимостей
RUN apk update && apk add gcc libffi-dev g++ bash

# Установка рабочего каталога
WORKDIR /code

# Этап сборки
FROM base as builder

# Установка переменных окружения для pip
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Установка Poetry
RUN pip install "poetry"

# Копирование файлов конфигурации зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей в виртуальное окружение
RUN poetry config virtualenvs.create false && poetry install --no-root

# Копирование всего кода приложения
COPY . .

# Сборка пакета (если необходимо)
RUN poetry build

# Финальный образ
FROM base as final

# Копирование зависимостей из этапа сборки
COPY --from=builder /code/dist /code/dist
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Установка собранного пакета
RUN pip install /code/dist/*.whl

# Опционально: установка рабочей директории для финального образа
WORKDIR /code

