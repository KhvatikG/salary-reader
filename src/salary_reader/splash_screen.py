"""
Splash Screen с анимированными точками для SalaryReader
"""
import sys
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from loguru import logger


class AnimatedSplashScreen(QSplashScreen):
    """Splash screen с анимированными точками загрузки"""
    
    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Настройки анимации
        self.dots_count = 0
        self.max_dots = 3
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_dots)
        self.animation_timer.start(300)  # Обновление каждые 300мс для более плавной анимации
        
        # Настройки текста
        self.loading_text = "Загрузка"
        self.version_text = ""
        
        # Центрируем splash screen
        self.center_splash()
        
        # Устанавливаем минимальный размер
        self.setMinimumSize(400, 300)
        
    def center_splash(self):
        """Центрирует splash screen на экране"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def update_dots(self):
        """Обновляет количество точек в анимации"""
        self.dots_count = (self.dots_count + 1) % (self.max_dots + 1)
        self.update()
    
    def set_version(self, version_text):
        """Устанавливает текст версии"""
        self.version_text = version_text
        self.update()
    
    def drawContents(self, painter):
        """Отрисовывает содержимое splash screen"""
        super().drawContents(painter)
        
        # Получаем размеры splash screen
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        
        # Настройки шрифта для основного текста
        main_font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(main_font)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        # Рисуем текст "Загрузка" с точками
        dots = "." * self.dots_count
        loading_text = f"{self.loading_text}{dots}"
        
        # Вычисляем позицию основного текста (центрируем)
        text_rect = painter.fontMetrics().boundingRect(loading_text)
        text_x = center_x - text_rect.width() // 2
        text_y = center_y + 70
        
        # Добавляем тень для лучшей читаемости
        painter.setPen(QPen(QColor(0, 0, 0, 100), 3))
        painter.drawText(text_x + 1, text_y + 1, loading_text)
        
        # Основной текст
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(text_x, text_y, loading_text)
        
        # Рисуем версию, если она задана
        if self.version_text:
            version_font = QFont("Arial", 10)
            painter.setFont(version_font)
            painter.setPen(QPen(QColor(180, 180, 180), 1))
            
            version_rect = painter.fontMetrics().boundingRect(self.version_text)
            version_x = center_x - version_rect.width() // 2
            version_y = center_y + 90
            
            # Тень для версии
            painter.setPen(QPen(QColor(0, 0, 0, 80), 2))
            painter.drawText(version_x + 1, version_y + 1, self.version_text)
            
            # Основной текст версии
            painter.setPen(QPen(QColor(180, 180, 180), 1))
            painter.drawText(version_x, version_y, self.version_text)


def create_splash_screen(background_image_path: str, version_text: str = "") -> AnimatedSplashScreen:
    """
    Создает и настраивает splash screen
    
    Args:
        background_image_path: Путь к фоновому изображению
        version_text: Текст версии для отображения
        
    Returns:
        AnimatedSplashScreen: Настроенный splash screen
    """
    try:
        # Загружаем фоновое изображение
        pixmap = QPixmap(background_image_path)
        if pixmap.isNull():
            logger.warning(f"Не удалось загрузить изображение: {background_image_path}")
            # Создаем простой фон если изображение не загрузилось
            pixmap = QPixmap(400, 300)
            pixmap.fill(QColor(50, 50, 50))
        
        # Создаем splash screen
        splash = AnimatedSplashScreen(pixmap)
        splash.set_version(version_text)
        
        logger.info("Splash screen создан успешно")
        return splash
        
    except Exception as e:
        logger.error(f"Ошибка при создании splash screen: {e}")
        # Возвращаем простой splash screen в случае ошибки
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(50, 50, 50))
        splash = AnimatedSplashScreen(pixmap)
        return splash


def show_splash_screen(app: QApplication, background_path: str, version_text: str = "", 
                      min_display_time: int = 1000) -> AnimatedSplashScreen:
    """
    Показывает splash screen и возвращает его для дальнейшего управления
    
    Args:
        app: QApplication instance
        background_path: Путь к фоновому изображению
        version_text: Текст версии
        min_display_time: Минимальное время отображения в миллисекундах
        
    Returns:
        AnimatedSplashScreen: Созданный splash screen
    """
    splash = create_splash_screen(background_path, version_text)
    splash.show()
    app.processEvents()  # Обрабатываем события для отображения
    
    # Устанавливаем минимальное время отображения
    from PySide6.QtCore import QTime
    splash.start_time = QTime.currentTime()
    splash.min_display_time = min_display_time
    
    return splash
