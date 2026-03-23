"""
Главный демонстрационный скрипт
"""

import time
from tasks import (
    calculate_employee_salary,
    send_notification,
    calculate_with_retry,
    generate_payslip_pdf,
    app  # добавим импорт app
)
from celery import chain, group, chord
import sys


def demonstrate_basic_usage():
    """Демонстрация 1: Базовое использование"""
    print("\n" + "="*60)
    print("1. БАЗОВОЕ ИСПОЛЬЗОВАНИЕ")
    print("="*60)
    
    try:
        print("Отправка задачи на расчет зарплаты...")
        result = calculate_employee_salary.delay(
            employee_id=101,
            hours=160,
            rate=250
        )
        
        print(f"✅ Задача отправлена. ID: {result.id}")
        print("⏳ Ожидание завершения...")
        
        salary_data = result.get(timeout=30)
        
        print(f"\n✅ Результат:")
        print(f"   Сотрудник: {salary_data['employee_id']}")
        print(f"   Начислено: {salary_data['gross_salary']} руб.")
        print(f"   Налог: {salary_data['tax']} руб.")
        print(f"   К выплате: {salary_data['net_salary']} руб.")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def demonstrate_chain():
    """Демонстрация 2: Цепочки задач"""
    print("\n" + "="*60)
    print("2. ЦЕПОЧКИ ЗАДАЧ (Chain)")
    print("="*60)
    
    try:
        workflow = chain(
            calculate_employee_salary.s(employee_id=102, hours=150, rate=300),
            send_notification.s('employee@company.com')
        )
        
        print("Запуск цепочки задач...")
        result = workflow.apply_async()
        
        final_result = result.get(timeout=45)
        print(f"✅ Результат цепочки: {final_result}")
        
    except Exception as e:
        print(f"❌ Ошибка в цепочке: {e}")


def demonstrate_group():
    """Демонстрация 3: Группа задач"""
    print("\n" + "="*60)
    print("3. ГРУППА ЗАДАЧ (Group)")
    print("="*60)
    
    try:
        employees = [
            (103, 160, 280),
            (104, 168, 320),
            (105, 152, 270),
            (106, 176, 350)
        ]
        
        jobs = group(
            calculate_employee_salary.s(emp_id, hours, rate)
            for emp_id, hours, rate in employees
        )
        
        print(f"Запуск группы из {len(employees)} задач...")
        result = jobs.apply_async()
        
        results = result.get(timeout=60)
        print("\n✅ Результаты группы:")
        total = 0
        for res in results:
            print(f"   Сотрудник {res['employee_id']}: {res['net_salary']} руб.")
            total += res['net_salary']
        print(f"\n   Общая сумма выплат: {total:.2f} руб.")
        
    except Exception as e:
        print(f"❌ Ошибка в группе: {e}")


def demonstrate_chord():
    """Демонстрация 4: Хорд (Chord) - группа с объединяющей задачей"""
    print("\n" + "="*60)
    print("4. ХОРД (Chord) - группа с объединяющей задачей")
    print("="*60)
    
    try:
        # Данные сотрудников
        employees_data = [
            (201, 160, 250),
            (202, 168, 280),
            (203, 152, 300),
            (204, 176, 320)
        ]
        
        # Создаем подзадачи
        calculations = []
        for emp_id, hours, rate in employees_data:
            calculations.append(calculate_employee_salary.s(emp_id, hours, rate))
        
        # Создаем задачу для агрегации прямо здесь и регистрируем её
        @app.task(name='aggregate_salaries_task')
        def aggregate_salaries_task(results):
            total = sum(r['net_salary'] for r in results)
            return {
                'total_payroll': round(total, 2),
                'average_salary': round(total / len(results), 2),
                'employee_count': len(results),
            }
        
        print("Запуск расчета зарплаты отдела...")
        
        # Создаем хорд
        chord_result = chord(calculations)(aggregate_salaries_task.s())
        final_result = chord_result.get(timeout=60)
        
        print(f"\n✅ Результат расчета отдела:")
        print(f"   Всего сотрудников: {final_result['employee_count']}")
        print(f"   Общий фонд: {final_result['total_payroll']} руб.")
        print(f"   Средняя зарплата: {final_result['average_salary']} руб.")
        
        # Показываем детали
        print(f"\n📊 Детали расчета:")
        for emp_id, hours, rate in employees_data:
            gross = hours * rate
            net = gross - (gross * 0.13)
            print(f"   Сотрудник {emp_id}: {hours}ч × {rate}р = {gross:.0f}р → {net:.0f}р")
        
    except Exception as e:
        print(f"❌ Ошибка в хорде: {e}")


def demonstrate_error_handling():
    """Демонстрация 5: Обработка ошибок"""
    print("\n" + "="*60)
    print("5. ОБРАБОТКА ОШИБОК И АВТОМАТИЧЕСКИЕ ПОВТОРЫ")
    print("="*60)
    
    try:
        print("Запуск задачи с некорректными данными...")
        result = calculate_with_retry.delay(
            employee_id=999,
            hours=-10,
            rate=300
        )
        
        print("⏳ Задача будет пытаться выполниться 3 раза...")
        
        try:
            res = result.get(timeout=30)
            print(f"\n✅ Успешно: {res}")
        except Exception as e:
            print(f"\n⚠️ Задача не удалась: {e}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def demonstrate_pdf_generation():
    """Демонстрация 6: Генерация PDF"""
    print("\n" + "="*60)
    print("6. ГЕНЕРАЦИЯ PDF (длительные операции)")
    print("="*60)
    
    try:
        print("Сначала рассчитываем зарплату...")
        salary_result = calculate_employee_salary.delay(
            employee_id=107,
            hours=160,
            rate=350
        )
        
        salary_data = salary_result.get(timeout=30)
        print(f"✅ Зарплата рассчитана: {salary_data['net_salary']} руб.")
        
        print("Генерация PDF расчетного листка...")
        pdf_result = generate_payslip_pdf.delay(salary_data)
        pdf_file = pdf_result.get(timeout=60)
        print(f"✅ PDF создан: {pdf_file}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ CELERY                     ║
    ║     Расчет зарплат с использованием асинхронных задач    ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print("ℹ️  Убедитесь, что запущен Celery worker:")
    print("   celery -A tasks worker --loglevel=info\n")
    
    input("Нажмите Enter, чтобы начать демонстрацию...")
    
    print("\n🔍 Проверка подключения...")
    try:
        conn = app.connection()
        conn.connect()
        print("✅ Успешное подключение к Redis!")
        conn.release()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        sys.exit(1)
    
    # Запуск демонстраций
    try:
        demonstrate_basic_usage()
        demonstrate_chain()
        demonstrate_group()
        demonstrate_chord()
        demonstrate_error_handling()
        demonstrate_pdf_generation()
        
        print("\n" + "="*60)
        print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА! 🎉")
        print("="*60)
        print("\n📁 Создан PDF файл: payslip_107.pdf")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")