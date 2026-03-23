import time
import logging
from typing import Dict, List
from celery import Celery
from config import BROKER_URL, RESULT_BACKEND, TAX_RATE

# Импорты для PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

# Создание Celery приложения
app = Celery(
    'salary_tasks',
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

# Конфигурация Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
)


# ============================================
# ВСТРОЕННАЯ ФУНКЦИЯ ДЛЯ ГЕНЕРАЦИИ PDF
# ============================================
def generate_payslip_internal(employee_data, filepath):
    """Генерация PDF расчетного листка"""
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=20,
        alignment=1,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30
    )
    
    story = []
    
    story.append(Paragraph("PAYSLIP", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    emp_data = [
        ["Employee ID:", str(employee_data['employee_id'])],
        ["Period:", "March 2026"],
        ["Position:", "Developer"]
    ]
    
    emp_table = Table(emp_data, colWidths=[2*inch, 3*inch])
    emp_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 0.3*inch))
    
    salary_table_data = [
        ["Description", "Amount (RUB)"],
        ["Gross Salary", f"{employee_data['gross_salary']:.2f}"],
        ["Tax (13%)", f"{employee_data['tax']:.2f}"],
        ["NET PAY", f"{employee_data['net_salary']:.2f}"]
    ]
    
    salary_table = Table(salary_table_data, colWidths=[3*inch, 2*inch])
    salary_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4fd')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#e67e22')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(salary_table)
    story.append(Spacer(1, 0.5*inch))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        textColor=colors.grey
    )
    story.append(Paragraph("Generated automatically by Salary System", footer_style))
    
    doc.build(story)
    return filepath


# ============================================
# CELERY ЗАДАЧИ
# ============================================

@app.task(name='calculate_employee_salary')
def calculate_employee_salary(employee_id: int, hours: float, rate: float) -> Dict:
    """Расчет зарплаты одного сотрудника"""
    print(f"Начинаем расчет для сотрудника {employee_id}")
    time.sleep(2)
    
    gross = hours * rate
    tax = gross * TAX_RATE
    net = gross - tax
    
    result = {
        'employee_id': employee_id,
        'hours': hours,
        'rate': rate,
        'gross_salary': round(gross, 2),
        'tax': round(tax, 2),
        'net_salary': round(net, 2),
        'status': 'completed'
    }
    
    print(f"Расчет для сотрудника {employee_id} завершен. Итого: {net:.2f}")
    return result


@app.task(name='send_notification')
def send_notification(salary_data: Dict, employee_email: str) -> Dict:
    """Отправка уведомления"""
    print(f"Отправка уведомления на {employee_email}")
    time.sleep(1)
    
    return {
        'to': employee_email,
        'subject': 'Расчет зарплаты',
        'body': f"Ваша зарплата составила {salary_data['net_salary']} руб.",
        'status': 'sent'
    }


@app.task(name='calculate_with_retry', max_retries=3)
def calculate_with_retry(employee_id: int, hours: float, rate: float) -> Dict:
    """Расчет с повтором при ошибке"""
    try:
        print(f"Попытка расчета для {employee_id}")
        
        if hours <= 0:
            raise ValueError(f"Некорректное количество часов: {hours}")
        
        gross = hours * rate
        tax = gross * TAX_RATE
        net = gross - tax
        
        return {
            'employee_id': employee_id,
            'net_salary': round(net, 2),
        }
        
    except Exception as exc:
        print(f"Ошибка для {employee_id}, будет повтор...")
        raise calculate_with_retry.retry(exc=exc, countdown=5)


@app.task(name='generate_payslip_pdf')
def generate_payslip_pdf(employee_data: Dict) -> str:
    """Генерация PDF"""
    filename = f"payslip_{employee_data['employee_id']}.pdf"
    filepath = f"C:\\Users\\Vlado\\OneDrive\\Рабочий стол\\calary\\{filename}"
    
    print(f"Генерация PDF для сотрудника {employee_data['employee_id']}")
    generate_payslip_internal(employee_data, filepath)
    
    print(f"✅ PDF создан: {filename}")
    return filename