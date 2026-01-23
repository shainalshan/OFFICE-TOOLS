import PyInstaller.__main__
import os

# Install requirements first: pip install pyinstaller
# Run this script to generate execution file

PyInstaller.__main__.run([
    'device_tracker/agent.py',
    '--onefile',
    '--name=DeviceMonitor',
    '--hidden-import=psutil',
    '--hidden-import=requests',
    '--noconsole' # Comment out for debugging
])
