import serial
import logging
import pytz
from datetime import datetime, date
from PySide6.QtCore import QThread, Signal
from threading import Lock

class GPSData:
    def __init__(self):
        self.time = "未知"
        self.date = "未知"
        self.latitude = "未知"
        self.longitude = "未知"
        self.speed = "未知"
        self.course = "未知"
        self.altitude = "未知"
        self.satellites = "未知"
        self.lock = Lock()

    def update(self, **kwargs):
        with self.lock:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def get_all(self):
        with self.lock:
            return {
                'time': self.time,
                'date': self.date,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'speed': self.speed,
                'course': self.course,
                'altitude': self.altitude,
                'satellites': self.satellites
            }

class GPSWorker(QThread):
    data_received = Signal(str)
    connection_status_changed = Signal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.serial_port = serial.Serial(port, baudrate, timeout=1)
        self.gps_data = GPSData()

    def run(self):
        while self.running:
            try:
                if self.serial_port.is_open:
                    line = self.serial_port.readline().decode('ascii', errors='ignore').strip()
                    if line:
                        self.process_gps_data(line)
                        self.data_received.emit(line)
                else:
                    self.connection_status_changed.emit("串口关闭")
                    break
            except Exception as e:
                logging.error(f"读取GPS数据时发生错误: {e}")
                self.connection_status_changed.emit(f"读取数据错误: {e}")
                break

    def stop(self):
        self.running = False
        if self.serial_port.is_open:
            self.serial_port.close()

    def process_gps_data(self, line):
        if line.startswith("$GNRMC"):
            data = parse_rmc(line)
            if data:
                self.gps_data.update(
                    time=data['time'],
                    date=data['date'],
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    speed=data['speed'],
                    course=data['course']
                )
        elif line.startswith("$GNGGA"):
            data = parse_gga(line)
            if data:
                self.gps_data.update(
                    altitude=data['altitude'],
                    satellites=data['num_satellites']
                )

    def get_current_data(self):
        return self.gps_data.get_all()

def convert_latitude(raw_value, direction):
    try:
        degrees = int(raw_value[:2])
        minutes = float(raw_value[2:])
        degree_minute_str = f"{degrees}°{minutes:.3f}′"
        if direction == 'S':
            degree_minute_str = "-" + degree_minute_str
        return degree_minute_str
    except ValueError as e:
        logging.error(f"转换纬度时出错: {e}")
        return "未知"

def convert_longitude(raw_value, direction):
    try:
        degrees = int(raw_value[:3])
        minutes = float(raw_value[3:])
        degree_minute_str = f"{degrees}°{minutes:.3f}′"
        if direction == 'W':
            degree_minute_str = "-" + degree_minute_str
        return degree_minute_str
    except ValueError as e:
        logging.error(f"转换经度时出错: {e}")
        return "未知"

def parse_rmc(line):
    parts = line.split(',')
    if len(parts) > 11:
        time = parts[1]
        status = "有效" if parts[2] == 'A' else "无效"
        latitude = convert_latitude(parts[3], parts[4])
        longitude = convert_longitude(parts[5], parts[6])
        speed = parts[7]  # Speed over ground in knots
        course = parts[8]  # Course over ground in degrees
        date = parts[9]

        dt = datetime.strptime(f"{date}{time[:6]}", "%d%m%y%H%M%S")
        utc_dt = pytz.utc.localize(dt)
        cst_dt = utc_dt.astimezone(pytz.timezone('Asia/Shanghai'))
        current_time = cst_dt.strftime("%H:%M:%S")

        return {
            'time': current_time,
            'status': status,
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'course': course,
            'date': f"{date[0:2]}:{date[2:4]}:{date[4:6]}",
            'full_time': cst_dt.strftime("%Y-%m-%d %H:%M:%S%z")
        }
    return None

def parse_gga(line):
    parts = line.split(',')
    if len(parts) > 9:
        time = parts[1]
        latitude = convert_latitude(parts[2], parts[3])
        longitude = convert_longitude(parts[4], parts[5])
        fix_quality = parts[6]
        num_satellites = parts[7]
        altitude = parts[9]

        current_date = date.today().strftime("%d%m%y")
        dt = datetime.strptime(f"{current_date}{time[:6]}", "%d%m%y%H%M%S")
        if '.' in time:
            dt = dt.replace(microsecond=int(float("0." + time.split('.')[1]) * 1_000_000))

        utc_dt = pytz.utc.localize(dt)
        cst_dt = utc_dt.astimezone(pytz.timezone('Asia/Shanghai'))
        current_time = cst_dt.strftime("%Y-%m-%d %H:%M:%S%z")

        return {
            'time': current_time,
            'latitude': latitude,
            'longitude': longitude,
            'num_satellites': num_satellites,
            'altitude': altitude
        }
    return None

def parse_gsv(line):
    parts = line.split(',')
    total_messages = parts[1]
    message_number = parts[2]
    satellites_in_view = parts[3]
    system_type = "未知"

    if line.startswith("$GPGSV"):
        system_type = "GPS"
    elif line.startswith("$GLGSV"):
        system_type = "GLONASS"
    elif line.startswith("$GBGSV"):
        system_type = "BeiDou"

    return {
        'system_type': system_type,
        'message_number': message_number,
        'total_messages': total_messages,
        'satellites_in_view': satellites_in_view
    }