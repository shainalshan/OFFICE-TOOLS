import psutil
import requests
import platform
import time
import json
import socket
import logging

# CONFIGURATION
SERVER_URL = "http://127.0.0.1:8000/tracker/heartbeat/" # Change this to real server IP
INTERVAL = 5 # Seconds

def get_serial_number():
    """Get Serial Number based on OS. Requires Admin/Root typically."""
    os_name = platform.system()
    try:
        if os_name == "Windows":
            import subprocess
            cmd = "wmic bios get serialnumber"
            output = subprocess.check_output(cmd, shell=True).decode()
            return output.split('\n')[1].strip()
        elif os_name == "Darwin": # Mac
            import subprocess
            cmd = "ioreg -l | grep IOPlatformSerialNumber"
            output = subprocess.check_output(cmd, shell=True).decode()
            return output.split('"')[-2]
        else:
            return "UNKNOWN"
    except:
        return f"UNKNOWN-{socket.gethostname()}"

def main():
    hostname = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()}"
    serial = get_serial_number()
    
    print(f"Starting Agent for: {hostname} ({serial})")
    print(f"Target: {SERVER_URL}")

    while True:
        try:
            # Gather Stats
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            
            payload = {
                'serial_number': serial,
                'hostname': hostname,
                'os_info': os_info,
                'cpu_percent': cpu,
                'memory_percent': mem,
                'battery_percent': battery.percent if battery else None,
                'is_charging': battery.power_plugged if battery else False
            }
            
            # Send Data
            requests.post(SERVER_URL, json=payload, timeout=3)
            # print(f"Sent: {payload}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
