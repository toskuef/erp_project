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
CMD ["gunicorn", "core.wsgi:application", "--bind", "0:8000"]
#CMD ["uvicorn", "core.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["gunicorn", "api_yamdb.wsgi:application", "uvicorn.workers.UvicornWorker"]
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
#daphne -b 0.0.0.0 -p 8000 core.asgi:application

