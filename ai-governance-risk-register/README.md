# AI Governance Risk Register (ISO/IEC 42001:2023 + EU AI Act)

Operational toolkit from **IT Chronicle** for IT Security Managers, CISOs, and DPOs to classify corporate AI systems and maintain an audit-ready AI Risk Register.

## Contents

1. **`ai-risk-classifier.py`** — Zero-dependency Python 3 CLI that evaluates AI systems against **EU AI Act** risk tiers (Unacceptable, High-Risk Annex III, Limited Risk Art. 50, Minimal Risk) and maps mandatory **ISO/IEC 42001:2023 Annex A** controls.
2. **`ISO42001_EU_AI_Act_Risk_Register.csv`** — Executive audit-ready Risk Register template (Excel / Google Sheets compatible) with pre-mapped enterprise AI scenarios, inherent/residual scoring, and audit evidence hooks.

## Quick Start

### Interactive Classification
```bash
python3 ai-risk-classifier.py --interactive --export-csv my_ai_risks.csv
