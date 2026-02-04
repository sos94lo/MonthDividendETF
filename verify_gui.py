import os
import time
import tkinter as tk
from main_gui import ETFApp
import sys

def run_app():
    print("Initializing Application...")
    root = tk.Tk()
    app = ETFApp(root)

    # Force update to render
    root.update()
    print("Application Window Created.")

    # Wait for data load (simulating user waiting)
    print("Fetching Data (via yfinance)...")
    time.sleep(5)
    root.update()

    # Inspect the Treeview content
    print("\n--- [UI STATE INSPECTION] ---")
    children = app.tree.get_children()
    print(f"Found {len(children)} rows in List Control.")

    if len(children) == 0:
        print("ERROR: List Control is empty!")

    for i, child in enumerate(children):
        values = app.tree.item(child)['values']
        # Print first few columns to verify data
        print(f"Row {i+1}: Ticker={values[0]}, Name={values[1]}, Price={values[6]}, Yield(1m)={values[9]}")

    print("-----------------------------\n")

    # Take screenshot using scrot (external tool)
    if not os.path.exists("verification"):
        os.makedirs("verification")

    screenshot_path = "verification/proof_of_run.png"
    os.system(f"scrot {screenshot_path}")
    print(f"Screenshot taken at {screenshot_path}")

    root.destroy()
    print("Application Closed.")

if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
