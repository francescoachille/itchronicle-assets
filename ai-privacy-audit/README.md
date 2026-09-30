AI Privacy Audit Tool 🛡️

🇮🇹 Italiano | 🇬🇧 English

🇮🇹 AI Privacy Audit Tool

Strumento di verifica e prevenzione per la Shadow AI. Analizza le directory di lavoro aziendali alla ricerca di dati sensibili, credenziali e informazioni personali (PII) prima che vengano accidentalmente esposte verso chatbot IA pubblici (ChatGPT, Claude, ecc.), garantendo conformità e sicurezza.

🚀 Installazione e Utilizzo Rapido

Clona o scarica questo repository.

Installa le dipendenze (se necessarie):

pip install -r requirements.txt


Esegui lo script indicando la cartella da analizzare e la lingua (it):

python ai_privacy_audit.py C:\ProgettiAziendali --lang it


📋 Caratteristiche

Pattern Universali: Rilevamento di chiavi API, token segreti, indirizzi IP privati e carte di credito/IBAN.

Pattern Specifici (IT): Rilevamento di Codici Fiscali italiani.

Reportistica chiara: Evidenzia riga per riga la tipologia di rischio riscontrata.

🇬🇧 AI Privacy Audit Tool

Audit and prevention tool against Shadow AI. Scans corporate directories for sensitive data, credentials, and personally identifiable information (PII) before they can be accidentally leaked to public AI chatbots, ensuring compliance and data sovereignty.

🚀 Installation & Quick Start

Clone or download this repository.

Install requirements (if any):

pip install -r requirements.txt


Run the script specifying the target directory and language (en):

python ai_privacy_audit.py /path/to/corporate/project --lang en


📋 Features

Universal Patterns: Detects API keys, secret tokens, private IP addresses, and credit cards/IBANs.

Specific Patterns (EN): Detects US Social Security Numbers (SSN) and UK National Insurance Numbers.

Clear Reporting: Pinpoints the exact line and risk category found.
