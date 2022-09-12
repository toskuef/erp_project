FROM python:3.8-slim

# Создать директорию вашего приложения.
RUN mkdir /app

# Скопировать с локального компьютера файл зависимостей
# в директорию /app.
COPY requirements.txt /app

# Выполнить установку зависимостей внутри контейнера.
RUN pip install --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install -r /app/requirements.txt --no-cache-dir



# Скопировать содержимое директории /api_yamdb c локального компьютера
# в директорию /app.
COPY ../ /app

# Сделать директорию /app рабочей директорией.
WORKDIR /app

# Выполнить запуск сервера разработки при старте контейнера.
CMD ["gunicorn", "erp_core.wsgi:application", "--bind", "0:8000" ]