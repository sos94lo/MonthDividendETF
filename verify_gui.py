import os
import time
import tkinter as tk
from main_gui import ETFApp
import sys

def run_app():
    root = tk.Tk()
    app = ETFApp(root)
    # Force update to render
    root.update()

    # Wait longer for data fetch (network call)
    print("Waiting for data load...")
    time.sleep(10)
    root.update()

    # Take screenshot using scrot (external tool)
    if not os.path.exists("verification"):
        os.makedirs("verification")
    os.system("scrot verification/final_run_retry.png")
    print("Screenshot taken.")

    root.destroy()

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
