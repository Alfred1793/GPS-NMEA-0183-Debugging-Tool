from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit, 
                               QPushButton, QHBoxLayout, QComboBox, QFormLayout, QGroupBox, QCheckBox)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt
import serial.tools.list_ports
from gps_communication import GPSWorker

class GPSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPS NMEA-0183 调试工具")

        self.main_layout = QHBoxLayout()

        # 左侧信息面板
        self.info_panel = QGroupBox("GPS信息")
        self.create_info_panel()
        
        # 右侧控制面板
        self.control_panel = QVBoxLayout()
        self.create_control_panel()

        # 将左右两个面板添加到主布局
        self.main_layout.addWidget(self.info_panel, 1)
        self.main_layout.addLayout(self.control_panel, 2)

        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self.gps_worker = None

        # 初始化时显示 ASCII 艺术
        self.toggle_log_display(Qt.Unchecked)

    def create_info_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)  # 设置很小的间距
        layout.setContentsMargins(10, 10, 10, 10)  # 设置边距

        font = QFont()
        font.setPointSize(9)

        self.info_labels = {
            "连接状态": QLabel("未连接"),
            "COM端口": QLabel("未选择"),
            "波特率": QLabel("未设置"),
            "时间": QLabel("未知"),
            "日期": QLabel("未知"),
            "纬度": QLabel("未知"),
            "经度": QLabel("未知"),
            "高度": QLabel("未知"),
            "速度": QLabel("未知"),
            "航向": QLabel("未知"),
            "卫星数量": QLabel("未知")
        }

        for label, value in self.info_labels.items():
            info_layout = QHBoxLayout()
            info_layout.setSpacing(5)
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(font)
            label_widget.setFixedWidth(60)  # 固定标签宽度
            value.setFont(font)
            info_layout.addWidget(label_widget)
            info_layout.addWidget(value, 1)
            layout.addLayout(info_layout)

        layout.addStretch(1)  # 添加弹性空间把所有内容推到顶部
        self.info_panel.setLayout(layout)

    def create_control_panel(self):
        settings_group = QGroupBox("连接设置")
        settings_layout = QFormLayout()
        settings_layout.setVerticalSpacing(5)

        self.com_port_combo = QComboBox()
        self.baud_rate_combo = QComboBox()

        self.com_port_combo.addItems(self.get_available_com_ports())
        self.baud_rate_combo.addItems(["4800", "9600", "19200", "38400", "57600", "115200"])
        self.baud_rate_combo.setCurrentText("9600")

        settings_layout.addRow("COM端口:", self.com_port_combo)
        settings_layout.addRow("波特率:", self.baud_rate_combo)
        settings_group.setLayout(settings_layout)

        self.control_panel.addWidget(settings_group)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("启动")
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        self.control_panel.addLayout(button_layout)

        # 添加显示日志的复选框
        self.show_log_checkbox = QCheckBox("显示日志")
        self.show_log_checkbox.setChecked(False)
        self.show_log_checkbox.stateChanged.connect(self.toggle_log_display)
        self.control_panel.addWidget(self.show_log_checkbox)

        self.gps_info_text = QTextEdit()
        self.gps_info_text.setReadOnly(True)
        self.set_log_style()
        self.control_panel.addWidget(self.gps_info_text)

        self.start_button.clicked.connect(self.start_reading)
        self.stop_button.clicked.connect(self.stop_reading)

    def set_log_style(self):
        palette = self.gps_info_text.palette()
        palette.setColor(QPalette.Base, QColor(0, 0, 0))  # 黑色背景
        palette.setColor(QPalette.Text, QColor(0, 255, 0))  # 绿色文字
        self.gps_info_text.setPalette(palette)

    def get_available_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start_reading(self):
        port = self.com_port_combo.currentText()
        baudrate = int(self.baud_rate_combo.currentText())

        if self.gps_worker is not None:
            self.gps_worker.stop()
            self.gps_worker.wait()

        self.gps_worker = GPSWorker(port, baudrate)
        self.gps_worker.data_received.connect(self.process_gps_data)
        self.gps_worker.connection_status_changed.connect(self.update_connection_status)
        self.gps_worker.start()

        self.info_labels["连接状态"].setText("已连接")
        self.info_labels["COM端口"].setText(port)
        self.info_labels["波特率"].setText(str(baudrate))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.gps_info_text.clear()

    def stop_reading(self):
        if self.gps_worker is not None:
            self.gps_worker.stop()
            self.gps_worker.wait()

        self.info_labels["连接状态"].setText("已停止")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def process_gps_data(self, line):
        current_data = self.gps_worker.get_current_data()
        self.update_info_panel(current_data)

        if self.show_log_checkbox.isChecked():
            if line.startswith("$GNRMC"):
                speed_kmh = self.convert_knots_to_kmh(current_data['speed'])
                self.gps_info_text.append(f"时间: {current_data['time']} 日期: {current_data['date']} "
                                          f"经度: {current_data['longitude']} 纬度: {current_data['latitude']} "
                                          f"速度: {speed_kmh:.2f} km/h 航向: {current_data['course']}°")
            elif line.startswith("$GNGGA"):
                self.gps_info_text.append(f"GGA信息 -> 时间: {current_data['time']} "
                                          f"纬度: {current_data['latitude']} 经度: {current_data['longitude']} "
                                          f"卫星数量: {current_data['satellites']} 高度: {current_data['altitude']}m")

    def update_info_panel(self, data):
        self.info_labels["时间"].setText(data['time'])
        self.info_labels["日期"].setText(data['date'])
        self.info_labels["纬度"].setText(data['latitude'])
        self.info_labels["经度"].setText(data['longitude'])
        self.info_labels["高度"].setText(f"{data['altitude']}m")
        speed_kmh = self.convert_knots_to_kmh(data['speed'])
        self.info_labels["速度"].setText(f"{speed_kmh:.2f} km/h")
        self.info_labels["航向"].setText(f"{data['course']}°")
        self.info_labels["卫星数量"].setText(data['satellites'])

    def update_connection_status(self, status):
        self.info_labels["连接状态"].setText(status)

    @staticmethod
    def convert_knots_to_kmh(speed):
        try:
            return float(speed) * 1.852
        except ValueError:
            return 0.0

    def toggle_log_display(self, state):
        self.gps_info_text.clear()
        if state == Qt.Unchecked:
            copyright_notice = """
    GPS NMEA-0183 调试工具
    GPS NMEA-0183 Debugging Tool
    版本 1.0
    Version 1.0
    请连接您的GPS设备并点击“启动”按钮。
    Please connect your GPS device and click the "启动" button.
    """
            self.gps_info_text.setPlainText(copyright_notice)
        else:
            self.gps_info_text.setPlainText("")

    def closeEvent(self, event):
        if self.gps_worker is not None:
            self.gps_worker.stop()
            self.gps_worker.wait()
        event.accept()