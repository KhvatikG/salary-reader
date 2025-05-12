GTS_TABLE_STYLE = u"""
/* Основной стиль таблицы */
QTableWidget {
background-color: rgba(255, 255, 255, 30);
border-radius: 7px;
gridline-color: rgba(255, 255, 255, 70);
color: white;
}

/* Стиль выделенных элементов */
QTableWidget::item:selected {
background-color: rgba(255, 255, 255, 120);
font-weight: bold;
color: white;
}

/* Стиль заголовков */
QHeaderView {
background-color: rgba(255, 255, 255, 30);
color: white;
border-radius: 5px;
}
/* Фикс для скругления углов таблицы */
QTableView {
border-radius: 7px;
gridline-color: rgba(255, 255, 255, 70);
}
"""