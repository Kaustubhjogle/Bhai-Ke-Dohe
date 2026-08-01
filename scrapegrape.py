import json
import os
import re
from pathlib import Path

from scrapegraph_py import ScrapeGraphAI

API_KEY = os.getenv("SCRAPEGRAPH_API_KEY")
TARGET_URL = "https://x.com/BeingSalmanKhan"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "filtered_tweets.json"
FALLBACK_TWEETS_PATHS = [
    Path(__file__).resolve().parent / "tweets.json",
    Path(__file__).resolve().parent / "all_tweets.json",
    Path(__file__).resolve().parent.parent / "data" / "all_tweets.json",
    Path(__file__).resolve().parent.parent / "data" / "tweets.json",
]
MAX_TWEETS = 1000

MOVIE_KEYWORDS = [
    "movie",
    "movies",
    "film",
    "films",
    "trailer",
    "trailers",
    "teaser",
    "release",
    "releases",
    "premiere",
    "cinema",
    "theatre",
    "box office",
    "shooting",
    "actor",
    "actress",
    "director",
    "review",
    "launch",
    "launches",
    "award",
    "awards",
    "festival",
    "promotion",
    "promotional",
]


def is_movie_related(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in MOVIE_KEYWORDS)


def extract_year(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\b(20\d{2})\b", str(value))
    return int(match.group(1)) if match else None


def is_in_year_range(tweet: dict) -> bool:
    for key in ("timestamp", "created_at", "date", "datetime"):
        year = extract_year(tweet.get(key))
        if year is not None:
            return 2024 <= year <= 2026
    return False


def clean_tweet(tweet: dict) -> dict:
    text = (
        tweet.get("text")
        or tweet.get("full_text")
        or tweet.get("content")
        or tweet.get("description")
        or tweet.get("body")
        or ""
    )
    timestamp = (
        tweet.get("timestamp")
        or tweet.get("created_at")
        or tweet.get("date")
        or tweet.get("date_posted")
        or ""
    )
    likes = tweet.get("likes") or tweet.get("like_count") or tweet.get("favorite_count") or 0
    retweets = tweet.get("retweets") or tweet.get("retweet_count") or tweet.get("reposts") or 0
    replies = tweet.get("replies") or tweet.get("reply_count") or 0
    views = tweet.get("views") or tweet.get("view_count") or 0

    return {
        "text": str(text).strip(),
        "timestamp": str(timestamp).strip(),
        "likes": likes,
        "retweets": retweets,
        "replies": replies,
        "views": views,
    }


def score_tweet(tweet: dict) -> int:
    text = str(tweet.get("text") or tweet.get("full_text") or tweet.get("content") or "").strip()
    lowered = text.lower()
    score = 0

    memorable_keywords = [
        "yaar",
        "baba",
        "alone",
        "lonely",
        "khud",
        "dil",
        "darr",
        "haan",
        "nahi",
        "nahin",
        "matters",
        "zindagi",
        "jindagi",
        "duniya",
        "family",
        "friends",
        "hmm",
        "kabhi",
        "bhool",
        "gaya",
        "gya",
        "samajh",
        "soch",
        "sukh",
        "duniya",
        "jeet",
        "haar",
        "dil se",
        "khud se",
        "matlab",
    ]

    if any(keyword in lowered for keyword in memorable_keywords):
        score += 6
    if "?" in text or "!" in text:
        score += 2
    if len(text) > 20 and len(text) < 140:
        score += 2
    if len(text) > 40 and len(text) < 140:
        score += 2
    if any(marker in lowered for marker in ["doesn't matter", "does nt matter", "matters", "khud", "sukh", "dil", "darr"]):
        score += 4

    likes = int(tweet.get("likes") or tweet.get("like_count") or tweet.get("favorite_count") or 0)
    score += min(6, likes // 10000)

    return score


def load_tweets_from_scrapegraph() -> list[dict]:
    if not API_KEY:
        raise RuntimeError("SCRAPEGRAPH_API_KEY is not set in the environment")

    try:
        sgai = ScrapeGraphAI(api_key=API_KEY)
        response = sgai.extract(
            url=TARGET_URL,
            prompt=(
                "Extract tweets from this profile page from the years 2024 through 2026. "
                "Prioritize tweets that feel funniest, weirdest, wisest, or most unforgettable. "
                "Skip tweets that mention movies, trailers, launches, releases, premieres, or any other film-related information. "
                "Return up to 300 tweets with full text, timestamp, like count, retweet count, reply count, and view count."
            ),
        )

        raw_tweets: list[dict] = []
        if getattr(response, "data", None) is not None:
            payload = response.data.json_data or {}
            if isinstance(payload, dict):
                if isinstance(payload.get("tweets"), list):
                    raw_tweets = payload["tweets"]
                elif isinstance(payload.get("data"), list):
                    raw_tweets = payload["data"]
                elif isinstance(payload.get("items"), list):
                    raw_tweets = payload["items"]
                else:
                    raw_tweets = []
            elif isinstance(payload, list):
                raw_tweets = payload
        return raw_tweets
    except Exception as exc:
        print(f"ScrapeGraphAI failed: {exc}")
        return []


def load_fallback_tweets() -> list[dict]:
    tweets: list[dict] = []
    seen_keys = set()

    for path in FALLBACK_TWEETS_PATHS:
        if not path.exists():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Fallback tweet file could not be read: {path} -> {exc}")
            continue

        if isinstance(data, dict):
            candidates = []
            for key in ("tweets", "data", "results", "items"):
                if isinstance(data.get(key), list):
                    candidates = data[key]
                    break
            if candidates:
                items = candidates
            else:
                continue
        elif isinstance(data, list):
            items = data
        else:
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            key = (
                str(item.get("text") or item.get("full_text") or item.get("content") or item.get("description") or "").strip(),
                str(item.get("timestamp") or item.get("created_at") or item.get("date") or item.get("date_posted") or ""),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            tweets.append(item)

    return tweets


def main() -> None:
    raw_tweets = load_tweets_from_scrapegraph()
    fallback_tweets = load_fallback_tweets()

    if not raw_tweets and fallback_tweets:
        print("ScrapeGraphAI returned no usable data; using local tweet archive as fallback.")
    elif raw_tweets and fallback_tweets:
        raw_tweets = raw_tweets + fallback_tweets

    combined_tweets = raw_tweets or fallback_tweets

    filtered_tweets = []
    seen_keys = set()
    for tweet in combined_tweets:
        if not isinstance(tweet, dict):
            continue

        text = (tweet.get("text") or tweet.get("full_text") or tweet.get("content") or tweet.get("description") or "").strip()
        if not text or is_movie_related(text):
            continue
        if not is_in_year_range(tweet):
            continue

        key = (text, str(tweet.get("timestamp") or tweet.get("created_at") or tweet.get("date") or tweet.get("date_posted") or ""))
        if key in seen_keys:
            continue
        seen_keys.add(key)

        filtered_tweets.append(clean_tweet(tweet))

    filtered_tweets = sorted(
        filtered_tweets,
        key=lambda tweet: (score_tweet(tweet), int(tweet.get("likes") or 0)),
        reverse=True,
    )[:MAX_TWEETS]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": TARGET_URL,
        "year_range": "2024-2026",
        "count": len(filtered_tweets),
        "tweets": filtered_tweets,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {len(filtered_tweets)} filtered tweets to {OUTPUT_PATH}")
    for tweet in filtered_tweets:
        print(
            f"{tweet['timestamp']} | {tweet['text'][:90]}{'...' if len(tweet['text']) > 90 else ''} | "
            f"{tweet['likes']} likes"
        )


if __name__ == "__main__":
    main()
