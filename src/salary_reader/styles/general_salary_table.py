GTS_TABLE_STYLE = u"""
/* База таблицы */
QTableWidget {
    background-color: rgba(255, 255, 255, 30);
    border: 1px solid rgba(255, 255, 255, 40);
    border-radius: 7px;
    gridline-color: rgba(255, 255, 255, 70);
    color: white;
}

/* Выделение */
QTableWidget::item:selected {
    background-color: rgba(255, 255, 255, 120);
    font-weight: bold;
    color: white;
}

/* Контейнер заголовка — прозрачный, всё рисуют секции */
QHeaderView {
    background: transparent;
    color: white;
}

/* Секции заголовка — именно они и видны */
QHeaderView::section {
    background-color: rgba(255, 255, 255, 28);
    color: white;
    border: 1px solid rgba(255, 255, 255, 40);
    padding: 6px;
}

/* Скругления краёв у первой и последней секции горизонтального заголовка */
QHeaderView::section:horizontal:first {
    border-top-left-radius: 7px;
}
QHeaderView::section:horizontal:last {
    border-top-right-radius: 7px;
}

/* Уголок (ячейка в левом верхнем углу) */
QTableCornerButton::section {
    background-color: rgba(255, 255, 255, 28);
    border: none;
    border-top-left-radius: 7px;
}

/* Доп. фиксы */
QTableView {
    border-radius: 7px;
    gridline-color: rgba(255, 255, 255, 70);
}
"""
