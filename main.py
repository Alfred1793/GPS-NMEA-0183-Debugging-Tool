import sys
import logging
from PySide6.QtWidgets import QApplication
from gps_ui import GPSApp

# 设置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPSApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())