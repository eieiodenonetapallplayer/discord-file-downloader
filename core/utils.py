import os
import json
import platform
from typing import Dict, Optional
from plyer import notification

def load_config(config_file: str = "config.json") -> Dict:
    """
    โหลดการตั้งค่าจากไฟล์ config
    """
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_config(token: str, guild_id: str, config_file: str = "config.json") -> None:
    """
    บันทึกการตั้งค่าไปยังไฟล์ config
    """
    with open(config_file, "w") as f:
        json.dump({"token": token, "guild_id": guild_id}, f, indent=4)

def show_notification(title: str, message: str) -> None:
    """
    แสดงการแจ้งเตือนระบบ
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Discord Downloader",
            timeout=10
        )
    except Exception as e:
        print(f"Failed to show notification: {e}")

def open_file_in_explorer(file_path: str) -> None:
    """
    เปิดไฟล์ใน File Explorer
    """
    try:
        if platform.system() == "Windows":
            os.startfile(os.path.dirname(file_path))
        elif platform.system() == "Darwin":
            os.system(f"open '{os.path.dirname(file_path)}'")
        else:
            os.system(f"xdg-open '{os.path.dirname(file_path)}'")
    except Exception as e:
        print(f"Failed to open file explorer: {e}")

def format_file_size(size_bytes: int) -> str:
    """
    จัดรูปแบบขนาดไฟล์ให้อ่านง่าย
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def sanitize_filename(filename: str) -> str:
    """
    ทำความสะอาดชื่อไฟล์
    """
    invalid_chars = '<>:"/\\|?*'
    for ch in invalid_chars:
        filename = filename.replace(ch, '_')
    return filename.strip(' .')