import json
import time
import random
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

# --- GLOBAL VARIABLES ---
BASE_DIR = Path(__file__).resolve().parent
TWEETS_FILE = str(BASE_DIR / "all_tweets.json")
scraped_tweets = {}
is_rate_limited = False
MAX_SCROLLS = 1200
MAX_STAGNATION = 60
TARGET_OLDEST_YEAR = 2013

# --- HELPER FUNCTIONS ---

def load_existing_tweets():
    """Loads existing tweets from file so you can resume scraping if stopped."""
    global scraped_tweets
    if os.path.exists(TWEETS_FILE):
        try:
            with open(TWEETS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                scraped_tweets = {tweet['tweet_id']: tweet for tweet in data}
                print(f"[+] Resumed with {len(scraped_tweets)} existing tweets.")
        except Exception:
            print("[-] Could not read existing tweets file, starting fresh.")

def save_tweets():
    """Autosaves tweets instantly to prevent data loss."""
    with open(TWEETS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(scraped_tweets.values()), f, indent=4, ensure_ascii=False)

def load_and_clean_cookies(filepath="cookies.json"):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_cookies = json.load(f)
    
    cleaned_cookies = []
    for c in raw_cookies:
        cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/")
        }
        if "expirationDate" in c: cookie["expires"] = c["expirationDate"]
        if "secure" in c: cookie["secure"] = c["secure"]
        if "httpOnly" in c: cookie["httpOnly"] = c["httpOnly"]
        if "sameSite" in c:
            val = c["sameSite"].lower()
            if val == "no_restriction": cookie["sameSite"] = "None"
            elif val in ["lax", "strict"]: cookie["sameSite"] = val.capitalize()
        cleaned_cookies.append(cookie)
    return cleaned_cookies

def extract_tweet_data(json_response):
    global scraped_tweets
    new_tweets_found = 0
    try:
        user_data = json_response.get('data', {}).get('user', {})
        if not user_data:
            user_data = json_response.get('data', {}).get('user_result_by_screen_name', {})
            
        timeline = user_data.get('result', {}).get('timeline_v2', {}).get('timeline', {})
        if not timeline:
            timeline = user_data.get('result', {}).get('timeline', {}).get('timeline', {})
            
        instructions = timeline.get('instructions', [])
        
        for instruction in instructions:
            if instruction.get('type') == 'TimelineAddEntries':
                for entry in instruction.get('entries', []):
                    if 'tweet' in entry.get('entryId', ''):
                        item = entry.get('content', {}).get('itemContent', {}).get('tweet_results', {}).get('result', {})
                        
                        if 'tweet' in item: item = item['tweet']
                        legacy = item.get('legacy')
                        
                        if legacy:
                            tweet_id = legacy.get("id_str")
                            if tweet_id and tweet_id not in scraped_tweets:
                                scraped_tweets[tweet_id] = {
                                    "tweet_id": tweet_id,
                                    "created_at": legacy.get("created_at"),
                                    "text": legacy.get("full_text"),
                                    "likes": legacy.get("favorite_count"),
                                    "retweets": legacy.get("retweet_count"),
                                    "replies": legacy.get("reply_count"),
                                    "views": item.get("views", {}).get("count")
                                }
                                new_tweets_found += 1
                                
        if new_tweets_found > 0:
            save_tweets()
            
    except Exception:
        pass

def handle_response(response):
    global is_rate_limited
    if "graphql" in response.url and "UserTweets" in response.url:
        if response.status == 200:
            is_rate_limited = False
            try:
                extract_tweet_data(response.json())
            except Exception:
                pass
        elif response.status == 429:
            is_rate_limited = True
            print("\n[!] RATE LIMIT (429) DETECTED! X is throttling us.")

def jiggle_scroll(page):
    """Tricks the UI into rendering if it gets stuck."""
    print("[*] Jiggling the scroll to force UI refresh...")
    page.evaluate("window.scrollBy(0, -1500);")
    time.sleep(random.uniform(1.5, 2.5))
    page.evaluate("window.scrollBy(0, 2000);")

def smooth_scroll(page):
    """Simulates a human scrolling down."""
    for _ in range(4):
        page.evaluate("window.scrollBy(0, 900);")
        time.sleep(random.uniform(0.5, 1.2))


def get_tweet_year(tweet):
    created_at = tweet.get("created_at") or ""
    try:
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").year
    except Exception:
        return None


# --- MAIN EXECUTION ---

def scrape_all(username):
    global is_rate_limited
    load_existing_tweets()
    
    with sync_playwright() as p:
        # Launch with stealth arguments
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        # Mac-specific User Agent to match your actual machine
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        cookies = load_and_clean_cookies("cookies.json")
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.on("response", handle_response)
        
        try:
            # 1. Warm-up: Load the home page first so X thinks you just opened the app normally
            print("Warming up browser: Loading home feed first...")
            page.goto("https://x.com/home", timeout=60000)
            page.wait_for_timeout(random.randint(3000, 5000))
            
            # 2. Navigate to the actual profile you want
            print(f"Navigating to {username}'s profile...")
            page.goto(f"https://x.com/{username}", timeout=60000)
            
            page.wait_for_selector("article[data-testid='tweet']", timeout=20000)
            
        except TimeoutError:
            print("\n[-] Timeout Error: X blocked the page load ('Something went wrong').")
            print("[!] Fix: You are still in X's penalty box. Wait 15 minutes, browse X manually in Chrome, export fresh cookies, and try again.")
            browser.close()
            return

        previous_height = 0
        stuck_count = 0
        scroll_count = 0
        
        print("Starting extended scroll to collect older tweets. Press CTRL+C to stop at any time.")
        
        while scroll_count < MAX_SCROLLS:
            try:
                # 429 MITIGATION
                if is_rate_limited:
                    wait_time = random.randint(70, 120)
                    print(f"⏳ Sleeping for {wait_time} seconds to clear X's penalty...")
                    time.sleep(wait_time)
                    is_rate_limited = False
                    jiggle_scroll(page)
                    continue

                smooth_scroll(page)
                time.sleep(random.uniform(4.0, 7.0))
                
                new_height = page.evaluate("document.body.scrollHeight")
                
                if new_height == previous_height:
                    stuck_count += 1
                    jiggle_scroll(page)
                    
                    if stuck_count >= MAX_STAGNATION:
                        print("\n[+] Reached a stable bottom of the timeline; stopping scroll.")
                        break
                else:
                    stuck_count = 0
                
                previous_height = new_height
                scroll_count += 1
                oldest_year = min((get_tweet_year(tweet) for tweet in scraped_tweets.values() if get_tweet_year(tweet) is not None), default=None)
                print(f"Scroll {scroll_count}/{MAX_SCROLLS} | Total Unique Tweets Saved: {len(scraped_tweets)} | Oldest Year: {oldest_year}", end="\r")

                if oldest_year is not None and oldest_year <= TARGET_OLDEST_YEAR:
                    print("\n[+] Reached the target oldest year range; stopping.")
                    break

            except KeyboardInterrupt:
                print("\n[+] Manual stop triggered. Saving and exiting safely...")
                break
            except Exception as e:
                print(f"\n[-] Unexpected scroll error: {e}")
                jiggle_scroll(page)
                time.sleep(5)

        browser.close()
        print(f"\n✅ Finished! {len(scraped_tweets)} total tweets saved to {TWEETS_FILE}")

# Start the script!
if __name__ == "__main__":
    scrape_all("BeingSalmanKhan")