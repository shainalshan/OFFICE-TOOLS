import tkinter as tk
from tkinter import filedialog
import sys

def browse_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring dialog to front
    
    folder_path = filedialog.askdirectory()
    
    if folder_path:
        print(folder_path)
    
    root.destroy()

if __name__ == "__main__":
    browse_folder()
