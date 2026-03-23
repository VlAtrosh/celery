"""
Запуск Flower для мониторинга Celery
Запуск: python monitoring.py
Или: celery -A tasks flower --port=5555
"""

import subprocess
import webbrowser
import time

def start_flower_monitoring():
    """
    Запуск Flower для визуального мониторинга задач
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     ЗАПУСК FLOWER - ВЕБ-ИНТЕРФЕЙС ДЛЯ CELERY             ║
    ║     Откроется браузер с панелью мониторинга              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Запуск Flower
        process = subprocess.Popen(
            ['celery', '-A', 'tasks', 'flower', '--port=5555'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("Flower запущен на http://localhost:5555")
        time.sleep(2)
        
        # Открыть браузер
        webbrowser.open('http://localhost:5555')
        
        print("\nFlower предоставляет:")
        print("  • Статистика по воркерам")
        print("  • Список всех задач")
        print("  • Графики выполнения")
        print("  • Возможность повторного запуска задач")
        print("  • Просмотр результатов")
        
        print("\nНажмите Ctrl+C для остановки...")
        process.wait()
        
    except KeyboardInterrupt:
        print("\nОстановка Flower...")
        process.terminate()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    start_flower_monitoring()