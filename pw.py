import json
from playwright.sync_api import sync_playwright

def load_cookies_and_scrape(username):
    # 1. Load the raw cookies from the extension export
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
        
    # 2. Clean up extension-specific keys that Playwright doesn't accept
    for cookie in cookies:
        if 'hostOnly' in cookie: del cookie['hostOnly']
        if 'session' in cookie: del cookie['session']
        if 'storeId' in cookie: del cookie['storeId']
        if 'id' in cookie: del cookie['id']
        
        # Playwright requires the 'sameSite' attribute to be a specific string format
        if 'sameSite' in cookie and cookie['sameSite'] == 'no_restriction':
            cookie['sameSite'] = 'None'

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # 3. Inject your real browser's cookies into Playwright
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        # You are now fully authenticated without ever logging in via Playwright!
        page.goto(f"https://x.com/{username}")
        
        # ... (rest of your scraping logic goes here) ...