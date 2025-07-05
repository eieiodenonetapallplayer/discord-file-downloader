from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class StatsDashboard(QWidget):
    """
    Dashboard แสดงสถิติการดาวน์โหลด
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # กราฟวงกลมแสดงประเภทไฟล์
        file_type_chart = QChart()
        file_type_chart.setTitle("File Type Distribution")
        file_type_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        
        series = QPieSeries()
        series.append("Images", 45)
        series.append("Videos", 30)
        series.append("Documents", 25)
        series.setLabelsVisible(True)
        
        # กำหนดสีสำหรับแต่ละส่วน
        slices = series.slices()
        theme = QApplication.instance().property("theme")
        slices[0].setColor(QColor(theme["primary"]))  # Images
        slices[1].setColor(QColor(theme["danger"]))   # Videos
        slices[2].setColor(QColor(theme["success"]))  # Documents
        
        file_type_chart.addSeries(series)
        file_type_chart.legend().setVisible(True)
        
        chart_view = QChartView(file_type_chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # กราฟแท่งแสดงประวัติการดาวน์โหลด
        history_chart = QChart()
        history_chart.setTitle("Download History")
        history_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        
        bar_set = QBarSet("Downloads")
        bar_set.append([5, 10, 15, 20, 25, 30])
        bar_set.setColor(QColor(theme["primary"]))
        
        bar_series = QBarSeries()
        bar_series.append(bar_set)
        history_chart.addSeries(bar_series)
        
        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        axis = QBarCategoryAxis()
        axis.append(categories)
        history_chart.createDefaultAxes()
        history_chart.setAxisX(axis, bar_series)
        
        history_chart_view = QChartView(history_chart)
        history_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        layout.addWidget(chart_view)
        layout.addWidget(history_chart_view)
        self.setLayout(layout)