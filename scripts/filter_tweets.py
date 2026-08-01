import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_FILES = [
    ROOT / "scripts" / "all_tweets.json",
    ROOT / "scripts" / "tweets.json",
]
OUTPUT_PATH = ROOT / "data" / "curated_tweets.json"

BLOCKED_TERMS = [
    "SKF_Music",
    "Being Human Clothing",
    "Being Human",
    "bebeinghuman",
    "Chingari",
    "Book Now",
    "ZEE5India",
    "k_satyarthi",
]

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

MEMORABLE_KEYWORDS = [
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
    "jeet",
    "haar",
    "dil se",
    "khud se",
    "matlab",
    "aisa",
    "let it go",
    "aapna",
    "lene dena",
    "does nt matter",
    "doesn't matter",
]


def load_raw_items():
    items = []
    for path in RAW_FILES:
        if not path.exists():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for key in ("tweets", "data", "results", "items"):
                value = raw.get(key)
                if isinstance(value, list):
                    items.extend(value)
                    break
        elif isinstance(raw, list):
            items.extend(raw)
    return items


def clean_text(value):
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    text = re.sub(r"(?<!\S)(@\w[\w.]*)\s+(https?://|www\.)\S+", r"\1", text)
    text = re.sub(r"(https?://|www\.)\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return text.strip()


def contains_blocked(text):
    lowered = text.lower()
    return any(term.lower() in lowered for term in BLOCKED_TERMS)


def is_movie_related(text):
    lowered = text.lower()
    return any(keyword in lowered for keyword in MOVIE_KEYWORDS)


def has_url(text):
    return bool(re.search(r"https?://\S+|www\.\S+", text))


def score_tweet(text, likes):
    lowered = text.lower()
    score = 0
    if any(keyword in lowered for keyword in MEMORABLE_KEYWORDS):
        score += 8
    if "?" in text or "!" in text:
        score += 2
    if 20 <= len(text) <= 140:
        score += 2
    if 40 <= len(text) <= 140:
        score += 2
    if any(marker in lowered for marker in ["doesn't matter", "does nt matter", "matters", "khud", "sukh", "dil", "darr"]):
        score += 4
    if len(text.split()) <= 12:
        score += 1
    score += min(6, int(likes or 0) // 10000)
    return score


def build_curated_tweets():
    items = load_raw_items()
    curated = []
    seen = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        raw_text = (
            item.get("text")
            or item.get("full_text")
            or item.get("content")
            or item.get("description")
            or item.get("body")
            or ""
        )
        text = clean_text(raw_text)
        if not text:
            continue
        if contains_blocked(text) or is_movie_related(text):
            continue

        timestamp = str(
            item.get("timestamp")
            or item.get("created_at")
            or item.get("date")
            or item.get("date_posted")
            or ""
        ).strip()
        likes = item.get("likes") or item.get("like_count") or item.get("favorite_count") or 0
        retweets = item.get("retweets") or item.get("retweet_count") or item.get("reposts") or 0
        replies = item.get("replies") or item.get("reply_count") or 0
        views = item.get("views") or item.get("view_count") or 0

        key = (text, timestamp)
        if key in seen:
            continue
        seen.add(key)

        entry = {
            "text": text,
            "timestamp": timestamp,
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "views": views,
            "with_url": "yes" if has_url(raw_text) else "no",
        }
        entry["_score"] = score_tweet(text, likes)
        curated.append(entry)

    curated = sorted(curated, key=lambda entry: (entry["_score"], int(entry.get("likes") or 0)), reverse=True)[:250]
    for entry in curated:
        entry.pop("_score", None)

    payload = {
        "source": "https://x.com/BeingSalmanKhan",
        "year_range": "mixed",
        "count": len(curated),
        "tweets": curated,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = build_curated_tweets()
    print(f"Wrote {payload['count']} curated tweets to {OUTPUT_PATH}")
