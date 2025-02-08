import calendar
from datetime import date
from collections import defaultdict

from loguru import logger
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import subprocess

from app.models.control_models import get_employee_name_by_id

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


class ReportGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.font_name = "DejaVuSans"

    def _group_by_month(self, rows):
        grouped = defaultdict(list)
        for row in rows:
            d = row['date']
            grouped[(d.year, d.month)].append(row)
        return grouped

    def _create_month_table(self, name, year, month, month_rows):
        num_days = calendar.monthrange(year, month)[1]
        header_style = ParagraphStyle(
            'Header',
            fontName=self.font_name,
            fontSize=8,
            alignment=1,
            leading=9,
            #spaceAfter=6,
            spaceBefore=1*mm,
            spaceAfter=2*mm
        )

        footer_style = ParagraphStyle(
            'Footer',
            fontName=self.font_name,
            fontSize=8,
            alignment=2,
            leading=9,
        )

        table_data = [
            [Paragraph(f"<b>{name}</b> - {month:02d}/{year}", header_style)],
            ["Дата", "Тип смены", "Период", "ЗП"]
        ]

        salary_sum = 0  # Переменная для накопления итога по зп
        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            row = next((r for r in month_rows if r['date'] == current_date), None)
            logger.warning(f"Тип смены {row['shift_type'] if row else 'Нет типа'}")
            table_data.append([
                current_date.strftime("%d.%m.%Y"),
                row['shift_type'] if row else "",
                row['period'] if row else "",
                str(row['salary']) if row else ""
            ])
            salary_sum += int(row['salary']) if row else 0
        table_data.append([
            Paragraph(f"Итого: {salary_sum}", footer_style),
        ])
        return table_data

    def generate_payslip_report(self, employee_ids):
        all_tables = []
        for emp_id in employee_ids:
            name = get_employee_name_by_id(emp_id)
            logger.warning(f"Имя {name}")
            rows = self.parent.get_detailed_table_rows(emp_id)
            for (year, month), month_rows in self._group_by_month(rows).items():
                all_tables.append(self._create_month_table(name, year, month, month_rows))

        pdf_filename = "payslip_report.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        c.setFont(self.font_name, 7)  # Устанавливаем шрифт для всего документа

        # Размеры таблицы
        table_width = 70 * mm
        table_height = 130 * mm

        # Позиции на странице для таблиц
        positions = [
            (1 * mm, A4[1] - 10 * mm - table_height),  # Верх-лево
            (71 * mm, A4[1] - 10 * mm - table_height),  # Верх-центр
            (141 * mm, A4[1] - 10 * mm - table_height),  # Верх-право
            (1 * mm, A4[1] - 150 * mm - table_height),  # Низ-лево
            (71 * mm, A4[1] - 150 * mm - table_height),  # Низ-центр
            (141 * mm, A4[1] - 150 * mm - table_height)  # Низ-право
        ]

        first_page = True
        for i in range(0, len(all_tables), 6):
            if not first_page:
                c.showPage()
            else:
                first_page = False

            page_tables = all_tables[i:i + 6]

            for idx, table_data in enumerate(page_tables):
                t = Table(
                    table_data,
                    colWidths=[14 * mm, 25 * mm, 15 * mm, 9 * mm],
                    # Первая строка – высота 8 мм, остальные – по 5 мм
                    rowHeights=[8 * mm] + [4 * mm] * (len(table_data) - 1)
                )
                style = TableStyle([
                    ('SPAN', (0, 0), (-1, 0)),
                    ('SPAN', (0, -1), (-1, -1)),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 1), (-1, -2), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
                    ('LEADING', (0, 0), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 0.5*mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5*mm),
                ])
                t.setStyle(style)

                x, y = positions[idx]
                t.wrapOn(c, table_width, table_height)
                t.drawOn(c, x, y)

        c.save()

        if os.name == 'nt':
            os.startfile(pdf_filename)
        else:
            subprocess.run(['xdg-open', pdf_filename])

        return pdf_filename

    def create_payslip_pdf(self) -> None:
        """
        Передает список id сотрудников из parent (AttendancesDataDriver) в generate_payslip_report.

        В AttendancesDataDriver.employees_attendances.attendances содержатся "отчищенные" явки сотрудников,
        в виде списка словарей, где ключи это id сотрудника.
        """
        try:
            employee_ids = [emp_id for emp_id in self.parent.employees_attendances.attendances]
            self.generate_payslip_report(employee_ids)
        except PermissionError as e:
            logger.exception(e)
            raise
        except Exception as e:
            logger.exception(e)
            raise
