"""
Task definitions and graders for the Contract Review RL Environment.

Each task defines:
  - contract: the text the agent reads
  - description: what the agent is asked to do
  - answer: the ground-truth issues (used by grader)
  - max_steps: how many attempts the agent gets

Grader returns: (reward: float, feedback: str, hints: list[str])
"""

from typing import Tuple, List

# â”€â”€ TASK 1: EASY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

EASY_CONTRACT = """
VENDOR SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 15, 2024,
between TechStartup Inc. ("Client") and DevShop Ltd. ("Vendor").

1. SERVICES
   Vendor agrees to provide web development and maintenance services as
   requested by Client from time to time.

2. PAYMENT TERMS
   Client shall pay Vendor $8,000 per month. Payment is due within
   30 days of receipt of invoice.

3. TERM
   This Agreement commences on February 1, 2024 and continues for
   12 months, unless terminated earlier.

4. TERMINATION
   Either party may terminate this Agreement with 30 days written notice.

5. CONFIDENTIALITY
   Both parties agree to maintain the confidentiality of the other party's
   proprietary information during and after the term of this Agreement.

6. GOVERNING LAW
   This Agreement shall be governed by the laws of the State of California.

Signed:
Client: _______________     Date: ___________
Vendor: _______________     Date: ___________
"""

EASY_ANSWER = {
    "risk_level": "high",
    "missing_clauses": [
        "indemnification",
        "limitation of liability",
        "intellectual property ownership",
        "dispute resolution",
        "warranty disclaimer",
    ],
    "key_risk_terms": [
        "indemnif",
        "liabilit",
        "intellectual property",
        "ip ",
        "ownership",
        "deliverable",
        "undefined services",
        "vague",
    ],
}

EASY_DESCRIPTION = """
Review this Vendor Service Agreement and identify:
1. What is the overall risk level? (low / medium / high)
2. What important standard clauses are missing from this agreement?
3. What specific risks do these gaps create?

List each missing clause by name in 'missing_clauses'.
Explain the risks clearly in 'review_notes'.
"""


# â”€â”€ TASK 2: MEDIUM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

MEDIUM_CONTRACT = """
INDEPENDENT CONTRACTOR CONSULTING AGREEMENT

This Agreement is made between Acme Corp ("Company") and Jane Smith ("Consultant").

1. ENGAGEMENT
   Company engages Consultant to provide strategic business consulting
   services on an as-needed basis.

2. COMPENSATION
   Consultant shall be compensated at a rate that is fair and reasonable
   for services of this nature in the marketplace.

3. WORK PRODUCT & INTELLECTUAL PROPERTY
   All materials, reports, analyses, and deliverables created by Consultant
   during this engagement shall become the sole property of Company
   upon creation.

4. NON-COMPETE
   Consultant agrees not to provide similar consulting services to any
   competitor of Company anywhere in the world for a period of 3 years
   after the termination of this Agreement.

5. EXPENSES
   Company will reimburse Consultant for reasonable business expenses
   incurred in connection with the services.

6. INDEPENDENT CONTRACTOR STATUS
   Consultant is an independent contractor and not an employee, agent,
   or partner of Company.

7. TERM & TERMINATION
   This Agreement begins immediately upon signing and continues until
   either party terminates with 2 weeks written notice.
"""

MEDIUM_ANSWER = {
    "risk_level": "high",
    "missing_clauses": [
        "specific payment amount",
        "payment schedule",
        "dispute resolution",
    ],
    "ambiguous_clauses": [
        "fair and reasonable compensation",
        "reasonable business expenses",
    ],
    "unenforceable_clauses": [
        "non-compete worldwide 3 years",
    ],
    "key_risk_terms": [
        "reasonable",
        "fair",
        "ambiguous",
        "non-compete",
        "unenforceable",
        "worldwide",
        "3 year",
        "three year",
        "compensation",
        "no amount",
        "no rate",
        "ip assign",
        "intellectual property",
        "no consideration",
        "payment schedule",
    ],
}

MEDIUM_DESCRIPTION = """
Review this Independent Contractor Agreement and identify:
1. What clauses contain dangerously ambiguous or vague language?
2. Which clauses are likely legally unenforceable, and why?
3. What specific missing information creates financial or legal risk?

Pay special attention to compensation terms and the non-compete clause.
Rate the overall risk and explain each issue in detail.
"""


# â”€â”€ TASK 3: HARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

