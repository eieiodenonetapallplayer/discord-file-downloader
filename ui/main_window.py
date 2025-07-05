import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QComboBox, QCheckBox, QProgressBar, QFrame, QSizePolicy,
    QMessageBox, QFileDialog, QTabWidget, QGroupBox, QMenu, QGraphicsDropShadowEffect,
    QTabBar, QSpinBox, QDateTimeEdit, QStackedWidget, QInputDialog, QApplication
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QPoint,
    QThread, pyqtSignal, QUrl, QDateTime, QRectF
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QLinearGradient, QBrush, QIcon,
    QPixmap, QTextCursor, QAction, QGuiApplication, QRegularExpressionValidator,
    QMovie, QPainter, QPainterPath, QImage
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis

from core import (
    DiscordOAuth, TokenValidator,
    ForumDownloader, ChannelDownloader, DownloadWorker, DownloadResumer,
    load_config, save_config, show_notification,
    get_guild_channels, is_token_valid, is_in_guild
)
from .components import (
    RippleButton, FloatingActionButton, ToggleSwitch,
    StatsDashboard, DiscordOAuthWindow, ToastNotification,
    FilePreviewer, DownloadScheduler, FileTagger, FileSearch
)
from .themes import apply_theme, DARK_THEME, LIGHT_THEME

class DiscordFileDownloader(QMainWindow):
    """
    หน้าต่างหลักของแอปพลิเคชัน Discord File Downloader
    """
    def __init__(self):
        super().__init__()
        self.token = None
        self.guild_id = None
        self.download_path = os.path.join(os.getcwd(), "DOWNLOADS")
        self.current_theme = "Dark"
        self.download_queue = []
        self.active_downloads = []
        
        self._init_ui()
        self._setup_animations()
        self._load_config()
        
        apply_theme(self, self.current_theme)
        self._start_api_server()

    def _init_ui(self):
        """Initialize the main UI components"""
        self.setWindowTitle("Discord File Downloader Ultimate")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Central widget with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(ModernTabBar())
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs
        self._create_main_tab()
        self._create_dashboard_tab()
        self._create_settings_tab()
        
        # Add header
        self.header = AnimatedHeader()
        self.layout().insertWidget(0, self.header)
        
        # Add floating action button
        self.fab = FloatingActionButton("assets/download.png")
        self.fab.clicked.connect(self._show_quick_download)
        self.fab.move(self.width() - 80, self.height() - 80)
        
        # Create toast notification
        self.toast = ToastNotification(self)
        
        # Create menu
        self._create_menu()
        
        # Status bar
        self._create_status_bar()

    # ... (โค้ดส่วนอื่นๆ จะคล้ายกับไฟล์ thai_ui.py เดิม แต่จัดโครงสร้างใหม่)
    # สามารถดูโค้ดเต็มได้จากไฟล์ thai_ui.py ที่คุณส่งมา

class ModernTabBar(QTabBar):
    """
    แท็บบาร์แบบโมเดิร์น
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 16px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5865F2;
                color: white;
            }
        """)

class AnimatedHeader(QLabel):
    """
    ส่วนหัวแบบมีอนิเมชัน
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._gradient_pos = 0
        
        self._animation = QPropertyAnimation(self, b"gradient_pos")
        self._animation.setDuration(3000)
        self._animation.setStartValue(0)
        self._animation.setEndValue(100)
        self._animation.setLoopCount(-1)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(self._gradient_pos, 0, 100 + self._gradient_pos, 100)
        
        theme = QApplication.instance().property("theme")
        gradient.setColorAt(0, QColor(theme["primary"]))
        gradient.setColorAt(0.5, QColor("#EB459E"))
        gradient.setColorAt(1, QColor(theme["danger"]))
        
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Draw logo
        logo = QPixmap("assets/logo.png").scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        painter.drawPixmap(20, 15, logo)
        
        # Draw title
        font = QFont("Poppins", 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(80, 50, "Discord File Downloader")