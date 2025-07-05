import os
import json
import aiohttp
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadResumer:
    """
    ระบบ Resume การดาวน์โหลด
    """
    def __init__(self, state_file: str = "download_state.json"):
        self.state_file = state_file

    def save_state(self, download_state: Dict) -> None:
        """
        บันทึกสถานะการดาวน์โหลดปัจจุบัน
        """
        try:
            with open(self.state_file, "w") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "downloads": download_state
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to save download state: {e}")

    def load_state(self) -> Optional[Dict]:
        """
        โหลดสถานะการดาวน์โหลดที่บันทึกไว้
        """
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    # ตรวจสอบว่าสถานะไม่เก่าเกินไป (เช่น 24 ชม.)
                    last_updated = datetime.fromisoformat(state["timestamp"])
                    if (datetime.now() - last_updated).total_seconds() < 86400:
                        return state["downloads"]
        except Exception as e:
            print(f"Failed to load download state: {e}")
        return None

    def clear_state(self) -> None:
        """
        ลบไฟล์สถานะการดาวน์โหลด
        """
        try:
            Path(self.state_file).unlink(missing_ok=True)
        except Exception as e:
            print(f"Failed to clear download state: {e}")

class DownloadWorker(QThread):
    """
    Worker สำหรับดาวน์โหลดไฟล์ใน Thread แยก
    """
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    download_complete = pyqtSignal(str)           # channel_name
    error_occurred = pyqtSignal(str)             # error_message

    def __init__(self, token: str, guild_id: str, channel_id: str, channel_name: str, save_metadata: bool = True):
        super().__init__()
        self.token = token
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.save_metadata = save_metadata
        self.resumer = DownloadResumer()
        self.state = self._load_resume_state()
        self._is_running = True

    def _load_resume_state(self) -> Optional[Dict]:
        """
        โหลดสถานะการดาวน์โหลดที่ค้างไว้
        """
        state = self.resumer.load_state()
        if state and str(self.channel_id) in state:
            return state[str(self.channel_id)]
        return None

    def _save_resume_state(self, progress: Dict) -> None:
        """
        บันทึกสถานะการดาวน์โหลดปัจจุบัน
        """
        state = self.resumer.load_state() or {}
        state[str(self.channel_id)] = progress
        self.resumer.save_state(state)

    def stop(self) -> None:
        """
        หยุดการดาวน์โหลด
        """
        self._is_running = False

    def run(self) -> None:
        """
        เริ่มการดาวน์โหลด
        """
        try:
            asyncio.run(self._download())
        except Exception as e:
            self.error_occurred.emit(f"Error downloading {self.channel_name}: {str(e)}")
        finally:
            self.resumer.clear_state()

    async def _download(self) -> None:
        """
        ดาวน์โหลดไฟล์จากช่องทาง
        """
        try:
            downloader = ChannelDownloader(self.token, self.guild_id, self.save_metadata)
            start_from = self.state["last_message_id"] if self.state else None

            async with aiohttp.ClientSession() as session:
                await downloader.download_attachments_from_channel(
                    session,
                    self.channel_id,
                    self.channel_name,
                    progress_callback=self._update_progress,
                    start_from=start_from
                )

            self.download_complete.emit(f"Download complete: {self.channel_name}")
        except Exception as e:
            self.error_occurred.emit(f"Error downloading {self.channel_name}: {str(e)}")

    def _update_progress(self, current: int, total: int, message: str) -> None:
        """
        อัปเดตความคืบหน้า
        """
        if self._is_running:
            self.progress_updated.emit(current, total, message)
            self._save_resume_state({
                "last_message_id": message.split(" ")[-1],  # เก็บ ID ของข้อความล่าสุด
                "downloaded_files": current,
                "total_files": total,
                "timestamp": datetime.now().isoformat()
            })

