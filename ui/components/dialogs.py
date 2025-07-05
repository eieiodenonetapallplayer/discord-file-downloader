from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt6.QtGui import QColor, QPainter, QFont, QPixmap, QImage
from plyer import notification

class DiscordOAuthWindow(QDialog):
    """
    หน้าต่างล็อกอินด้วย Discord OAuth
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Discord Login")
        self.setFixedSize(600, 700)
        self.token = None
        
        self.webview = QWebEngineView()
        self.profile = QWebEngineProfile("oauth_profile", self.webview)
        self.webview.setPage(QWebEnginePage(self.profile, self.webview))
        
        # Load Discord OAuth URL
        client_id = "YOUR_CLIENT_ID"  # เปลี่ยนเป็น Client ID ของคุณ
        redirect_uri = "http://localhost:8080/auth"
        scope = "identify guilds"
        oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        self.webview.load(QUrl(oauth_url))
        self.webview.urlChanged.connect(self._check_redirect)
        
        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

    def _check_redirect(self, url):
        if "code=" in url.toString():
            self.token = self._extract_token_from_url(url)
            if self.token:
                self.accept()

    def _extract_token_from_url(self, url):
        return url.toString().split("code=")[1].split("&")[0]

class ToastNotification(QLabel):
    """
    การแจ้งเตือนแบบ Toast
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            background-color: #202225;
            color: white;
            border-radius: 5px;
            padding: 0 15px;
            font-weight: bold;
        """)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

    def show_message(self, message: str, success: bool = True) -> None:
        theme = QApplication.instance().property("theme")
        color = theme["success"] if success else theme["danger"]
        
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 5px;
            padding: 0 15px;
            font-weight: bold;
        """)
        self.setText(message)
        self.show()
        
        # เอฟเฟกต์ fade in/out
        self.setWindowOpacity(0)
        
        fade_in = QPropertyAnimation(self, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        
        delay = QTimer()
        delay.setSingleShot(True)
        delay.timeout.connect(lambda: fade_out.start())
        
        fade_in.finished.connect(delay.start)
        fade_out.finished.connect(self.hide)
        fade_in.start()

class FilePreviewer(QDialog):
    """
    หน้าต่างแสดงตัวอย่างไฟล์ก่อนดาวน์โหลด
    """
    def __init__(self, file_info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Preview")
        self.setMinimumSize(600, 500)
        self.file_info = file_info
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        
        # พื้นที่แสดงตัวอย่างไฟล์
        self.preview_area = QLabel()
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # สร้างตัวอย่างตามประเภทไฟล์
        if self.file_info['type'].startswith('image'):
            self._setup_image_preview()
        elif self.file_info['type'].startswith('video'):
            self._setup_video_preview()
        elif self.file_info['type'] in ['pdf', 'document']:
            self._setup_document_preview()
        else:
            self._setup_generic_preview()
        
        layout.addWidget(self.preview_area)
        
        # ข้อมูลไฟล์
        info_group = QGroupBox("File Information")
        info_layout = QVBoxLayout()
        
        info_layout.addWidget(QLabel(f"Name: {self.file_info.get('filename', 'N/A')}"))
        info_layout.addWidget(QLabel(f"Type: {self.file_info.get('type', 'N/A')}"))
        info_layout.addWidget(QLabel(f"Size: {self._format_size(self.file_info.get('size', 0))}"))
        info_layout.addWidget(QLabel(f"Uploaded: {self.file_info.get('timestamp', 'N/A')}"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # ปุ่มควบคุม
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _setup_image_preview(self):
        image = QImage(400, 300, QImage.Format.Format_RGB32)
        image.fill(QColor(54, 57, 63))
        
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20))
        painter.drawText(QRectF(0, 0, 400, 300), 
                        Qt.AlignmentFlag.AlignCenter, 
                        f"Image Preview\n{self.file_info['filename']}")
        painter.end()
        
        self.preview_area.setPixmap(QPixmap.fromImage(image))
    
    def _setup_video_preview(self):
        image = QImage(400, 300, QImage.Format.Format_RGB32)
        image.fill(QColor(30, 33, 36))
        
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20))
        
        # วาดไอคอนเล่นวิดีโอ
        painter.drawEllipse(150, 100, 100, 100)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPolygon([QPoint(180, 130), QPoint(180, 170), QPoint(220, 150)])
        
        painter.drawText(QRectF(0, 220, 400, 80), 
                        Qt.AlignmentFlag.AlignCenter, 
                        f"Video Preview\n{self.file_info['filename']}")
        painter.end()
        
        self.preview_area.setPixmap(QPixmap.fromImage(image))
    
    def _setup_document_preview(self):
        image = QImage(400, 300, QImage.Format.Format_RGB32)
        image.fill(QColor(255, 255, 255))
        
        painter = QPainter(image)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 20))
        
        # วาดไอคอนเอกสาร
        painter.drawRect(160, 100, 120, 160)
        painter.drawRect(170, 110, 100, 20)
        painter.drawLine(170, 140, 270, 140)
        painter.drawLine(170, 160, 270, 160)
        painter.drawLine(170, 180, 270, 180)
        painter.drawLine(170, 200, 270, 200)
        painter.drawLine(170, 220, 270, 220)
        painter.drawLine(170, 240, 270, 240)
        
        painter.drawText(QRectF(0, 20, 400, 80), 
                        Qt.AlignmentFlag.AlignCenter, 
                        f"Document Preview\n{self.file_info['filename']}")
        painter.end()
        
        self.preview_area.setPixmap(QPixmap.fromImage(image))
    
    def _setup_generic_preview(self):
        image = QImage(400, 300, QImage.Format.Format_RGB32)
        image.fill(QColor(54, 57, 63))
        
        painter = QPainter(image)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20))
        painter.drawText(QRectF(0, 0, 400, 300), 
                        Qt.AlignmentFlag.AlignCenter, 
                        f"No Preview Available\n{self.file_info['filename']}")
        painter.end()
        
        self.preview_area.setPixmap(QPixmap.fromImage(image))
    
    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"