import curatedTweets from "../../data/curated_tweets.json";

export const POSTS = Object.freeze(
  (curatedTweets.tweets ?? [])
    .filter((tweet) => tweet?.text?.trim())
    .map((tweet, index) =>
      Object.freeze({
        id: tweet.id ?? `${index}-${tweet.text}`,
        text: tweet.text.trim(),
        date: tweet.timestamp ?? null,
        tag: tweet.with_url === "yes" ? "with_url" : "no_url",
      }),
    ),
);

export const FILTERS = Object.freeze(["all", "with_url", "no_url"]);

export function getQuoteLength(text) {
  if (text.length > 72) return "long";
  if (text.length > 34) return "medium";
  return "short";
}

export function formatTimestamp(date) {
  return date === "Oct 18, 2010" ? "6:59 PM · 10/18/10" : date;
}
