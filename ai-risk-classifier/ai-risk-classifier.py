#!/usr/bin/env python3
"""
ITChronicle Enterprise AI Governance & Risk Register Engine
Compliance: EU AI Act (Reg. UE 2024/1689) & ISO/IEC 42001:2023
Zero external dependencies - Standard Library only.
"""

import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ANNEX_III_DOMAINS = {
    "1": ("Biometria e identificazione remota", "HIGH_RISK", "Art. 6(2) - Annex III.1"),
    "2": ("Infrastrutture critiche (energia, acqua, reti, trasporti)", "HIGH_RISK", "Art. 6(2) - Annex III.2"),
    "3": ("Istruzione e formazione professionale", "HIGH_RISK", "Art. 6(2) - Annex III.3"),
    "4": ("Occupazione, selezione HR e gestione lavoratori", "HIGH_RISK", "Art. 6(2) - Annex III.4"),
    "5": ("Accesso a servizi essenziali (credit scoring, sanità, welfare)", "HIGH_RISK", "Art. 6(2) - Annex III.5"),
    "6": ("Forze dell'ordine, migrazione e amministrazione giustizia", "HIGH_RISK", "Art. 6(2) - Annex III.6-8"),
    "7": ("Chatbot / GenAI customer-facing o supporto interno", "LIMITED_RISK", "Art. 50 - Obblighi Trasparenza"),
    "8": ("Automazione interna / analisi dati non-PII", "MINIMAL_RISK", "Art. 95 - Codici di condotta volontari")
}

ISO42001_CONTROLS = {
    "HIGH_RISK": [
        "A.4.2 Resource documentation (Data, Compute, Model Lineage)",
        "A.5.2 AI System Impact Assessment (AIIA) obbligatorio",
        "A.6.2.4 Data quality & bias mitigation verification",
        "A.7.3 Human oversight & kill-switch operativi (Art. 14 AI Act)",
        "A.8.4 Logging automatico eventi e tracciabilità (Art. 12 AI Act)"
    ],
    "LIMITED_RISK": [
        "A.5.2 AI System Impact Assessment (lightweight)",
        "A.8.2 Disclosure esplicita interazione con IA (Art. 50 AI Act)",
        "A.6.2.2 Data governance e prevenzione Data Leakage PII"
    ],
    "MINIMAL_RISK": [
        "A.2.2 Censimento nell'inventario asset IA aziendale",
        "A.6.2.2 Acceptable Use Policy per LLM e Prompt Engineering"
    ]
}

def evaluate_system(name: str, provider: str, domain_key: str, processes_pii: bool, human_in_loop: bool) -> dict:
    domain_desc, risk_tier, legal_ref = ANNEX_III_DOMAINS.get(
        domain_key, ("Dominio non classificato", "HIGH_RISK", "Default Precautionary Principle")
    )

    inherent_score = {"HIGH_RISK": 9.0, "LIMITED_RISK": 5.5, "MINIMAL_RISK": 2.5}[risk_tier]
    if processes_pii:
        inherent_score = min(10.0, inherent_score + 1.0)
    if not human_in_loop and risk_tier == "HIGH_RISK":
        inherent_score = 10.0

    controls = ISO42001_CONTROLS[risk_tier].copy()
    if processes_pii:
        controls.append("GDPR Art. 35 - Data Protection Impact Assessment (DPIA) integrata")

    record_id = hashlib.sha256(f"{name}-{provider}-{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

    return {
        "asset_id": f"AI-{record_id.upper()}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "system_name": name,
        "provider_model": provider,
        "domain": domain_desc,
        "eu_ai_act_tier": risk_tier,
        "legal_reference": legal_ref,
        "processes_pii": processes_pii,
        "human_oversight": human_in_loop,
        "inherent_risk_score": inherent_score,
        "mandatory_iso42001_controls": " | ".join(controls)
    }

def export_register(records: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "ai_risk_register_iso42001.json"
    csv_path = out_dir / "ai_risk_register_iso42001.csv"

    with json_path.open("w", encoding="utf-8") as jf:
        json.dump({"schema": "ISO/IEC 42001 + EU AI Act", "records": records}, jf, indent=2, ensure_ascii=False)

    with csv_path.open("w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print(f"\n[+] Registro esportato con successo:\n    - {json_path}\n    - {csv_path}")

if __name__ == "__main__":
    print("=== ITChronicle AI Governance & Risk Register Builder ===")
    systems = [
        evaluate_system("HR CV Screening Assistant", "Azure OpenAI GPT-4o", "4", True, True),
        evaluate_system("SOC Log Anomaly Classifier", "Local Llama-3-8B (Ollama)", "2", False, True),
        evaluate_system("Public Support Chatbot", "Gemini API", "7", True, True)
    ]
    export_register(systems, Path("./ai_governance_output"))