HARD_CONTRACT = """
=== DOCUMENT 1: MASTER SERVICE AGREEMENT (MSA) ===

MASTER SERVICE AGREEMENT

Entered into as of March 1, 2024 between GlobalTech Inc. ("Client")
and Solutions Pro LLC ("Provider").

SECTION 4. DELIVERABLES & ACCEPTANCE
Provider shall deliver all work product as described in each Statement
of Work. Client has 10 business days to accept or reject each deliverable.

SECTION 8. PAYMENT TERMS
All invoices shall be paid within sixty (60) days of the invoice date
("Net-60"). Late payments shall incur interest at 1.5% per month on
the outstanding balance. This payment term supersedes and applies to
all Statements of Work executed under this MSA.

SECTION 12. ORDER OF PRECEDENCE
This MSA, together with any Statements of Work, constitutes the entire
agreement between the parties. In the event of any conflict or
inconsistency between this MSA and any SOW, the terms of this MSA
shall control and govern.

SECTION 15. LIMITATION OF LIABILITY
Provider's total cumulative liability shall not exceed the total fees
paid by Client in the three (3) months preceding the claim.


=== DOCUMENT 2: STATEMENT OF WORK #3 (SOW-003) ===

STATEMENT OF WORK NO. 3
Issued pursuant to the Master Service Agreement dated March 1, 2024.

PROJECT: Enterprise Database Migration
SCOPE: Complete migration of customer database to new cloud platform
TIMELINE: 90 days from kickoff meeting

PRICING & MILESTONES:
  Phase 1 - Discovery & Architecture:    $45,000
  Phase 2 - Migration Execution:         $85,000
  Phase 3 - Testing & Validation:        $30,000
  TOTAL PROJECT VALUE:                  $160,000

PAYMENT SCHEDULE:
  Deposit (due at SOW signing):          $48,000 (30% of total)
  Phase 1 acceptance:                    $45,000 â€” due within 30 days
  Phase 2 acceptance:                    $85,000 â€” due within 30 days
  Phase 3 final acceptance:              $30,000 â€” due within 30 days

SUSPENSION RIGHTS:
  Provider reserves the right to suspend all work if any invoice
  remains unpaid 45 days after the due date stated in this SOW.

ADDITIONAL TERMS:
  Time is of the essence for all payment obligations in this SOW.
  Parties agree that the payment schedule herein reflects their
  specific negotiated terms for this project.
"""

HARD_ANSWER = {
    "risk_level": "high",
    "missing_clauses": [],
    "contradictions": [
        "Payment terms: MSA Section 8 requires Net-60 but SOW payment schedule requires Net-30 per milestone",
        "Suspension rights: MSA has no suspension clause but SOW allows suspension after 45 days (before Net-60 expires)",
        "Order of precedence: MSA Section 12 says MSA controls, but SOW states it reflects 'specific negotiated terms'",
    ],
    "key_risk_terms": [
        "net-60",
        "net-30",
        "net 60",
        "net 30",
        "30 day",
        "60 day",
        "contradict",
        "conflict",
        "payment term",
        "msa",
        "sow",
        "supersede",
        "suspension",
        "45 day",
        "precedence",
    ],
}

HARD_DESCRIPTION = """
You have TWO related documents: a Master Service Agreement (MSA) and
Statement of Work No. 3 (SOW-003).

Review BOTH documents carefully and identify:
1. Any direct contradictions or conflicts BETWEEN the two documents
2. Which document controls under the conflict-resolution clause
3. What practical risks these conflicts create for a $160,000 project

This is a CROSS-DOCUMENT review. Do not focus on missing clauses â€”
focus on what conflicts exist between the documents.
"""


# â”€â”€ TASK REGISTRY â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

TASKS = {
    "easy": {
        "contract": EASY_CONTRACT,
        "description": EASY_DESCRIPTION,
        "answer": EASY_ANSWER,
        "name": "Missing Clause Detection",
        "max_steps": 3,
    },
    "medium": {
        "contract": MEDIUM_CONTRACT,
        "description": MEDIUM_DESCRIPTION,
        "answer": MEDIUM_ANSWER,
        "name": "Ambiguous Language Detection",
        "max_steps": 3,
    },
    "hard": {
        "contract": HARD_CONTRACT,
        "description": HARD_DESCRIPTION,
        "answer": HARD_ANSWER,
        "name": "Cross-Document Contradiction Detection",
        "max_steps": 3,
    },
}


# â”€â”€ GRADER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _fuzzy_match(agent_list: List[str], expected_list: List[str]) -> int:
    """Count how many expected items are roughly covered by agent's list."""
    agent_text = " ".join(agent_list).lower()
    matched = 0
    for expected in expected_list:
        # Split expected into key words, check if any appear in agent text
        keywords = expected.lower().replace("-", " ").split()
        # Match if at least one meaningful keyword is found
        if any(len(kw) > 3 and kw in agent_text for kw in keywords):
            matched += 1
    return matched


