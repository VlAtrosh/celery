import os
from dotenv import load_dotenv

load_dotenv()

# Настройки Celery
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')

BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Настройки расчета зарплаты
TAX_RATE = 0.13  # НДФЛ 13%
PENSION_RATE = 0.22  # Пенсионные отчисления
SOCIAL_RATE = 0.051  # Социальное страхование