DEPARTMENT_COMBO_BOX = u"""
    QComboBox {
        background-color: rgba(255, 255, 255, 30);
        border: 1px solid rgba(255, 255, 255, 40);
        border-radius: 7px;
        color: white;
        font-weight: bold;
        font-size: 16pt;
        padding-left: 10px;
        text-align: center;
    }
    
    /* Скрываем выпадающую стрелку */
    QComboBox::drop-down {
        width: 0;
        border: 0;
        background: transparent;
    }
    
    /* Центрируем текст в выпадающем списке */
    QComboBox QAbstractItemView {
        text-align: center;
        background-color: qlineargradient(spread:pad, x1:1, y1:1, x2:0, y2:0, stop:0 rgba(81, 0, 135, 255), stop:0.427447 rgba(41, 61, 132, 235), stop:1 rgba(155, 79, 165, 255));
        color: white;
    }
    
    /* Фикс для выравнивания основного текста */
    QComboBox QLineEdit {
        text-align: center;
        padding: 0;
        margin: 0;
    }

"""