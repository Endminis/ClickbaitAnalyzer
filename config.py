import os

"""
Конфігурація підключення до бази даних.
Тут задайте параметри вашої СУБД перед запуском додатку.
"""
DB_CONFIG = {
    # Хост сервера бази даних, наприклад 'localhost' або IP-адреса
    'host': 'localhost',
    # Порт сервера, зазвичай 5432 для PostgreSQL
    'port': 5432,
    # Ім’я користувача бази даних
    'user': 'postgres',
    # Пароль користувача
    'password': '123456',
    # Назва бази даних
    'database': 'clickbait_db'
}

SECRET_KEY = os.urandom(32)

# Назва трансформерного енкодера (шлях на HuggingFace)
ENCODER_NAME = "Goader/liberta-large-v2"

# Назва класифікатора
CLASSIFIER_NAME = "logreg"

# Директорія, де лежать ваші збережені моделі
MODEL_DIR = "models/"