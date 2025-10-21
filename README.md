# GPS Vehicle Tracker using Raspberry Pi Pico
## Real-time Vehicle Tracking System with GSM & GPS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico-red.svg)](https://www.raspberrypi.org/products/raspberry-pi-pico/)
[![Language](https://img.shields.io/badge/Language-MicroPython-blue.svg)](https://micropython.org/)

A professional GPS-based vehicle tracking system built with Raspberry Pi Pico, GSM module, and Neo-6M GPS receiver. This project enables real-time vehicle location tracking via SMS and Google Maps integration, offering an affordable and efficient solution for vehicle monitoring.

---

## 🚀 Features

- ✅ **Real-time GPS Tracking** - Accurate location tracking using Neo-6M GPS module
- ✅ **GSM Communication** - Send/receive location data via SMS
- ✅ **Google Maps Integration** - View tracked location on Google Maps
- ✅ **Low Power Consumption** - Optimized for battery-powered applications
- ✅ **MicroPython Based** - Easy to understand and modify code
- ✅ **Cost-Effective** - Affordable alternative to commercial trackers
- ✅ **Remote Monitoring** - Track vehicles from anywhere via SMS commands
- ✅ **Compact Design** - Small form factor suitable for vehicle installation

---

## 📋 Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Circuit Diagram](#circuit-diagram)
- [Installation](#installation)
- [Wiring Guide](#wiring-guide)
- [Configuration](#configuration)
- [Usage](#usage)
- [SMS Commands](#sms-commands)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)

---

## 🔧 Hardware Requirements

| Component | Specification | Quantity |
|-----------|--------------|----------|
| Raspberry Pi Pico | RP2040 Microcontroller | 1 |
| Neo-6M GPS Module | GPS Receiver with Antenna | 1 |
| GSM Module | SIM800L / SIM900A | 1 |
| SIM Card | Active cellular SIM | 1 |
| Power Supply | 5V 2A adapter | 1 |
| Breadboard | Standard size | 1 |
| Jumper Wires | Male-to-Female, Male-to-Male | 20+ |
| USB Cable | Micro USB for programming | 1 |

### Optional Components
- External antenna for better GPS signal
- Battery pack for portable operation
- Enclosure/case for weatherproofing

---

## 💻 Software Requirements

- **Thonny IDE** (v3.3.3 or later) - [Download Here](https://thonny.org/)
- **MicroPython** firmware for Raspberry Pi Pico
- **Python 3.7+** (for development)

### Required Libraries
- `machine` - Built-in MicroPython library
- `time` - Built-in MicroPython library
- `utime` - MicroPython time utilities

---

## 🔌 Circuit Diagram

### GPS Module (Neo-6M) Connections
```
Neo-6M GPS    →    Raspberry Pi Pico
-----------------------------------------
VCC           →    5V (VBUS - Pin 40)
GND           →    GND (Pin 38)
TX            →    GP1 (UART0 RX - Pin 2)
RX            →    GP0 (UART0 TX - Pin 1)
```

### GSM Module (SIM800L) Connections
```
SIM800L       →    Raspberry Pi Pico
-----------------------------------------
VCC           →    5V (VBUS - Pin 40)
GND           →    GND (Pin 38)
TXD           →    GP5 (UART1 RX - Pin 7)
RXD           →    GP4 (UART1 TX - Pin 6)
```

> ⚠️ **Important**: Ensure proper power supply to GSM module (SIM800L requires stable 3.7-4.2V with peak current up to 2A). Consider using a separate power source or voltage regulator.

---

## 📥 Installation

### Step 1: Install Thonny IDE
1. Download Thonny IDE from [https://thonny.org/](https://thonny.org/)
2. Install for your operating system (Windows/Mac/Linux)
3. Launch Thonny IDE

### Step 2: Flash MicroPython Firmware
1. Download MicroPython firmware for Pico: [MicroPython Downloads](https://micropython.org/download/rp2-pico/)
2. Hold the BOOTSEL button on Pico while connecting to PC
3. Pico will appear as a USB mass storage device
4. Drag and drop the `.uf2` firmware file to the Pico drive
5. Pico will automatically reboot with MicroPython

### Step 3: Clone or Download Repository
```bash
git clone https://github.com/ShahbazCoder1/GPS-Vehicle-Tracker-using-Raspberry-Pi-Pico-MicroPython-Thonny-IDE.git
```

Or download ZIP from GitHub and extract.

### Step 4: Upload Code to Pico
1. Open Thonny IDE
2. Go to **Tools** → **Options** → **Interpreter**
3. Select "MicroPython (Raspberry Pi Pico)"
4. Open the main Python file from the repository
5. Click **Run** → **Save to Raspberry Pi Pico**
6. Save as `main.py`

---

## 🔗 Wiring Guide

### Complete Connection Diagram

```
Raspberry Pi Pico Pinout:
┌─────────────────────────┐
│ GP0 (TX)  ──→  GPS RX   │
│ GP1 (RX)  ←──  GPS TX   │
│ GP4 (TX)  ──→  GSM RX   │
│ GP5 (RX)  ←──  GSM TX   │
│ VBUS      ──→  GPS VCC  │
│ VBUS      ──→  GSM VCC  │
│ GND       ──→  Common GND│
└─────────────────────────┘
```

### Safety Tips
- Double-check all connections before powering on
- Use a multimeter to verify voltage levels
- Ensure GSM module has adequate power supply
- Keep GPS antenna away from electronic interference

---

## ⚙️ Configuration

### 1. Configure Phone Number
Edit the main code file and update the phone number:

```python
# Replace with your phone number
ADMIN_PHONE = "+9186********"
```

### 3. Configure GPS Update Interval
```python
# Update interval in seconds
GPS_UPDATE_INTERVAL = 10
```

---

## 📱 Usage

### Starting the System
1. Connect all hardware components as per wiring guide
2. Insert active SIM card into GSM module
3. Power on the Raspberry Pi Pico
4. Wait for GPS to acquire satellite lock (blue LED on GPS module)
5. Wait for GSM module to register on network

### Monitoring Status
- **GPS LED**: Blinking = Searching, Solid = Lock acquired
- **GSM LED**: Blinking = Network registered

---

## 💬 SMS Commands

Send the following SMS commands to the tracker:

| Command | Description | Response |
|---------|-------------|----------|
| `LOCATION` | Get current GPS coordinates | Lat, Lng, Google Maps link |
| `STATUS` | Check system status | GPS status, GSM signal strength |
| `HELP` | List available commands | Command list |

### Example
```
Send: LOCATION
Receive: Lat: 37.7749, Lng: -122.4194
Google Maps: https://maps.google.com/?q=37.7749,-122.4194
```

---

## 🐛 Troubleshooting

### GPS Not Getting Fix
- Ensure GPS antenna has clear view of sky
- Wait 2-5 minutes for initial satellite lock (cold start)
- Check UART connections (TX/RX not reversed)
- Verify 3.3V power supply to GPS module

### GSM Module Not Responding
- Check power supply (needs 3.7-4.2V with sufficient current)
- Verify SIM card is active and has credit
- Check antenna connection
- Ensure correct APN settings for your carrier
- Try AT commands manually to test module

### No SMS Received
- Verify phone number format (include country code)
- Check SIM card has SMS capability
- Ensure GSM module is registered on network
- Check signal strength in your area

### Code Upload Fails
- Ensure MicroPython firmware is properly installed
- Check USB cable connection
- Try different USB port
- Restart Thonny IDE


---

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Shahbaz** - [@ShahbazCoder1](https://github.com/ShahbazCoder1)

Project Link: [https://github.com/ShahbazCoder1/GPS-Vehicle-Tracker-using-Raspberry-Pi-Pico-MicroPython-Thonny-IDE](https://github.com/ShahbazCoder1/GPS-Vehicle-Tracker-using-Raspberry-Pi-Pico-MicroPython-Thonny-IDE)

---

## 🙏 Acknowledgments

- [Raspberry Pi Foundation](https://www.raspberrypi.org/) for the amazing Pico board
- [MicroPython](https://micropython.org/) community for the excellent firmware
- [Thonny IDE](https://thonny.org/) developers for the user-friendly IDE
- All contributors and users of this project

---

## ⭐ Show Your Support

If you find this project helpful, please give it a ⭐ on GitHub!

---

**Made with ❤️ by ShahbazCoder1**
