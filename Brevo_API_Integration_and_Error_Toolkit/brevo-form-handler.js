/**
 * Client-Side Brevo Lead Generation Controller for Static Blogs (Blogger)
 * Features: Double-click prevention, honeypot forwarding, localized dynamic feedback.
 * Author: IT Chronicle (https://itchronicle.com)
 */

(function initBrevoLeadForm() {
  const form = document.getElementById("apiLeadForm");
  if (!form) return;

  const btn = document.getElementById("submitBtn");
  const feedback = document.getElementById("formFeedback");
  const emailInput = document.getElementById("userEmail");
  const langInput = document.getElementById("formLang");
  const urlInput = document.getElementById("toolUrl");
  const hpInput = document.getElementById("hp_field");

  const originalBtnText = btn ? btn.innerText : "SUBMIT";

  form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = emailInput ? emailInput.value.trim() : "";
    const lang = langInput ? langInput.value : "en";
    const redirectUrl = urlInput ? urlInput.value : "";
    const honeypot = hpInput ? hpInput.value : "";

    // Client-side quick check
    if (!email || !email.includes("@")) {
      showFeedback(lang === "en" ? "> Please provide a valid email." : "> Inserisci un'email valida.", "#ff4b4b");
      return;
    }

    // Set UI Loading State
    btn.disabled = true;
    btn.innerText = lang === "en" ? "PROCESSING..." : "ELABORAZIONE...";
    clearFeedback();

    try {
      const response = await fetch("https://brevo-optin-api.francescoachille.workers.dev", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          lang: lang,
          redirectUrl: redirectUrl,
          hp_field: honeypot
        })
      });

      const resData = await response.json();

      if (response.ok && resData.success) {
        showFeedback(
          lang === "en" 
            ? "> Success! Please verify your inbox for the download link." 
            : "> Richiesta completata! Controlla la tua casella di posta.", 
          "var(--accent, #00ff66)"
        );
        form.reset();
      } else {
        const errorMsg = resData.message || (lang === "en" ? "Submission rejected." : "Richiesta respinta.");
        showFeedback("> " + errorMsg, "#ff4b4b");
      }
    } catch (networkErr) {
      showFeedback(
        lang === "en" 
          ? "> Network failure. Unable to reach verification proxy." 
          : "> Errore di rete. Impossibile contattare il server gateway.", 
        "#ff4b4b"
      );
    } finally {
      btn.disabled = false;
      btn.innerText = originalBtnText;
    }
  });

  function showFeedback(text, color) {
    if (!feedback) return;
    feedback.innerText = text;
    feedback.style.color = color;
    feedback.style.display = "block";
  }

  function clearFeedback() {
    if (!feedback) return;
    feedback.style.display = "none";
    feedback.innerText = "";
  }
})();
