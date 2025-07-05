from flask import Flask, request, jsonify
from threading import Thread
import json
from datetime import datetime
from typing import Dict, List
from .downloader import DownloadWorker

class DownloaderAPI:
    """
    REST API สำหรับควบคุมการดาวน์โหลดจากระยะไกล
    """
    def __init__(self, download_manager, port: int = 5000):
        self.app = Flask(__name__)
        self.port = port
        self.download_manager = download_manager
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        กำหนดเส้นทาง API
        """
        self.app.add_url_rule('/api/add_download', 'add_download', self.add_download, methods=['POST'])
        self.app.add_url_rule('/api/status', 'get_status', self.get_status, methods=['GET'])
        self.app.add_url_rule('/api/stop', 'stop_download', self.stop_download, methods=['POST'])
        self.app.add_url_rule('/api/queue', 'get_queue', self.get_queue, methods=['GET'])

    def add_download(self) -> Dict:
        """
        เพิ่มงานดาวน์โหลดใหม่
        """
        data = request.json
        required_fields = ['channel_id', 'channel_name', 'guild_id']
        
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        task = {
            'channel_id': data['channel_id'],
            'channel_name': data['channel_name'],
            'guild_id': data['guild_id'],
            'save_metadata': data.get('save_metadata', True),
            'scheduled_time': data.get('scheduled_time')
        }
        
        self.download_manager.add_download_task(task)
        return jsonify({"status": "success", "message": "Download task added"})

    def get_status(self) -> Dict:
        """
        รับสถานะการดาวน์โหลดปัจจุบัน
        """
        active_downloads = self.download_manager.get_active_downloads()
        queue = self.download_manager.get_download_queue()
        
        return jsonify({
            "status": "success",
            "active_downloads": active_downloads,
            "queue": queue
        })

    def stop_download(self) -> Dict:
        """
        หยุดการดาวน์โหลดปัจจุบัน
        """
        data = request.json
        channel_id = data.get('channel_id')
        
        if channel_id:
            self.download_manager.stop_download(channel_id)
            return jsonify({"status": "success", "message": f"Download for {channel_id} stopped"})
        else:
            self.download_manager.stop_all_downloads()
            return jsonify({"status": "success", "message": "All downloads stopped"})

    def get_queue(self) -> Dict:
        """
        รับรายการคิวดาวน์โหลด
        """
        queue = self.download_manager.get_download_queue()
        return jsonify({"status": "success", "queue": queue})

    def start(self) -> None:
        """
        เริ่มเซิร์ฟเวอร์ API
        """
        self.app.run(port=self.port, threaded=True)

    def start_in_thread(self) -> None:
        """
        เริ่มเซิร์ฟเวอร์ API ใน thread แยก
        """
        thread = Thread(target=self.start, daemon=True)
        thread.start()