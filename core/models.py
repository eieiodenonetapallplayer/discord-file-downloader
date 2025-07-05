from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

@dataclass
class DownloadTask:
    """
    โมเดลสำหรับงานดาวน์โหลด
    """
    channel_id: str
    channel_name: str
    channel_type: str  # "text", "forum", "thread"
    guild_id: str
    scheduled_time: Optional[datetime] = None
    save_metadata: bool = True
    status: str = "pending"  # "pending", "downloading", "completed", "failed"
    progress: float = 0.0
    downloaded_files: int = 0
    total_files: int = 0

@dataclass
class FileMetadata:
    """
    โมเดลสำหรับ metadata ของไฟล์
    """
    id: str
    filename: str
    path: str
    size: int
    file_type: str
    message_id: str
    channel_id: str
    guild_id: str
    author_id: str
    timestamp: datetime
    tags: List[str] = None
    downloaded_at: datetime = None

@dataclass
class GuildInfo:
    """
    โมเดลสำหรับข้อมูล Guild
    """
    id: str
    name: str
    icon: Optional[str]
    channels: List['ChannelInfo'] = None

@dataclass
class ChannelInfo:
    """
    โมเดลสำหรับข้อมูล Channel
    """
    id: str
    name: str
    type: int  # 0 = text, 2 = voice, 4 = category, 5 = announcement, 15 = forum
    parent_id: Optional[str]
    position: int
    topic: Optional[str]
    nsfw: bool = False