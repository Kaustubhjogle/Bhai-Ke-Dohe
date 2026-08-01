# Bhai Ke Dohe

## Fetch the X archive

1. Revoke the credentials that were shared in chat and create a replacement Bearer token in the X Developer Portal.
2. Copy `.env.example` to `.env`.
3. Set `X_BEARER_TOKEN` in `.env`.
4. Run:

   ```bash
   npm run fetch:tweets
   ```

The script resolves `@beingsalmankhan`, requests pages of up to 100 posts from the official X API, and stores the result in `data/beingsalmankhan-tweets.json`. The JSON archive is ignored by Git so fetched content and local credentials do not get committed.

Your X access plan controls how much historical data the API returns. The script requests every page the API makes available.
