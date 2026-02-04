from playwright.sync_api import sync_playwright, expect
import time

def verify_etf_table():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the app
            page.goto("http://127.0.0.1:5000/")

            # Wait for title
            expect(page.get_by_role("heading", name="Monthly Dividend ETF Tracker")).to_be_visible()

            # Check for table
            table = page.locator("table")
            expect(table).to_be_visible()

            # Check for rows
            rows = table.locator("tbody tr")
            # Wait for at least one row
            expect(rows.first).to_be_visible()

            count = rows.count()
            print(f"Found {count} rows in the table.")

            # Check for specific data (JEPI)
            expect(page.get_by_text("JEPI")).to_be_visible()

            # Take screenshot
            page.screenshot(path="verification/app_screenshot.png")
            print("Screenshot saved to verification/app_screenshot.png")

        except Exception as e:
            print(f"Verification failed: {e}")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_etf_table()
