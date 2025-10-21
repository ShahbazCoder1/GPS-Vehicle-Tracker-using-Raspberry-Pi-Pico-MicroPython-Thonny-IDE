# GPS Vehicle Tracker using Raspberry Pi Pico | MicroPython & Thonny IDE
# Written by Shahbaz Hashmi Ansari

import machine
import time
import sys
from micropygps import MicropyGPS

# --- Pin Definitions ---
POWER_LED_PIN = 25
GSM_LED_PIN = 15
GPS_LED_PIN = 14

# --- Constants and Configuration ---
ADMIN_NUMBER = "+9186********"
LOCATION_INTERVAL_MS = 1 * 60 * 1000  # 1 minute for testing
GSM_CHECK_INTERVAL_MS = 10000 # Check GSM network status every 10 seconds

# --- Hardware Configuration ---
# UART for GSM Module (SIM800L, etc.)
gsm_uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1), timeout=1000)

# UART for GPS Module (NEO-6M, etc.)
gps_uart = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))

# --- System State Variables ---
gsm_connected = False
gps_fix_acquired = False
gsm_initialized = False

# --- GPS Parser Setup ---
# India is UTC+5:30, so local_offset is 5.5
gps_parser = MicropyGPS(location_formatting='dd', local_offset=5.5)

# --- Timing Variables for Non-Blocking Delays ---
last_location_sent_ms = 0
last_gsm_check_ms = 0

# --- LED Setup ---
power_led = machine.Pin(POWER_LED_PIN, machine.Pin.OUT)
gsm_led = machine.Pin(GSM_LED_PIN, machine.Pin.OUT)
gps_led = machine.Pin(GPS_LED_PIN, machine.Pin.OUT)
power_led.on()

#=================================================
# ===== HELPER FUNCTIONS =========================
#=================================================

def send_at_command(command, wait_time_ms=1000, max_wait_ms=3000):
    """Sends an AT command to the GSM module and returns the response."""
    print(f"Sending: {command}")
    try:
        # Clear any pending data first
        if gsm_uart.any():
            gsm_uart.read()
        
        gsm_uart.write((command + '\r\n').encode())
        
        # Wait for response with timeout
        response = ""
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < max_wait_ms:
            if gsm_uart.any():
                chunk = gsm_uart.read()
                if chunk:
                    response += chunk.decode('utf-8', 'ignore')
                # Small delay to allow complete response
                time.sleep_ms(wait_time_ms)
                # Read any remaining data
                if gsm_uart.any():
                    chunk = gsm_uart.read()
                    if chunk:
                        response += chunk.decode('utf-8', 'ignore')
                break
            time.sleep_ms(100)
        
        if response:
            print(f"Response: {response.strip()}")
        else:
            print("No response received")
        
        return response
    except Exception as e:
        print(f"Error in send_at_command: {e}")
        return ""

def check_gsm_module():
    """Check if GSM module is responding."""
    print("\nChecking GSM module connection...")
    
    # Try basic AT command
    response = send_at_command('AT', 1000, 2000)
    if 'OK' in response:
        print("✓ GSM module is responding")
        return True
    
    print("✗ GSM module not responding")
    print("  Check: 1) Power supply (4V) 2) TX/RX connections 3) Ground connection")
    return False

def send_sms(number, message):
    """Sends an SMS message with improved timeout handling."""
    if not gsm_connected:
        print("Cannot send SMS. GSM not connected.")
        return False
        
    print(f"\nSending SMS to {number}")
    print(f"Message: {message}")
    
    try:
        # Set SMS text mode
        send_at_command('AT+CMGF=1', 500)
        
        # Send the SMS command
        gsm_uart.write(f'AT+CMGS="{number}"\r\n'.encode())
        
        # Wait for '>' prompt with timeout
        prompt_received = False
        start_time = time.ticks_ms()
        response = ""
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 5000:
            if gsm_uart.any():
                chunk = gsm_uart.read()
                if chunk:
                    response += chunk.decode('utf-8', 'ignore')
                    if '>' in response:
                        prompt_received = True
                        break
            time.sleep_ms(50)
        
        if not prompt_received:
            print(f"Failed to get SMS prompt '>'")
            # Send ESC to cancel
            gsm_uart.write(b'\x1B')
            return False
        
        print("Got prompt, sending message...")
        
        # Send message content
        gsm_uart.write(message.encode('utf-8'))
        time.sleep_ms(100)
        
        # Send Ctrl+Z to finish
        gsm_uart.write(b'\x1A')
        
        # Wait for confirmation
        confirmation = ""
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 10000:
            if gsm_uart.any():
                chunk = gsm_uart.read()
                if chunk:
                    confirmation += chunk.decode('utf-8', 'ignore')
                    if '+CMGS:' in confirmation or 'OK' in confirmation:
                        print("✓ SMS sent successfully!")
                        return True
                    if 'ERROR' in confirmation:
                        print(f"✗ SMS error: {confirmation}")
                        return False
            time.sleep_ms(100)
        
        print("SMS timeout - message may not have been sent")
        return False
        
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def has_valid_gps_data():
    """Check if GPS has valid position data."""
    # Check if latitude and longitude tuples have valid data
    if (gps_parser.latitude[0] is not None and 
        gps_parser.longitude[0] is not None and
        gps_parser.latitude[0] != 0 and 
        gps_parser.longitude[0] != 0):
        return True
    return False

