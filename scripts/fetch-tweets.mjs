import { mkdir, rename, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const username = 'beingsalmankhan';
const baseUrl = 'https://api.twitter.com/2';
const bearerToken = process.env.X_BEARER_TOKEN;
const outputPath = resolve('data', `${username}-tweets.json`);

if (!bearerToken || bearerToken === 'replace_with_a_newly_generated_bearer_token') {
  throw new Error('Missing X_BEARER_TOKEN. Copy .env.example to .env and add a valid Bearer token.');
}

async function xFetch(path, searchParams = {}) {
  const url = new URL(`${baseUrl}${path}`);
  for (const [key, value] of Object.entries(searchParams)) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value);
  }

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${bearerToken}` },
  });
  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = body?.detail || body?.title || JSON.stringify(body);
    throw new Error(`X API request failed (${response.status}): ${detail}`);
  }
  return body;
}

async function getUser() {
  const result = await xFetch(`/users/by/username/${username}`, {
    'user.fields': 'id,name,username,created_at,description,profile_image_url',
  });
  if (!result.data) throw new Error(`X did not return a user record for @${username}.`);
  return result.data;
}

async function getAllTweets(userId) {
  const tweets = [];
  let paginationToken;
  let page = 0;

  do {
    page += 1;
    const result = await xFetch(`/users/${userId}/tweets`, {
      max_results: '100',
      pagination_token: paginationToken,
      'tweet.fields': 'id,text,created_at,conversation_id,lang,public_metrics,entities,referenced_tweets,attachments',
      expansions: 'attachments.media_keys',
      'media.fields': 'media_key,type,url,preview_image_url,alt_text,width,height',
    });

    const pageTweets = result.data ?? [];
    tweets.push(...pageTweets);
    paginationToken = result.meta?.next_token;
    console.log(`Fetched page ${page}: ${pageTweets.length} posts (${tweets.length} total)`);
  } while (paginationToken);

  return { tweets, pages: page };
}

async function writeArchive(user, tweets, pages) {
  const archive = {
    fetchedAt: new Date().toISOString(),
    source: `https://x.com/${username}`,
    user,
    meta: { pages, totalPosts: tweets.length },
    tweets,
  };

  await mkdir(dirname(outputPath), { recursive: true });
  const temporaryPath = `${outputPath}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify(archive, null, 2)}\n`, 'utf8');
  await rename(temporaryPath, outputPath);
  console.log(`Saved ${tweets.length} posts to ${outputPath}`);
}

const user = await getUser();
const { tweets, pages } = await getAllTweets(user.id);
await writeArchive(user, tweets, pages);
