import os
import re
import json
import argparse
from pathlib import Path

# Pattern universali validi globalmente (API keys, email, IP privati, IBAN)
UNIVERSAL_PATTERNS = {
    "API Key / Secret Token": r"(?i)(api[_-]?key|secret|token|password|passwd)[\s]*[=:]+[\s]*['\"`][A-Za-z0-9_\-]{16,}['\"`]",
    "Email Address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "Private IP Address": r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})\b",
    "Credit Card / IBAN": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b"
}

def load_locale(lang):
    locale_path = Path(__file__).parent / "locales" / f"{lang}.json"
    if not locale_path.exists():
        # Fallback di sicurezza su inglese se il file non viene trovato
        locale_path = Path(__file__).parent / "locales" / "en.json"
    
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def scan_file(file_path, active_patterns):
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for category, pattern in active_patterns.items():
                    matches = re.findall(pattern, line)
                    if matches:
                        findings.append({
                            "line": line_num,
                            "category": category,
                            "snippet": line.strip()[:80]
                        })
    except Exception:
        pass
    return findings

def main():
    parser = argparse.ArgumentParser(description="AI Privacy Audit Tool - Prevent Shadow AI Data Leaks")
    parser.add_argument("target", nargs="?", default=".", help="Directory to scan / Directory da scansionare")
    parser.add_argument("--lang", choices=["it", "en"], default="en", help="Language configuration / Configurazione lingua (it/en)")
    args = parser.parse_args()

    # Carica la localizzazione e i pattern specifici dal file JSON
    locale_data = load_locale(args.lang)
    msg = locale_data["messages"]
    
    # Unisce i pattern universali a quelli specifici della lingua scelta nel JSON
    active_patterns = {**UNIVERSAL_PATTERNS, **locale_data["patterns"]}

    print(msg["start"].format(target=args.target))
    print("-" * 60)

    total_files = 0
    flagged_files = 0

    for root, _, files in os.walk(args.target):
        for file in files:
            # Esclude file binari o di sistema
            if file.endswith(('.exe', '.zip', '.png', '.jpg', '.pdf', '.pyc', '.git', '.docx', '.xlsx')):
                continue
            file_path = Path(root) / file
            total_files += 1
            findings = scan_file(file_path, active_patterns)
            
            if findings:
                flagged_files += 1
                print(msg["alert"].format(path=file_path))
                for f in findings:
                    print(f"    -> [Line/Linea {f['line']}] {f['category']}: {f['snippet']}")
                print("-" * 60)

    print(f"\n[📊] AUDIT SUMMARY / RIEPILOGO:")
    print(msg["scanning"].format(total=total_files))
    print(msg["found"].format(flagged=flagged_files))
    if flagged_files > 0:
        print(msg["recommendation"])
    else:
        print(msg["safe"])

if __name__ == "__main__":
    main()
