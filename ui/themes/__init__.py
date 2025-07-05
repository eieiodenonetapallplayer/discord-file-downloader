from .dark import DARK_THEME
from .light import LIGHT_THEME
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

def apply_theme(widget, theme_name: str) -> None:
    """
    ใช้ธีมที่เลือกกับแอปพลิเคชัน
    """
    theme = DARK_THEME if theme_name == "Dark" else LIGHT_THEME
    
    # บันทึกธีมในคุณสมบัติแอปพลิเคชัน
    QApplication.instance().setProperty("theme", theme)
    
    # สร้าง palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(theme["background"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme["secondary"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["tertiary"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme["button"]["normal"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["danger"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(theme["primary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["text"]))
    
    widget.setPalette(palette)
    
    # สร้างสไตล์ชีต
    stylesheet = f"""
        /* CSS styles จะเหมือนกับที่ระบุในโค้ดเต็ม */
        QMainWindow {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        /* ... รายละเอียด stylesheet อื่นๆ ... */
    """
    
    widget.setStyleSheet(stylesheet)

__all__ = ['DARK_THEME', 'LIGHT_THEME', 'apply_theme']