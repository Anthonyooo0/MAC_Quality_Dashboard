# prompts.py
CATEGORIES = [
    "Product","Shipping","Documentation/Revision","Invoicing/RTV",
    "Supplier/SCAR","Damage/Transit","Missing Parts","Other",
]

BUSINESS_SUMMARY_STYLE = """
Write a brief business-style summary in 1–2 sentences (≤45 words) focused ONLY on the latest reply (ignore quoted history).
- State the concrete problem (e.g., “wrong rev shipped”, “cracked housing”, “missing fasteners”).
- Include the requested action if present (e.g., “RMA requested”, “replacement requested”, “credit requested”).
- Neutral tone; no verbatim copying.
"""

CONSTRAINTS = """
EXTRACTION RULES:
- part_number: 5–25 chars, A–Z 0–9 - _ . / only; must include ≥1 digit and ≥1 letter.
- If a candidate part number does not appear in the company master list, treat it as missing.

If missing or uncertain, use:
- part_number: "No part number provided"

category_suggested must be ONE of:
{categories}

case_key: stable across replies. Use sender domain + (part_number if present else normalized subject) + short normalized problem phrase. Lowercase, letters/digits/-_/ only. ≤80 chars.
"""

CLASSIFIER = """
Return a boolean field is_complaint:
- true if the latest reply indicates a nonconformance/quality issue, defect, wrong rev, damage, missing parts, NCMR/SCAR/DMR/RMA/return/replacement/rework/credit request, or a customer reporting a problem.
- false for newsletters, training, reminders, marketing, HR/policy blasts, general announcements, meeting invites, out-of-office, or anything with no defect/requested action.
"""

OUTPUT_FORMAT = """
Return STRICT JSON with these keys ONLY:
- is_complaint          (boolean)
- summary               (string)
- category_suggested    (string; one of allowed categories)
- case_key              (string; ≤80 chars; normalized)
- part_number           (string)
"""

PROMPT_TEXT = (
    f"You are a quality assistant that extracts key details from complaint emails.\n\n"
    f"{BUSINESS_SUMMARY_STYLE}\n\n"
    f"{CONSTRAINTS}\n\n"
    f"{CLASSIFIER}\n\n"
    f"{OUTPUT_FORMAT}\n\n"
    "INPUT\n"
    "SUBJECT (cleaned): {subject_clean}\n"
    "FROM: {from_email}\n"
    "LATEST REPLY (trimmed): {body_text}\n\n"
    "Notes:\n"
    "- The system validates part_number against the official master list. If your extracted part_number is not in that list, the system will set it to \"No part number provided\".\n"
).replace("{categories}", str(CATEGORIES))