import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import DiscordFileDownloader

def main():
    # ตั้งค่าการแสดงผลสำหรับ High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # ตั้งค่า font หลัก
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # สร้างและแสดงหน้าต่างหลัก
    window = DiscordFileDownloader()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()