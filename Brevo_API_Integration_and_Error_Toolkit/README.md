# Brevo API Integration & Error Toolkit
*Client and middleware modules for structured Brevo API v3 status code handling.*

## Included Modules
1. `brevo-client.js`: Maps HTTP status codes (400, 402, 409, 429, 500) into structured, localized human-friendly messages (EN / IT).
2. `brevo-form-handler.js`: Lightweight, dependency-free vanilla JS script for static CMS (Blogger) handling UI feedback, button states, and honeypot traps.

## Status Code Reference Table
| Status | Brevo Code | Meaning | User Feedback |
|---|---|---|---|
| **200/201** | `success` | Double opt-in email queued | "Please verify your inbox." |
| **400** | `invalid_parameter` | Syntax error in email / listId | "Invalid email format." |
| **409** | `duplicate_parameter` | Contact already subscribed | "Email already in list." |
| **429** | `too_many_requests` | API throttling reached | "Too many requests. Please wait." |
| **500** | `server_error` | Brevo upstream degradation | "Email servers unreachable." |
