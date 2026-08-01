import curatedTweets from "../../data/curated_tweets.json";

function shuffle(items) {
  const result = [...items];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
  }
  return result;
}

function buildOrderedPosts(tweets) {
  const regularTweets = shuffle(
    tweets.filter((tweet) => tweet?.text?.trim() && !tweet.highlight),
  );
  const highlightedTweets = shuffle(
    tweets.filter((tweet) => tweet?.text?.trim() && tweet.highlight),
  );

  const orderedTweets = [];
  let regularIndex = 0;
  let highlightIndex = 0;

  while (regularIndex < regularTweets.length || highlightIndex < highlightedTweets.length) {
    const batchSize = 2 + (Math.random() < 0.5 ? 0 : 1);
    const nextBatch = regularTweets.slice(regularIndex, regularIndex + batchSize);
    orderedTweets.push(...nextBatch);
    regularIndex += nextBatch.length;

    if (highlightIndex < highlightedTweets.length) {
      orderedTweets.push(highlightedTweets[highlightIndex]);
      highlightIndex += 1;
    }
  }

  return orderedTweets;
}

export const POSTS = Object.freeze(
  buildOrderedPosts(curatedTweets.tweets ?? [])
    .filter((tweet) => tweet?.text?.trim())
    .map((tweet, index) =>
      Object.freeze({
        id: tweet.id ?? `${index}-${tweet.text}`,
        text: tweet.text.trim(),
        date: tweet.timestamp ?? null,
        tag: tweet.with_url === "yes" ? "with_url" : "no_url",
        highlight: Boolean(tweet.highlight),
      }),
    ),
);

export const FILTERS = Object.freeze(["all"]);

export function getQuoteLength(text) {
  if (text.length > 72) return "long";
  if (text.length > 34) return "medium";
  return "short";
}

export function formatTimestamp(date) {
  return date === "Oct 18, 2010" ? "6:59 PM · 10/18/10" : date;
}
