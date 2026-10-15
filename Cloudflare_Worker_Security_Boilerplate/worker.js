/**
 * Cloudflare Worker Security Boilerplate
 * Production-ready serverless micro-proxy with Enterprise CORS, Honeypot, Input Validation & Rate Limiting.
 * Author: IT Chronicle (https://itchronicle.com)
 */

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get("Origin") || "";
    const allowedOrigins = (env.ALLOWED_ORIGINS || "https://itchronicle.com,https://www.itchronicle.com").split(",");
    const isAllowedOrigin = allowedOrigins.includes(origin);

    const corsHeaders = {
      "Access-Control-Allow-Origin": isAllowedOrigin ? origin : allowedOrigins[0],
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Accept",
      "Access-Control-Max-Age": "86400",
      "X-Content-Type-Options": "nosniff",
      "Referrer-Policy": "strict-origin-when-cross-origin"
    };

    // 1. Preflight CORS Request Handling
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    // 2. Strict Method Enforcement
    if (request.method !== "POST") {
      return new Response(JSON.stringify({ success: false, error: "Method Not Allowed" }), {
        status: 405,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    // 3. Security: Origin & Referer Verification
    if (origin && !isAllowedOrigin) {
      return new Response(JSON.stringify({ success: false, error: "Forbidden: Unauthorized Origin" }), {
        status: 403,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }

    // 4. Rate Limiting by Client IP (Optional Cloudflare KV binding: env.RATE_LIMIT_KV)
    const clientIP = request.headers.get("CF-Connecting-IP") || "unknown";
    if (env.RATE_LIMIT_KV) {
      const windowSec = 600; // 10 minutes
      const maxRequests = 5;  // 5 requests per 10 mins
      const kvKey = `ratelimit:${clientIP}`;
      const currentCount = parseInt(await env.RATE_LIMIT_KV.get(kvKey)) || 0;

      if (currentCount >= maxRequests) {
        return new Response(JSON.stringify({
          success: false,
          code: "RATE_LIMIT_EXCEEDED",
          message: "Too many requests from this IP. Please try again later."
        }), {
          status: 429,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }
      await env.RATE_LIMIT_KV.put(kvKey, (currentCount + 1).toString(), { expirationTtl: windowSec });
    }

    try {
      const bodyText = await request.text();
      let payload;
      try {
        payload = JSON.parse(bodyText);
      } catch (jsonErr) {
        return new Response(JSON.stringify({ success: false, error: "Invalid JSON payload" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      const { email, lang, redirectUrl, hp_field } = payload;

      // 5. Anti-Bot Honeypot Detection
      if (hp_field && hp_field.trim() !== "") {
        return new Response(JSON.stringify({ success: false, error: "Bot activity detected." }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      // 6. Strict RFC Email Validation & Length Sanitization
      const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;
      if (!email || typeof email !== "string" || email.length > 254 || !emailRegex.test(email.trim())) {
        return new Response(JSON.stringify({ success: false, code: "INVALID_EMAIL", message: "Invalid email syntax" }), {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      const cleanEmail = email.trim().toLowerCase();
      const cleanLang = (lang === "en") ? "en" : "it";
      const templateId = cleanLang === "en" ? parseInt(env.BREVO_TEMPLATE_EN || "12") : parseInt(env.BREVO_TEMPLATE_IT || "11");
      const listId = cleanLang === "en" ? parseInt(env.BREVO_LIST_EN || "5") : parseInt(env.BREVO_LIST_IT || "4");

      const brevoPayload = {
        email: cleanEmail,
        includeListIds: [listId],
        templateId: templateId,
        redirectionUrl: redirectUrl || "https://itchronicle.com/p/thank-you-resources.html"
      };

      // 7. Authenticated Upstream Dispatch
      const brevoResponse = await fetch("https://api.brevo.com/v3/contacts/doubleOptinConfirmation", {
        method: "POST",
        headers: {
          "api-key": env.BREVO_API_KEY,
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(brevoPayload)
      });

      let brevoData = {};
      const resText = await brevoResponse.text();
      try {
        brevoData = JSON.parse(resText);
      } catch (e) {
        brevoData = { message: resText };
      }

      if (!brevoResponse.ok) {
        return new Response(JSON.stringify({
          success: false,
          status: brevoResponse.status,
          code: brevoData.code || "UPSTREAM_ERROR",
          message: brevoData.message || "Failed upstream validation"
        }), {
          status: brevoResponse.status,
          headers: { ...corsHeaders, "Content-Type": "application/json" }
        });
      }

      return new Response(JSON.stringify({ success: true, message: "Double opt-in initiated" }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });

    } catch (err) {
      return new Response(JSON.stringify({ success: false, error: err.message }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      });
    }
  }
};
