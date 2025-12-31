
import psutil
import os
import signal

def kill_django():
    print("Searching for Django server...")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'manage.py' in cmdline and 'runserver' in cmdline:
                print(f"Found Server: PID={proc.info['pid']} {proc.info['name']}")
                print(f"Command: {cmdline}")
                proc.kill()
                print("Killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == "__main__":
    kill_django()
