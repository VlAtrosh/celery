"""
Настройка периодических задач (Celery Beat)
Запуск: celery -A tasks beat --loglevel=info
"""

from celery.schedules import crontab
from tasks import app

# Настройка расписания
app.conf.beat_schedule = {
    # Ежемесячный расчет зарплаты (1-го числа в 9:00)
    'monthly-payroll': {
        'task': 'monthly_payroll_run',
        'schedule': crontab(day_of_month='1', hour='9', minute='0'),
        'args': (),
    },
    
    # Ежедневная проверка посещаемости (в 8:30)
    'daily-attendance': {
        'task': 'daily_attendance_check',
        'schedule': crontab(hour='8', minute='30'),
        'args': (),
    },
    
    # Расчет бонусов каждую пятницу в 17:00
    'weekly-bonus': {
        'task': 'calculate_bonuses',  # Нужно создать эту задачу
        'schedule': crontab(day_of_week='5', hour='17', minute='0'),
        'args': (),
    },
}

print("Периодические задачи настроены:")
for task_name, schedule in app.conf.beat_schedule.items():
    print(f"  {task_name}: {schedule['schedule']}")