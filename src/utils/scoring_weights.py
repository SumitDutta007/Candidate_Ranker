"""
Scoring weights and configuration constants
"""
import numpy as np
from typing import List, Tuple, Dict, Callable, Any
from datetime import datetime

# ----------------------------
# Weights for hybrid scoring (can be tuned)
# ----------------------------
W_SEMANTIC = 0.4
W_SKILL = 0.3
W_EXPERIENCE = 0.2
W_SIGNALS = 0.1

# Desired skills extracted from the job description (lowercase for matching)
DESIRED_SKILLS: List[str] = [
    "embeddings",
    "vector database",
    "python",
    "evaluation",
    "ranking",
    "llm",
    "fine-tuning",
    "learning-to-rank",
    "retrieval",
    "hybrid search",
    "ndcg",
    "mrr",
    "map",
    "a/b testing",
    "product company",
    "ml systems"
]

# Experience scoring: ideal range and fallout
IDEAL_EXP_MIN = 5
IDEAL_EXP_MAX = 9
EXP_RANGE_TOLERANCE = 1  # allow +/- 3 years beyond ideal range for partial credit

# Known product companies (non-exhaustive, for heuristic)
PRODUCT_COMPANIES_INDICATORS: List[str] = [
    "google", "meta", "amazon", "microsoft", "apple", "netflix", "uber",
    "airbnb", "spotify", "adobe", "salesforce", "oracle", "ibm",
    "tiktok", "bytedance", "twitter", "linkedin", "paypal", "stripe",
    "shopify", "flipkart", "ola", "swiggy", "zomato", "paytm",
    "redrob"  # the hiring company itself
]

# Known services/consulting firms (for penalty)
CONSULTING_FIRMS: List[str] = [
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "htech", "lti", "mindtree", "mpp", "hexaware", "l&t infotech",
    "mindtree", "deutsche bank", "barclays", "hsbc", "citibank",
    "jpmorgan", "goldman sachs", "morgan stanley"
]

# ----------------------------------------------------------------------
# Signal‑weight configuration (tweakable)
# ----------------------------------------------------------------------
# Each entry:  signal_name → (weight, normaliser)
#   * weight  > 0  → boosts the candidate
#   * weight  < 0  → penalises (e.g. honeypot / fraud flags)
#   * normaliser converts the raw value to a 0‑1 float (or 0/1 for booleans)
# ----------------------------------------------------------------------
SIGNAL_WEIGHTS: Dict[str, Tuple[float, Callable[[Any], float]]] = {
    # 1. Profile completeness (0‑100 → 0‑1)
    "profile_completeness_score": (0.07, lambda v: max(0.0, min(1.0, v / 100.0))),

    # 2. signup_date – older accounts get a tiny reliability boost (max 5 yr)
    "signup_date": (
        0.02,
        lambda d: max(
            0.0,
            min(
                1.0,
                (datetime.fromisoformat(d) - datetime(2020, 1, 1)).days / 365.0 / 5.0,
            ),
        ),
    ),

    # 3. last_active_date – recent activity = strong signal
    "last_active_date": (
        0.10,
        lambda d: max(
            0.0,
            min(
                1.0,
                1.0 - max(0, (datetime.now() - datetime.fromisoformat(d)).days) / 180.0,
            ),
        ),
    ),

    # 4. open_to_work_flag
    "open_to_work_flag": (0.08, lambda v: 1.0 if v else 0.0),

    # 5. profile_views_received_30d (log‑scale)
    "profile_views_received_30d": (0.04, lambda v: np.log1p(v) / np.log1p(5000)),

    # 6. applications_submitted_30d (log‑scale, capped)
    "applications_submitted_30d": (
        0.02,
        lambda v: np.log1p(min(v, 50)) / np.log1p(50),
    ),

    # 7. recruiter_response_rate (already 0‑1)
    "recruiter_response_rate": (0.12, lambda v: max(0.0, min(1.0, v))),

    # 8. avg_response_time_hours – lower is better (capped at 48 h)
    "avg_response_time_hours": (
        -0.06,
        lambda h: max(0.0, min(1.0, 1.0 - (h / 48.0))),
    ),

    # 9. skill_assessment_scores – dict of skill→0‑100; average top‑3
    "skill_assessment_scores": (
        0.05,
        lambda d: (
            (lambda vals: sum(sorted(vals, reverse=True)[:3]) / (3 * 100.0))
            (list(d.values()))
            if isinstance(d, dict) and d
            else 0.0
        ),
    ),

    # 10. connection_count (log‑scale)
    "connection_count": (0.03, lambda v: np.log1p(v) / np.log1p(5000)),

    # 11. endorsements_received (log‑scale)
    "endorsements_received": (0.03, lambda v: np.log1p(v) / np.log1p(2000)),

    # 12. notice_period_days – shorter notice = higher score
    "notice_period_days": (
        -0.04,
        lambda d: max(0.0, 1.0 - min(d, 180) / 180.0),
    ),

    # 13. expected_salary_range_inr_lpa – penalise high expectations (cap 40 LPA)
    "expected_salary_range_inr_lpa": (
        -0.02,
        lambda rng: (
            1.0 - min(rng.get("max", 0) / 40.0, 1.0)
        ) if isinstance(rng, dict) else 0.0,
    ),

    # 14. preferred_work_mode – preference for remote/hybrid
    "preferred_work_mode": (
        0.02,
        lambda v: {"remote": 1.0, "hybrid": 0.8, "flexible": 0.6, "onsite": 0.4}.get(v.lower(), 0.0)
        if isinstance(v, str)
        else 0.0,
    ),

    # 15. willing_to_relocate (bool)
    "willing_to_relocate": (0.02, lambda v: 1.0 if v else 0.0),

    # 16. github_activity_score – -1 … 100 → normalise to 0‑1
    "github_activity_score": (
        0.07,
        lambda v: max(0.0, min(1.0, (v + 1) / 101.0)),
    ),

    # 17. search_appearance_30d – log‑scale
    "search_appearance_30d": (0.02, lambda v: np.log1p(v) / np.log1p(2000)),

    # 18. saved_by_recruiters_30d – log‑scale
    "saved_by_recruiters_30d": (0.04, lambda v: np.log1p(v) / np.log1p(500)),

    # 19. interview_completion_rate (0‑1)
    "interview_completion_rate": (0.06, lambda v: max(0.0, min(1.0, v))),

    # 20. offer_acceptance_rate – -1 means no offers yet → neutral 0.5
    "offer_acceptance_rate": (
        0.03,
        lambda v: 0.5 if v == -1 else max(0.0, min(1.0, v)),
    ),

    # 21. verified_email (bool)
    "verified_email": (0.02, lambda v: 1.0 if v else 0.0),

    # 22. verified_phone (bool)
    "verified_phone": (0.02, lambda v: 1.0 if v else 0.0),

    # 23. linkedin_connected (bool)
    "linkedin_connected": (0.02, lambda v: 1.0 if v else 0.0),
}