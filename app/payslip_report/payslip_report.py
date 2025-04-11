import calendar
from datetime import date, datetime, timedelta
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

from app.drivers.attendances import AttendancesDataDriver
from app.models.control_models import get_employee_name_by_id

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))


class ReportGenerator:
    def __init__(self, parent):
        self.parent: AttendancesDataDriver = parent
        self.font_name = "DejaVuSans"

    def _group_by_month(self, rows):
        grouped = defaultdict(list)
        for row in rows:
            d = row['date']
            grouped[(d.year, d.month)].append(row)
        return grouped

    def _create_month_table(self, name, year, month, month_rows, date_from=None, date_to=None):
        # Определяем базовые параметры
        month_start = date(year, month, 1)
        num_days = calendar.monthrange(year, month)[1]
        month_end = date(year, month, num_days)

        # Валидация периода
        period = None
        if date_from and date_to:
            # Нормализуем порядок дат
            date_from, date_to = sorted([date_from, date_to])

            # Проверяем принадлежность к текущему месяцу
            if (date_from >= month_start and date_to <= month_end
                    and date_from.month == date_to.month):
                period = (date_from.day, date_to.day)

        # Определяем диапазон дней
        if period:
            start_day = max(1, period[0])
            end_day = min(num_days, period[1])
            days_range = range(start_day, end_day + 1)
            period_str = f"{date_from.strftime('%d.%m')}-{date_to.strftime('%d.%m.%Y')}"
        else:
            days_range = range(1, num_days + 1)
            period_str = f"{month:02d}/{year}"

        # Оптимизация: создаём словарь для быстрого доступа
        date_to_row = {r['date']: r for r in month_rows}

        # Подготовка стилей
        header_style = ParagraphStyle(
            'Header',
            fontName=self.font_name,
            fontSize=8,
            alignment=1,
            leading=9,
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

        # Формируем заголовок
        table_data = [
            [Paragraph(f"<b>{name}</b> - {period_str}", header_style)],
            ["Дата", "Тип смены", "Период", "ЗП"]
        ]

        salary_sum = 0
        full_days = 0
        partial_days = 0

        # Основной цикл обработки дней
        for day in days_range:
            current_date = date(year, month, day)
            row = date_to_row.get(current_date)

            # Логирование с проверкой существования ключа
            shift_type = row.get('shift_type', 'Нет смены') if row else 'Нет смены'
            logger.info(f"Тип смены {shift_type} {day}-го")
            # Считаем количество полных и неполных смен для футера
            match shift_type.lower():
                case "полная":
                    full_days += 1
                case "пол смены":
                    partial_days += 1
                case _:
                    pass

            # Формируем строку таблицы
            table_data.append([
                current_date.strftime("%d.%m.%Y"),
                row.get('shift_type', '') if row else "",
                row.get('period', '') if row else "",
                str(row['salary']) if row and 'salary' in row else ""
            ])

            # Суммируем зарплату с проверкой
            try:
                salary_sum += int(row['salary']) if row else 0
            except (KeyError, ValueError, TypeError):
                logger.error(f"Ошибка в данных зарплаты для {current_date}")

        # Добавляем итоговую строку
        table_data.append([
            'Итого:', 'Полных смен', 'Неполных', 'Сумма'
        ])
        table_data.append([
            '-', str(full_days), str(partial_days), str(salary_sum)
        ])

        return table_data

    def generate_payslip_report(self, employee_ids: list, date_from: datetime, date_to: datetime):
        """
        Генерация отчета по зарплате

        :param employee_ids: ID сотрудников
        :param date_from: Дата начала периода
        :param date_to: Дата конца периода
        :return:
        """
        all_tables = []
        for emp_id in employee_ids:
            name = get_employee_name_by_id(emp_id)
            logger.warning(f"Имя {name}")
            rows = self.parent.get_detailed_table_rows(emp_id)
            for (year, month), month_rows in self._group_by_month(rows).items():
                all_tables.append(
                    self._create_month_table(
                    name, year, month, month_rows, date_from, date_to
                    )
                )
        logger.debug(f"Начинаем формировать PDF...")
        pdf_filename = "payslip_report.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        c.setFont(self.font_name, 7)  # Устанавливаем шрифт для всего документа

        # Размеры таблицы
        table_width = 70 * mm
        table_height = 140 * mm

        # Позиции на странице для таблиц
        positions = [
            (1 * mm, A4[1] - 10 * mm - table_height),  # Верх-лево
            (71 * mm, A4[1] - 10 * mm - table_height),  # Верх-центр
            (141 * mm, A4[1] - 10 * mm - table_height),  # Верх-право
            (1 * mm, A4[1] - 155 * mm - table_height),  # Низ-лево
            (71 * mm, A4[1] - 155 * mm - table_height),  # Низ-центр
            (141 * mm, A4[1] - 155 * mm - table_height)  # Низ-право
        ]

        first_page = True
        for i in range(0, len(all_tables), 6):
            if not first_page:
                c.showPage()
            else:
                first_page = False

            page_tables = all_tables[i:i + 6]

            logger.debug(f"Формируем страницу {i//6+1} из {len(all_tables)//6}")
            for idx, table_data in enumerate(page_tables):
                logger.debug(f"Формируем таблицу {idx+1} из {len(page_tables)}")
                t = Table(
                    table_data,
                    colWidths=[14 * mm, 25 * mm, 15 * mm, 9 * mm],
                    # Первая строка – высота 8 мм, остальные – по 5 мм
                    rowHeights=[8 * mm] + [4 * mm] * (len(table_data) - 1)
                )
                style = TableStyle([
                    ('SPAN', (0, 0), (-1, 0)),
                    #('SPAN', (0, -1), (-1, -1)),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.transparent),
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 1), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
                    ('BACKGROUND', (0, -2), (-1, -2), colors.lightgrey),
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

    def create_payslip_pdf(self, from_date: datetime, to_date: datetime) -> None:
        """
        Передает список id сотрудников из parent (AttendancesDataDriver) в generate_payslip_report.

        В AttendancesDataDriver.employees_attendances.attendances содержатся "отчищенные" явки сотрудников,
        в виде списка словарей, где ключи это id сотрудника.
        """
        try:
            logger.info(f"Строим отчет по зарплате за период {from_date} - {to_date}")

            employee_ids = []
            for row_num in range(self.parent.general_table.rowCount()):
                employee_id = self.parent.general_table.item(row_num, 16).text()
                employee_ids.append(employee_id)

            if not employee_ids:
                logger.warning("Нет сотрудников для отчета")
                return
            else:
                logger.info(f"Сотрудники для отчета: {employee_ids}")
                logger.info(f"Генерируем отчет...")
            self.generate_payslip_report(employee_ids, from_date, to_date)

        except PermissionError as e:
            logger.exception(e)
            raise
        except Exception as e:
            logger.exception(e)
            raise
