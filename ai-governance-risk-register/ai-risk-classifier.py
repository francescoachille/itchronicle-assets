#!/usr/bin/env python3
"""
IT Chronicle - EU AI Act & ISO/IEC 42001:2023 Risk Classifier CLI
Zero external dependencies (Python 3.9+ standard library only).

Usage:
  Interactive assessment:
    python3 ai-risk-classifier.py --interactive --export-csv risk_output.csv

  Batch assessment from JSON:
    python3 ai-risk-classifier.py --input systems.json --export-csv risk_output.csv
"""

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Any

PROHIBITED_TRIGGERS = {
    "subliminal_manipulation": "Subliminal or deceptive manipulation causing harm (Art. 5.1.a)",
    "vulnerability_exploitation": "Exploitation of age, disability, or socio-economic vulnerability (Art. 5.1.b)",
    "social_scoring": "Social scoring leading to detrimental treatment (Art. 5.1.c)",
    "biometric_categorization_sensitive": "Biometric categorization inferring race, politics, religion, or sexual orientation (Art. 5.1.g)",
    "workplace_emotion_recognition": "Emotion recognition in workplace or educational institutions (Art. 5.1.f)",
    "untargeted_facial_scraping": "Untargeted scraping of facial images for recognition databases (Art. 5.1.e)",
}

HIGH_RISK_DOMAINS = {
    "critical_infrastructure": "Safety component in critical infrastructure / OT / energy / water (Annex III.2)",
    "education_assessment": "Admission, evaluation, or proctoring in education/training (Annex III.3)",
    "hr_employment": "Recruitment, CV screening, promotion, task allocation, or termination (Annex III.4)",
    "essential_services_credit": "Creditworthiness, insurance risk pricing, or public benefits eligibility (Annex III.5)",
    "law_enforcement_justice": "Law enforcement, migration, asylum, or judicial assistance (Annex III.6-8)",
    "biometric_identification": "Remote biometric identification or verification systems (Annex III.1)",
}

TRANSPARENCY_TRIGGERS = {
    "human_facing_chatbot": "Direct interaction with natural persons / chatbot (Art. 50.1)",
    "synthetic_media_generation": "Generation of synthetic audio, image, video, or text (Art. 50.2 / 50.4)",
    "gpai_foundation_model": "General-Purpose AI (GPAI) integration or fine-tuning (Art. 51-53)",
}

ISO42001_CONTROL_MAP = {
    "UNACCEPTABLE": [
        "A.2.2 AI Policy (Prohibition Enforcement)",
        "A.5.2 AI System Impact Assessment (Terminate Deployment)",
        "A.9.2 Processes for Responsible Use of AI",
    ],
    "HIGH_RISK": [
        "A.4.2 Resource Documentation & Traceability",
        "A.5.2-A.5.5 AI System Impact Assessment (FRIA)",
        "A.6.2.4 Verification & Validation (Bias/Accuracy Testing)",
        "A.6.2.6 Operational Monitoring & Logging (Art. 12)",
        "A.7.3-A.7.5 Data Quality, Provenance & Bias Governance (Art. 10)",
        "A.8.2 System Documentation & Instructions for Use (Art. 11/13)",
        "A.9.3 Human Oversight Objectives (Art. 14)",
    ],
    "LIMITED_RISK": [
        "A.8.2-A.8.3 Transparency & User Disclosure (Art. 50)",
        "A.7.4 Data Governance & PII Filtering (GDPR Art. 25)",
        "A.9.2 Acceptable Use & Prompt Guardrails",
    ],
    "MINIMAL_RISK": [
        "A.2.2 Baseline AI Acceptable Use Policy",
        "A.4.2 Inventory Registration in AIMS",
        "A.6.2.6 Basic Operational Logging",
    ],
}