def grade_action(
    task_id: str,
    action: dict,
    step: int,
) -> Tuple[float, str, List[str]]:
    """
    Grade the agent's contract review.

    Returns:
        reward   (float)     : 0.0â€“1.0
        feedback (str)       : what the agent got right/wrong
        hints    (List[str]) : guidance for next step (empty if last step)
    """
    task = TASKS[task_id]
    answer = task["answer"]
    is_last_step = step >= task["max_steps"]

    reward = 0.0
    fb: List[str] = []
    hints: List[str] = []

    # â”€â”€ 1. RISK LEVEL  (weight: 0.25) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    agent_risk = action.get("risk_level", "").lower().strip()
    expected_risk = answer["risk_level"]

    if agent_risk == expected_risk:
        reward += 0.25
        fb.append(f"âœ“ Correct risk level ({expected_risk}).")
    elif agent_risk in ("medium", "high") and expected_risk == "high":
        reward += 0.10
        fb.append(f"âœ— Risk is '{expected_risk}', not '{agent_risk}'. Think worst-case.")
        if not is_last_step:
            hints.append(f"The overall risk is '{expected_risk}'.")
    else:
        fb.append(f"âœ— Wrong risk level. Correct answer: '{expected_risk}'.")
        if not is_last_step:
            hints.append(f"Overall risk is '{expected_risk}'. Consider what could go catastrophically wrong.")

    # â”€â”€ 2. MISSING CLAUSES  (weight: 0.40) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    expected_clauses = answer.get("missing_clauses", [])

    if expected_clauses:
        agent_clauses = action.get("missing_clauses", [])
        matched = _fuzzy_match(agent_clauses, expected_clauses)
        clause_score = min(matched / len(expected_clauses), 1.0)
        reward += 0.40 * clause_score

        if clause_score >= 1.0:
            fb.append(f"âœ“ All {len(expected_clauses)} missing clauses identified!")
        elif clause_score >= 0.5:
            fb.append(f"âœ“ Found {matched}/{len(expected_clauses)} missing clauses.")
            if not is_last_step:
                missed = [c for c in expected_clauses
                          if not any(kw in " ".join(agent_clauses).lower()
                                     for kw in c.lower().split() if len(kw) > 3)]
                hints.append(f"Still missing: {', '.join(missed[:2])}.")
        else:
            fb.append(f"âœ— Only found {matched}/{len(expected_clauses)} missing clauses.")
            if not is_last_step:
                hints.append(f"Look for these missing clauses: {', '.join(expected_clauses[:2])}.")
    else:
        # Hard task: no missing clauses expected â€” penalise hallucination
        agent_clauses = action.get("missing_clauses", [])
        if not agent_clauses:
            reward += 0.40
            fb.append("âœ“ Correctly identified that no clauses are missing (focus is on contradictions).")
        else:
            reward += 0.20
            fb.append("âœ— Both documents have coverage of standard clauses. The issue is a conflict BETWEEN them.")
            if not is_last_step:
                hints.append("Don't look for missing clauses here. Compare the two documents' terms directly.")

    # â”€â”€ 3. DOMAIN-SPECIFIC ISSUES  (weight: 0.35) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    review_notes = action.get("review_notes", "").lower()
    contradictions_field = action.get("contradictions", [])
    flagged_field = action.get("flagged_language", [])

    all_agent_text = (
        review_notes
        + " " + " ".join(contradictions_field).lower()
        + " " + " ".join(flagged_field).lower()
    )

    key_terms = answer.get("key_risk_terms", [])
    hits = sum(1 for term in key_terms if term in all_agent_text)
    threshold = max(3, len(key_terms) // 3)  # need at least 1/3 of key terms

    if task_id == "easy":
        special_score = min(hits / threshold, 1.0)
        reward += 0.35 * special_score
        if hits >= threshold:
            fb.append("âœ“ Review notes correctly address key risk areas.")
        else:
            fb.append(f"Partial credit: found {hits}/{threshold}+ key risk indicators in notes.")
            if not is_last_step:
                hints.append("Discuss indemnification exposure, IP ownership of deliverables, and the vague 'as requested' services scope.")

    elif task_id == "medium":
        special_score = min(hits / threshold, 1.0)
        reward += 0.35 * special_score
        if hits >= threshold:
            fb.append("âœ“ Correctly identified ambiguous language and unenforceable clauses.")
        else:
            fb.append(f"Partial credit: caught {hits}/{threshold}+ key issues.")
            if not is_last_step:
                hints.append("Focus on: (1) 'fair and reasonable' compensation has no enforceable amount, (2) worldwide 3-year non-compete is almost certainly void, (3) IP transfer with no payment may be challenged.")

    elif task_id == "hard":
        special_score = min(hits / threshold, 1.0)
        reward += 0.35 * special_score
        if hits >= threshold:
            fb.append("âœ“ Correctly identified the MSA vs SOW payment term contradiction!")
        elif hits >= 2:
            fb.append("Partially identified the contradiction. Be more specific.")
            if not is_last_step:
                hints.append("MSA Section 8 says Net-60. SOW payment schedule says due within 30 days per milestone. That is a direct conflict. MSA Section 12 says MSA controls â€” but the SOW says its terms are 'specifically negotiated'.")
        else:
            fb.append("âœ— The main issue is between the two documents, not within a single document.")
            if not is_last_step:
                hints.append("Read MSA Section 8 (payment) and SOW payment schedule side by side. Compare the deadlines.")

    reward = round(min(max(reward, 0.0), 1.0), 4)
    feedback = "  ".join(fb)

    return reward, feedback, hints
