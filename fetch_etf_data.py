from playwright.sync_api import sync_playwright
import json
import time
import os

def fetch_and_save_etf_data():
    # Credentials from environment variables or placeholders
    # USER MUST SET THESE OR REPLACE THEM
    LOGIN_ID = os.getenv("ETF_LOGIN_ID", "YOUR_EMAIL@gmail.com")
    LOGIN_PW = os.getenv("ETF_LOGIN_PW", "YOUR_PASSWORD")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a larger viewport to ensure elements are clickable
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # 1. Navigate to Login Page
        login_url = "https://search-etf.com/bbs/login.php"
        print(f"Navigating to {login_url}...")
        page.goto(login_url)

        # 2. Handle Cookie Popup
        try:
            cookie_btn = page.locator(".dol_cookie_accept_all")
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
                print("Clicked 'Agree All' cookies.")
                time.sleep(1)
        except Exception as e:
            print(f"Cookie handling note: {e}")

        # 3. Open Admin/ID Login Popup
        print("Attempting to open Admin/ID login popup...")
        try:
            # The gear icon button
            admin_btn = page.locator(".login-admin-btn")
            if admin_btn.is_visible():
                admin_btn.click()
                print("Clicked admin login button.")
            else:
                # Fallback: maybe execute the function directly if button isn't clickable
                print("Admin button not found/visible, trying JS trigger...")
                page.evaluate("openAdminPopup()")

            # Wait for popup
            popup = page.locator("#adminPopupOverlay")
            popup.wait_for(state="visible", timeout=5000)
            print("Login popup is visible.")

            # 4. Fill Credentials
            # ID Field
            id_field = page.locator("#admin_id")
            id_field.click()
            id_field.fill("") # Clear default 'admin'
            id_field.fill(LOGIN_ID)
            print("Filled ID.")

            # Password Field
            pw_field = page.locator("#admin_password")
            pw_field.click()
            pw_field.fill(LOGIN_PW)
            print("Filled Password.")

            # 5. Submit
            submit_btn = page.locator("#adminLoginBtn")
            submit_btn.click()
            print("Clicked Login.")

            # Wait for navigation or error
            page.wait_for_load_state("networkidle", timeout=10000)
            print(f"Post-login URL: {page.url}")

            # Check for alerts or reCAPTCHA warnings
            # Note: We can't solve reCAPTCHA, but we can see if it blocked us.

        except Exception as e:
            print(f"Login interaction failed: {e}")

        # 4. Fetch Data (Attempt regardless, maybe cookie set?)
        data_url = "https://search-etf.com/backend/total/download_etf_list.php?format=json&sortBy=etftotcap&sortOrder=DESC"
        print(f"Navigating to data URL: {data_url}")

        try:
            response = page.goto(data_url)
            inner_text = page.locator("body").inner_text()

            try:
                json_data = json.loads(inner_text)
                if isinstance(json_data, dict) and json_data.get("status") == "error":
                     print("Login Error from server:", json_data.get("message"))
                     # Check if it mentions captcha
                     if "reCAPTCHA" in inner_text or "captcha" in inner_text.lower():
                         print("Blocked by reCAPTCHA.")
                else:
                     count = len(json_data) if isinstance(json_data, list) else len(json_data.get('data', []))
                     print(f"Successfully parsed JSON. Items: {count}")
                     with open("etf_data.json", "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                print("JSON Decode Error.")
                print("Snippet:", inner_text[:200])

        except Exception as e:
            print(f"Data fetch failed: {e}")

        browser.close()

if __name__ == "__main__":
    fetch_and_save_etf_data()
