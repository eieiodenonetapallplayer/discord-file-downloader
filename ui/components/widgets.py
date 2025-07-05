from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QDateTimeEdit,
    QPushButton, QLabel, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, QDateTime, QTimer, pyqtSignal
from PyQt6.QtGui import QColor

class DownloadScheduler(QWidget):
    """
    ระบบจัดคิวและกำหนดเวลาดาวน์โหลด
    """
    download_scheduled = pyqtSignal(dict)  # ส่งข้อมูลงานเมื่อกำหนดเวลา
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {
                background-color: #2F3136;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
        """)
        
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDateTime(QDateTime.currentDateTime())
        self.start_time_edit.setCalendarPopup(True)
        
        self.add_to_queue_btn = QPushButton("Add to Queue")
        self.schedule_btn = QPushButton("Schedule Download")
        self.cancel_btn = QPushButton("Cancel All")
        
        self.add_to_queue_btn.clicked.connect(self._add_to_queue)
        self.schedule_btn.clicked.connect(self._schedule_download)
        self.cancel_btn.clicked.connect(self._cancel_all)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_to_queue_btn)
        button_layout.addWidget(self.schedule_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(QLabel("Download Queue:"))
        layout.addWidget(self.queue_list)
        layout.addWidget(QLabel("Schedule Time:"))
        layout.addWidget(self.start_time_edit)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _add_to_queue(self):
        # ในแอปจริงควรมีกล่องโต้ตอบเลือกช่องทาง
        item = f"Channel {self.queue_list.count() + 1}"
        self.queue_list.addItem(item)
    
    def _schedule_download(self):
        if self.queue_list.count() == 0:
            return
            
        scheduled_time = self.start_time_edit.dateTime()
        items = [self.queue_list.item(i).text() for i in range(self.queue_list.count())]
        
        self.download_scheduled.emit({
            "channels": items,
            "scheduled_time": scheduled_time.toString(Qt.DateFormat.ISODate),
            "save_metadata": True
        })
        
        self.queue_list.clear()
    
    def _cancel_all(self):
        self.queue_list.clear()

class FileTagger(QWidget):
    """
    ระบบจัดการแท็กไฟล์
    """
    tag_added = pyqtSignal(str)
    tag_removed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = set()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add tags (comma separated)...")
        self.tag_input.returnPressed.connect(self._add_tags)
        
        self.add_tag_btn = QPushButton("Add Tags")
        self.add_tag_btn.clicked.connect(self._add_tags)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.tag_input)
        input_layout.addWidget(self.add_tag_btn)
        
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet("""
            QListWidget {
                background-color: #2F3136;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
        """)
        self.tag_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tag_list.customContextMenuRequested.connect(self._show_tag_context_menu)
        
        layout.addWidget(QLabel("File Tags:"))
        layout.addLayout(input_layout)
        layout.addWidget(self.tag_list)
        
        self.setLayout(layout)
    
    def _add_tags(self):
        tags_text = self.tag_input.text().strip()
        if not tags_text:
            return
            
        new_tags = {tag.strip() for tag in tags_text.split(",") if tag.strip()}
        
        for tag in new_tags:
            if tag not in self.tags:
                self.tags.add(tag)
                self.tag_list.addItem(tag)
                self.tag_added.emit(tag)
        
        self.tag_input.clear()
    
    def _show_tag_context_menu(self, pos):
        item = self.tag_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()
        remove_action = menu.addAction("Remove Tag")
        action = menu.exec(self.tag_list.mapToGlobal(pos))
        
        if action == remove_action:
            tag = item.text()
            self.tags.remove(tag)
            self.tag_list.takeItem(self.tag_list.row(item))
            self.tag_removed.emit(tag)
    
    def set_tags(self, tags):
        self.tags = set(tags)
        self.tag_list.clear()
        for tag in sorted(self.tags):
            self.tag_list.addItem(tag)
    
    def get_tags(self):
        return list(self.tags)

class FileSearch(QWidget):
    """
    ระบบค้นหาไฟล์ที่ดาวน์โหลดแล้ว
    """
    search_requested = pyqtSignal(str)
    file_opened = pyqtSignal(str)
    file_deleted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search downloaded files...")
        self.search_input.returnPressed.connect(self._trigger_search)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._trigger_search)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #2F3136;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
        """)
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self._show_result_context_menu)
        
        self.status_label = QLabel("Ready to search")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.results_list)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def _trigger_search(self):
        query = self.search_input.text().strip()
        if query:
            self.status_label.setText(f"Searching for '{query}'...")
            self.search_requested.emit(query)
    
    def set_search_results(self, results):
        self.results_list.clear()
        
        if not results:
            self.status_label.setText("No results found")
            return
            
        for result in results:
            self.results_list.addItem(result["name"])
        
        self.status_label.setText(f"Found {len(results)} results")
    
    def _show_result_context_menu(self, pos):
        item = self.results_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()
        open_action = menu.addAction("Open File")
        open_folder_action = menu.addAction("Open Folder")
        menu.addSeparator()
        delete_action = menu.addAction("Delete File")
        
        action = menu.exec(self.results_list.mapToGlobal(pos))
        
        if action == open_action:
            self.file_opened.emit(item.text())
        elif action == open_folder_action:
            self.file_opened.emit(item.text())
        elif action == delete_action:
            self.file_deleted.emit(item.text())