class ChannelDownloader:
    """
    ดาวน์โหลดไฟล์จากช่องทางปกติ
    """
    def __init__(self, token: str, guild_id: str, save_metadata: bool = True):
        self.token = token
        self.guild_id = guild_id
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0",
        }
        self.save_metadata = save_metadata

    @staticmethod
    def sanitize_name(name: str) -> str:
        """
        ทำความสะอาดชื่อไฟล์/โฟลเดอร์
        """
        invalid_chars = '<>:"/\\|?*'
        for ch in invalid_chars:
            name = name.replace(ch, '_')
        return name.strip(' .')

    async def download_attachments_from_channel(
        self,
        session: aiohttp.ClientSession,
        channel_id: str,
        channel_name: str,
        progress_callback=None,
        start_from: Optional[str] = None
    ) -> None:
        """
        ดาวน์โหลดไฟล์แนบจากช่องทาง
        """
        channel_folder = os.path.join('DOWNLOADS', self.sanitize_name(channel_name))
        os.makedirs(channel_folder, exist_ok=True)
        
        url = f"{self.base_url}/channels/{channel_id}/messages?limit=100"
        if start_from:
            url += f"&before={start_from}"

        total_files = 0
        downloaded_files = 0

        while url and self._is_running:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to fetch messages: {resp.status}")
                
                messages = await resp.json()
                if not messages:
                    break
                
                for msg in messages:
                    if self.save_metadata:
                        await self._process_message(msg, channel_folder, session)
                    
                    for attachment in msg.get("attachments", []):
                        total_files += 1
                        if await self._download_attachment(attachment, channel_folder, session):
                            downloaded_files += 1
                            if progress_callback:
                                progress_callback(downloaded_files, total_files, f"Downloading {channel_name} - {attachment['filename']}")

                last_msg_id = messages[-1]["id"]
                url = f"{self.base_url}/channels/{channel_id}/messages?limit=100&before={last_msg_id}"

    async def _download_attachment(self, attachment: Dict, folder: str, session: aiohttp.ClientSession) -> bool:
        """
        ดาวน์โหลดไฟล์แนบ
        """
        file_url = attachment["url"]
        filename = attachment["filename"]
        file_path = os.path.join(folder, filename)
        
        try:
            async with session.get(file_url, headers=self.headers) as resp:
                if resp.status == 200:
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(await resp.read())
                    return True
        except Exception as e:
            print(f"Failed to download {filename}: {str(e)}")
            return False

    async def _process_message(self, msg: Dict, folder: str, session: aiohttp.ClientSession) -> None:
        """
        ประมวลผลข้อความและบันทึก metadata
        """
        message_data = {
            'id': msg['id'],
            'content': msg.get('content', ''),
            'author': msg.get('author', {}),
            'timestamp': msg.get('timestamp', ''),
            'attachments': [],
            'embeds': msg.get('embeds', [])
        }
        
        messages_folder = os.path.join(folder, 'messages')
        os.makedirs(messages_folder, exist_ok=True)
        
        for attachment in msg.get('attachments', []):
            file_url = attachment["url"]
            filename = attachment["filename"]
            file_path = os.path.join(folder, filename)
            
            message_data['attachments'].append({
                'filename': filename,
                'url': file_url,
                'size': attachment.get('size'),
                'local_path': os.path.relpath(file_path, folder)
            })
        
        with open(os.path.join(messages_folder, f"{msg['id']}.json"), 'w', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False, indent=2)

class ForumDownloader(ChannelDownloader):
    """
    ดาวน์โหลดไฟล์จาก Forum/Thread
    """
    async def fetch_forum_channels(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        ดึงข้อมูล Forum Channels ทั้งหมด
        """
        url = f"{self.base_url}/guilds/{self.guild_id}/channels"
        async with session.get(url, headers=self.headers) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to fetch channels: {resp.status}")
            channels = await resp.json()
            return [ch for ch in channels if ch.get("type") == 15]  # type 15 = forum

    async def fetch_threads_in_forum(self, session: aiohttp.ClientSession, forum_channel_id: str) -> List[Dict]:
        """
        ดึงข้อมูล Threads ใน Forum
        """
        threads = []
        
        # Active threads
        active_url = f"{self.base_url}/channels/{forum_channel_id}/threads/active"
        async with session.get(active_url, headers=self.headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                threads.extend(data.get("threads", []))
        
        # Archived threads
        archived_url = f"{self.base_url}/channels/{forum_channel_id}/threads/archived/public"
        async with session.get(archived_url, headers=self.headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                threads.extend(data.get("threads", []))
        
        return threads

    async def download_forum(self, session: aiohttp.ClientSession, progress_callback=None) -> None:
        """
        ดาวน์โหลดไฟล์จาก Forum ทั้งหมด
        """
        forum_channels = await self.fetch_forum_channels(session)
        if not forum_channels:
            raise Exception("No forum channels found")
        
        for forum in forum_channels:
            threads = await self.fetch_threads_in_forum(session, forum['id'])
            
            for thread in threads:
                await self.download_attachments_from_channel(
                    session,
                    thread['id'],
                    f"Forum/{forum['name']}/{thread['name']}",
                    progress_callback
                )