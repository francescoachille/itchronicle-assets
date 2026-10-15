# Cloudflare Worker Security Boilerplate
*Production-ready edge serverless micro-proxy for secure lead generation forms.*

## Features
- **Strict Enterprise CORS:** Whitelist matching for domain, subdomains, and staging environments.
- **Honeypot Trap:** Rejects automated bot submissions with zero CPU latency.
- **RFC Email Verification:** Validates email strings before dispatching costly upstream calls.
- **Secret Isolation:** Uses Cloudflare Secret Storage for `BREVO_API_KEY`.
- **IP Rate Limiting:** Optional Cloudflare KV binding support to throttle repeat submissions.

## Quick Deployment
1. Install Wrangler CLI: `npm install -g wrangler`
2. Authenticate: `wrangler login`
3. Store your Brevo Secret:
   ```bash
   wrangler secret put BREVO_API_KEY
   ```
4. Deploy to Cloudflare Edge:
   ```bash
   wrangler deploy
   ```
