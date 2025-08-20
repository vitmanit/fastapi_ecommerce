# Базовый образ
FROM python:3.12.0

# Переменные окружения
ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создаем пользователя и группу
RUN mkdir -p $APP_HOME \
 && groupadd -r fast \
 && useradd -r -g fast fast

# Копируем весь проект из корня в /home/fast/app
COPY . $APP_HOME

# Меняем рабочую директорию
WORKDIR $APP_HOME

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R fast:fast .

# Смена пользователя
USER fast