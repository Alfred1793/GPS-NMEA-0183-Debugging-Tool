# GPS NMEA-0183 Debug Tool

## Project Overview

The GPS NMEA-0183 Debug Tool is a desktop application specifically designed for debugging and analyzing GPS device outputs. This tool **fully supports the NMEA-0183 protocol** and can parse and display GPS data conforming to this protocol in real-time. By connecting to GPS devices via serial port, this program can parse received NMEA data and present it through a clear and intuitive interface, facilitating debugging and analysis for developers and technicians.

## Key Features

- Comprehensive support for the NMEA-0183 protocol, capable of parsing common NMEA sentences (such as GPRMC, GPGGA, etc.)
- Real-time display of parsed GPS information, including time, date, latitude, longitude, altitude, speed, and heading
- Support for serial connections with various baud rates, compatible with a wide range of GPS devices
- Option to switch between displaying parsed information or raw NMEA data logs
- Classic command-line style log display with black background and green text, convenient for viewing and analyzing raw NMEA data
- User-friendly graphical interface, including information panels and control panels for quick setup and monitoring

## Installation Instructions

1. Ensure that Python 3.6 or higher is installed on your system.

2. Clone this repository to your local machine.

3. Install the required dependencies:
   ```
   pip install PySide6 pyserial pytz
   ```

## Usage Instructions

1. Run the main program:
   ```
   python main.py
   ```

2. Select the correct COM port and baud rate in the interface. Make sure these settings match your GPS device.

3. Click the "Start" button to begin receiving and parsing NMEA-0183 data.

4. Use the "Show Log" checkbox to toggle between displaying parsed information and raw NMEA data logs.

5. Analyze the displayed data, perform necessary debugging and testing.

6. Click the "Stop" button to stop receiving data.

Note: This tool is designed specifically for debugging GPS devices that comply with the NMEA-0183 protocol. If your device uses a different protocol, modifications may be necessary.

## File Structure

- `main.py`: Main program entry point
- `gps_ui.py`: User interface implementation
- `gps_communication.py`: GPS data communication and NMEA-0183 protocol parsing logic

## Dependencies

- PySide6
- pyserial
- pytz


---