def get_current_location_string():
    """Formats the current location into a readable string."""
    if has_valid_gps_data():
        # Formatted (human-readable)
        lat_str = gps_parser.latitude_string()
        lon_str = gps_parser.longitude_string()

        # Decimal (for Google Maps link)
        lat = gps_parser.latitude[0]
        lon = gps_parser.longitude[0]

        # Check if timestamp and date are valid before using them
        ts = gps_parser.timestamp
        dt = gps_parser.date
        
        timestamp_str = ""
        if dt[0] and ts[0] is not None:
            try:
                timestamp_str = f"\nTime: {dt[0]:02d}/{dt[1]:02d}/20{dt[2]:02d} {ts[0]:02d}:{ts[1]:02d}:{int(ts[2]):02d}"
            except:
                timestamp_str = "\nTime: N/A"
        else:
            timestamp_str = "\nTime: N/A"

        # Use decimal format for maps link (no ° N/E)
        maps_link = f"http://maps.google.com/maps?q={lat},{lon}"
        
        return f"Location: {lat_str}, {lon_str}{timestamp_str}\nMap: {maps_link}"
    else:
        return "GPS signal not available. Please wait."


def print_debug_report():
    """Prints a live status report to the console."""
    print("\n")
    print("=" * 50)
    print("          SYSTEM DEBUG REPORT")
    print("=" * 50)
    print("\n[ System Status ]")
    print("-" * 50)
    print(f"GSM Module Initialized: {'Yes' if gsm_initialized else 'No'}")
    print(f"GSM Network Connected: {'Yes' if gsm_connected else 'No'}")
    print(f"GPS Fix Acquired: {'Yes' if gps_fix_acquired else 'No'}")
    
    print("\n[ GPS Information ]")
    print("-" * 50)
    if gps_fix_acquired and has_valid_gps_data():
        print(f"Latitude: {gps_parser.latitude_string()}")
        print(f"Longitude: {gps_parser.longitude_string()}")
        print(f"Satellites in use: {gps_parser.satellites_in_use}")
        ts = gps_parser.timestamp
        if ts[0] is not None:
            print(f"Time: {ts[0]:02d}:{ts[1]:02d}:{int(ts[2]):02d}")
    else:
        print("No GPS fix - waiting for satellites...")
    
    print("\n[ Location Tracking ]")
    print("-" * 50)
    time_since_last = time.ticks_diff(time.ticks_ms(), last_location_sent_ms)
    next_send = (LOCATION_INTERVAL_MS - time_since_last) // 1000
    print(f"Interval: {LOCATION_INTERVAL_MS // 60000} minute(s)")
    print(f"Last sent: {time_since_last // 1000} seconds ago")
    print(f"Next send: {max(0, next_send)} seconds")
    
    print("\n[ Hardware Info ]")
    print("-" * 50)
    print(f"GSM UART: TX=Pin{0}, RX=Pin{1}")
    print(f"GPS UART: TX=Pin{4}, RX=Pin{5}")
    print(f"Admin Number: {ADMIN_NUMBER}")
    
    print("\n" + "=" * 50 + "\n")

def check_serial_input():
    """Check for serial input in a MicroPython compatible way."""
    # Try to check if stdin has data using polling
    try:
        # Use sys.stdin with non-blocking read
        if hasattr(sys.stdin, 'read'):
            # This method works better on MicroPython
            return True
        return False
    except:
        return False

#=================================================
# ===== INITIALIZATION ===========================
#=================================================

print("\n" + "=" * 50)
print("  Vehicle Tracking System V5 for RPi Pico")
print("=" * 50)
print("\nInitializing...")

# Check if GSM module is responding
gsm_initialized = check_gsm_module()

