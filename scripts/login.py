from playwright.sync_api import sync_playwright

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://x.com/login")
        print("Please log into your X account in the opened browser window.")
        print("Once you are fully logged in and see your timeline, press Enter in this terminal.")
        
        input("Press Enter here after logging in...")
        
        # Save the authenticated state (cookies/storage) to a file
        context.storage_state(path="auth.json")
        print("Authentication saved to auth.json!")
        
        browser.close()

if __name__ == "__main__":
    save_login_state()