/**
 * Brevo Error Status Code Mapper & Resilient Client
 * Maps raw HTTP responses to structured, localized messages.
 * Author: IT Chronicle (https://itchronicle.com)
 */

export const BrevoErrorCodes = {
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  PAYMENT_REQUIRED: 402,
  RATE_LIMITED: 429,
  INTERNAL_SERVER_ERROR: 500
};

export function parseBrevoResponse(statusCode, data, lang = "it") {
  const isEn = lang === "en";

  switch (statusCode) {
    case 200:
    case 201:
      return {
        success: true,
        message: isEn 
          ? "Request processed successfully. Please check your inbox for the confirmation link."
          : "Richiesta completata. Controlla la tua casella di posta per confermare l'iscrizione."
      };

    case 400:
      return {
        success: false,
        code: "INVALID_SYNTAX",
        message: isEn 
          ? "Invalid email format or missing parameters."
          : "Indirizzo email formalmente non valido o parametri incompleti."
      };

    case 409:
      return {
        success: false,
        code: "CONTACT_ALREADY_EXISTS",
        message: isEn
          ? "This email address is already subscribed to our newsletter."
          : "Questo indirizzo email risulta già iscritto alla newsletter."
      };

    case 429:
      return {
        success: false,
        code: "RATE_LIMIT_EXCEEDED",
        message: isEn
          ? "Too many requests. Please wait a few minutes before submitting again."
          : "Troppe richieste in un breve intervallo. Attendi qualche minuto prima di riprovare."
      };

    case 500:
    case 502:
    case 503:
      return {
        success: false,
        code: "UPSTREAM_UNAVAILABLE",
        message: isEn
          ? "Brevo email servers are temporarily unreachable. Please retry shortly."
          : "I server di Brevo sono temporaneamente non raggiungibili. Riprova a breve."
      };

    default:
      return {
        success: false,
        code: data?.code || "GENERIC_ERROR",
        message: data?.message || (isEn ? "An unexpected error occurred." : "Si è verificato un errore imprevisto.")
      };
  }
}