if gsm_initialized:
    print("\nConfiguring GSM module for SMS...")
    send_at_command('ATE0', 500)        # Disable command echo
    send_at_command('AT+CMGF=1', 500)   # Set SMS to text mode
    send_at_command('AT+CNMI=2,1,0,0,0', 500) # Configure SMS delivery
    print("GSM configuration complete.")
else:
    print("\n⚠ WARNING: GSM module not detected!")
    print("The system will continue, but SMS features won't work.")
    print("Please check your wiring and power supply.\n")

print("\nSystem is running...")
print("Commands:")
print("  - Type 'x' for debug report")
print("  - Type 't' to test SMS")
print("  - Type 'l' to get location")
print("-" * 50)

#=================================================
# ===== MAIN LOOP ================================
#=================================================

input_buffer = ""

while True:
    try:
        current_time_ms = time.ticks_ms()

        # --- 1. Process GPS Data ---
        if gps_uart.any():
            data = gps_uart.read().decode('utf-8', 'ignore')
            for char in data:
                sentence = gps_parser.update(char)
                # Optional: Print when complete sentence is parsed
                # if sentence:
                #     print(f"Parsed: {sentence}")
        
        # Check for GPS fix using correct attribute (fix_type instead of fix_stat)
        # fix_type: 1 = no fix, 2 = 2D fix, 3 = 3D fix
        if not gps_fix_acquired and gps_parser.fix_type >= 2 and has_valid_gps_data():
            gps_fix_acquired = True
            gps_led.on()
            print(f"\n✓ GPS Fix Acquired! (Fix type: {gps_parser.fix_type}D)")
            if gsm_connected:
                send_sms(ADMIN_NUMBER, "GPS fix acquired. Vehicle tracking active.")
            
        # --- 2. Check GSM Network Connection ---
        if gsm_initialized and not gsm_connected:
            if time.ticks_diff(current_time_ms, last_gsm_check_ms) >= GSM_CHECK_INTERVAL_MS:
                response = send_at_command('AT+CREG?', 500, 2000)
                
                if '+CREG: 0,1' in response or '+CREG: 0,5' in response:
                    gsm_connected = True
                    gsm_led.on()
                    print("\n✓ GSM Network Connected!")
                    send_sms(ADMIN_NUMBER, "Vehicle Tracking System is online.")
                    last_location_sent_ms = current_time_ms
                elif '+CREG:' in response:
                    print("GSM not registered yet, will retry...")
                
                last_gsm_check_ms = current_time_ms

        # --- 3. Interval Location Reporting ---
        if gsm_connected and gps_fix_acquired and has_valid_gps_data():
            if time.ticks_diff(current_time_ms, last_location_sent_ms) >= LOCATION_INTERVAL_MS:
                location_message = get_current_location_string()
                send_sms(ADMIN_NUMBER, location_message)
                last_location_sent_ms = current_time_ms

        # --- 4. Check for Incoming SMS ---
        if gsm_uart.any():
            response = gsm_uart.read().decode('utf-8', 'ignore')
            if '+CMT:' in response:
                print(f"\nIncoming SMS: {response}")
                if 'location' in response.lower():
                    print("Location request via SMS")
                    location_message = get_current_location_string()
                    send_sms(ADMIN_NUMBER, location_message)

        # --- 5. Check for Console Commands (Simplified for MicroPython) ---
        # Note: Interactive input via REPL may be limited during runtime
        # Consider using a button or external trigger for commands in production
        try:
            # Simple polling approach for MicroPython
            # This may not work in all environments - use hardware buttons as alternative
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                char = sys.stdin.read(1)
                
                if char == '\n' or char == '\r':
                    # Process the command
                    cmd = input_buffer.strip().lower()
                    input_buffer = ""
                    
                    if cmd == 'x':
                        print_debug_report()
                    elif cmd == 't':
                        print("\nTesting SMS...")
                        send_sms(ADMIN_NUMBER, "Test message from Vehicle Tracker")
                    elif cmd == 'l':
                        print("\nCurrent Location:")
                        print(get_current_location_string())
                    elif cmd != '':
                        print(f"\nUnknown command: '{cmd}'")
                        print("Valid commands: x (debug), t (test SMS), l (location)")
                else:
                    input_buffer += char
        except:
            # If select is not available or fails, skip input checking
            pass
        
        # Small delay
        time.sleep_ms(50)
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        break
    except Exception as e:
        print(f"\nError in main loop: {e}")
        time.sleep_ms(500)

print("System stopped.")