def classify_system(system: Dict[str, Any]) -> Dict[str, Any]:
    prohibited_hits = [
        desc for key, desc in PROHIBITED_TRIGGERS.items() if system.get(key) is True
    ]
    high_risk_hits = [
        desc for key, desc in HIGH_RISK_DOMAINS.items() if system.get(key) is True
    ]
    transparency_hits = [
        desc for key, desc in TRANSPARENCY_TRIGGERS.items() if system.get(key) is True
    ]

    if prohibited_hits:
        tier = "UNACCEPTABLE"
        eu_ref = "EU AI Act Art. 5 (Prohibited Practice)"
        inherent_score = "CRITICAL (25/25)"
        action = "BLOCK DEPLOYMENT IMMEDIATELY - Practice prohibited under EU law."
        rationale = "; ".join(prohibited_hits)
    elif high_risk_hits:
        tier = "HIGH_RISK"
        eu_ref = "EU AI Act Art. 6 & Annex III (High-Risk AI)"
        inherent_score = "HIGH (16/25)"
        action = "Mandatory Conformity Assessment, FRIA, Human Oversight, and EU Database Registration."
        rationale = "; ".join(high_risk_hits)
    elif transparency_hits:
        tier = "LIMITED_RISK"
        eu_ref = "EU AI Act Art. 50 (Transparency Obligations)"
        inherent_score = "MEDIUM (9/25)"
        action = "Enforce clear AI disclosure banners, watermarking/metadata, and DLP/GDPR controls."
        rationale = "; ".join(transparency_hits)
    else:
        tier = "MINIMAL_RISK"
        eu_ref = "EU AI Act Art. 95 (Voluntary Codes of Conduct)"
        inherent_score = "LOW (4/25)"
        action = "Register in corporate AI inventory and apply standard ISO 27001 / GDPR hygiene."
        rationale = "No prohibited, Annex III high-risk, or Art. 50 transparency triggers detected."

    processes_pii = bool(system.get("processes_pii", False))
    controls = list(ISO42001_CONTROL_MAP[tier])
    if processes_pii and "GDPR Art. 35 DPIA Required" not in controls:
        controls.append("GDPR Art. 35 DPIA & Data Minimization")

    return {
        "Assessment_Date": date.today().isoformat(),
        "System_ID": system.get("id", "AI-SYS-001"),
        "System_Name": system.get("name", "Unnamed AI System"),
        "Department_Owner": system.get("owner", "IT / Risk Owner"),
        "Deployment_Model": system.get("deployment", "On-Premise / Hybrid"),
        "Processes_PII": "Yes" if processes_pii else "No",
        "EU_AI_Act_Tier": tier,
        "Regulatory_Reference": eu_ref,
        "Inherent_Risk": inherent_score,
        "Trigger_Rationale": rationale,
        "ISO42001_Annex_A_Controls": " | ".join(controls),
        "Required_Action": action,
        "Audit_Status": "Pending Review",
    }


def ask_bool(question: str) -> bool:
    while True:
        ans = input(f"  [y/N] {question}: ").strip().lower()
        if ans in ("y", "yes", "s", "si", "sì"):
            return True
        if ans in ("", "n", "no"):
            return False


def run_interactive() -> List[Dict[str, Any]]:
    print("\n=== IT Chronicle | EU AI Act & ISO/IEC 42001 Risk Classifier ===\n")
    sys_id = input("System ID (e.g., AI-001): ").strip() or "AI-001"
    name = input("System Name (e.g., Local Ollama RAG): ").strip() or "Unnamed AI System"
    owner = input("Risk Owner / Department (e.g., CISO / HR): ").strip() or "IT Management"
    deployment = input("Deployment (On-Premise / Cloud SaaS / API): ").strip() or "On-Premise"
    processes_pii = ask_bool("Does the system process personal data (PII / GDPR)?")

    payload: Dict[str, Any] = {
        "id": sys_id,
        "name": name,
        "owner": owner,
        "deployment": deployment,
        "processes_pii": processes_pii,
    }

    print("\n[1/3] Prohibited Practices Screening (EU AI Act Art. 5):")
    for key, desc in PROHIBITED_TRIGGERS.items():
        payload[key] = ask_bool(desc)

    print("\n[2/3] High-Risk Domain Screening (EU AI Act Annex III):")
    for key, desc in HIGH_RISK_DOMAINS.items():
        payload[key] = ask_bool(desc)

    print("\n[3/3] Transparency & GPAI Screening (EU AI Act Art. 50):")
    for key, desc in TRANSPARENCY_TRIGGERS.items():
        payload[key] = ask_bool(desc)

    return [classify_system(payload)]


def print_report(results: List[Dict[str, Any]]) -> None:
    for r in results:
        print("\n" + "=" * 72)
        print(f"SYSTEM:     {r['System_ID']} — {r['System_Name']} ({r['Deployment_Model']})")
        print(f"RISK TIER:  {r['EU_AI_Act_Tier']} | {r['Inherent_Risk']}")
        print(f"LEGAL REF:  {r['Regulatory_Reference']}")
        print(f"RATIONALE:  {r['Trigger_Rationale']}")
        print(f"ISO 42001:  {r['ISO42001_Annex_A_Controls']}")
        print(f"ACTION:     {r['Required_Action']}")
        print("=" * 72)


def export_csv(results: List[Dict[str, Any]], output_path: Path) -> None:
    if not results:
        return
    fieldnames = list(results[0].keys())
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[+] Risk Register exported to: {output_path.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify AI systems against EU AI Act & ISO/IEC 42001:2023 (Zero dependencies)."
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Run interactive Q&A assessment.")
    parser.add_argument("--input", type=Path, help="Path to JSON file containing a list of AI system objects.")
    parser.add_argument("--export-csv", type=Path, help="Export classification results to an audit-ready CSV.")
    parser.add_argument("--export-json", type=Path, help="Export classification results to JSON.")
    args = parser.parse_args()

    if not args.interactive and not args.input:
        parser.print_help()
        return 1

    results: List[Dict[str, Any]] = []
    if args.interactive:
        results.extend(run_interactive())
    if args.input:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        systems = data if isinstance(data, list) else [data]
        results.extend(classify_system(s) for s in systems)

    print_report(results)

    if args.export_csv:
        export_csv(results, args.export_csv)
    if args.export_json:
        args.export_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[+] JSON report exported to: {args.export_json.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
