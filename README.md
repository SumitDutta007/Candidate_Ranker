# Intelligent Candidate Discovery & Ranking Engine

> **Redrob Data & AI Challenge** — Submission by [Your Team Name]

A multi-stage AI pipeline that ranks 100,000 candidates against a job description the way a senior recruiter would — combining semantic understanding, domain expertise detection, skill depth analysis, and behavioral signal integration to surface the highest-signal candidates with full explainability.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Scoring System](#scoring-system)
- [Honeypot & Fraud Detection](#honeypot--fraud-detection)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
- [Output Format](#output-format)
- [Design Decisions](#design-decisions)
- [Validation](#validation)
- [Submission Checklist](#submission-checklist)

---

## Overview

Traditional ATS systems fail because they match keywords, not meaning. This engine approaches candidate ranking the way a domain expert recruiter does:

1. **Deep JD Parsing** — Extracts required skills, experience targets, seniority signals, and domain keywords from any job description format.
2. **Semantic Fit** — Sentence transformer embeddings capture thematic alignment beyond surface-level keyword overlap.
3. **Domain Signal Detection** — Explicitly detects retrieval, ranking, recommendation, and evaluation experience from career narratives.
4. **Behavioral Signal Integration** — All 23 Redrob behavioral signals are weighted and normalized into a single signal score.
5. **Pedigree & Growth Analysis** — Distinguishes product company backgrounds from consulting-heavy profiles, and identifies career progression patterns.
6. **Honeypot Filtering** — Detects and penalizes statistically impossible or artificially inflated profiles before final ranking.

The result: a shortlist of 100 candidates with explainable, auditable reasoning for each rank.

---

## Architecture

```
JD Text
  └── JDAnalyzer ──────────────────────────────────┐
        ├── Required skills, domain keywords        │
        ├── Experience range extraction             │
        └── Seniority classification                │
                                                    ▼
Candidates (JSONL stream)                    QueryExpander
  └── CandidateDatasetLoader                  └── Ontology-based term expansion
        └── Candidate.from_dict()                   │
                                                    ▼
                                          CandidateRetriever   ← Prefilter (term hits)
                                                    │
                                          ┌─────────▼──────────┐
                                          │  Scoring Pipeline  │
                                          │                    │
                                          │  ExperienceScorer  │
                                          │   ├─ DomainAnalyzer│
                                          │   ├─ EvidenceAnalyzer
                                          │   ├─ GrowthAnalyzer│
                                          │   ├─ CompanyAnalyzer│
                                          │   └─ DomainPenaltyAnalyzer
                                          │                    │
                                          │  SkillScorer       │
                                          │  SignalScorer      │
                                          │  HoneypotScorer    │
                                          └─────────┬──────────┘
                                                    │
                                          SemanticRanker
                                           └── Batch cosine similarity
                                               (all-MiniLM-L6-v2)
                                                    │
                                          FinalRanker
                                           ├── Weighted hybrid score
                                           ├── Domain bonuses
                                           ├── Consulting penalty
                                           └── Honeypot risk discount
                                                    │
                                          ReasoningGenerator
                                                    │
                                          ranked_candidates.csv (Top 100)
```

### Pipeline Stages

**Stage 1 — Retrieval Prefilter**
Candidate texts are scored against expanded query terms (via ontology). Only candidates with `retrieval_score ≥ 5` pass to the next stage. This eliminates irrelevant candidates without any embedding computation, keeping the semantic stage tractable.

**Stage 2 — Scoring (Parallel)**
For all surviving candidates, four independent scorers run:
- `ExperienceScorer` — years fit, domain depth, company pedigree, career growth, quantified evidence
- `SkillScorer` — proficiency-weighted, endorsement-adjusted, duration-normalized skill matching
- `SignalScorer` — all 23 behavioral signals normalized and aggregated
- `HoneypotScorer` — statistical plausibility checks across profile, title, and signal consistency

**Stage 3 — Semantic Ranking**
Top candidates (by retrieval score) are batch-embedded with `all-MiniLM-L6-v2`. Cosine similarity to the JD embedding is computed vectorized via numpy, avoiding per-candidate overhead.

**Stage 4 — Final Ranking**
Scores are combined with configurable weights, domain bonuses applied for retrieval/ranking/recommendation expertise, honeypot risk discounted, and candidates sorted.

**Stage 5 — Reasoning Generation**
Each candidate gets a 1–2 sentence human-readable justification covering: role/company, matched skills, background type, domain strengths, signal highlights, and overall fit tier.

---

## Scoring System

### Score Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic Similarity | 35% | JD–profile cosine similarity via SBERT |
| Experience & Pedigree | 30% | Years fit, domain depth, company type, evidence |
| Behavioral Signals | 20% | 23 Redrob signals, normalized and weighted |
| Skill Match | 10% | Proficiency × endorsement × duration |
| Domain Bonuses | +3% each | Retrieval / ranking / recommendation expertise |

### Experience Score Breakdown

```
exp_score = (
    0.25 × years_score          # distance from JD target experience
  + 0.35 × domain_score         # domain keyword depth (12-term cap)
  + 0.20 × evidence_score       # quantified impact in descriptions
  + 0.10 × growth_score         # career level progression
  + 0.05 × product_score        # product vs. services company background
  + 0.05 × consulting_score     # consulting exposure penalty
) × domain_penalty              # CV/vision mismatch penalty
```

### Signal Weights (Selected)

| Signal | Weight | Notes |
|--------|--------|-------|
| `recruiter_response_rate` | +0.12 | Strongest behavioral signal |
| `last_active_date` | +0.10 | Recency within 180-day window |
| `open_to_work_flag` | +0.08 | Direct intent signal |
| `profile_completeness_score` | +0.07 | Data quality proxy |
| `github_activity_score` | +0.07 | Technical credibility |
| `interview_completion_rate` | +0.06 | Engagement seriousness |
| `avg_response_time_hours` | −0.06 | Penalizes slow responders |
| `notice_period_days` | −0.04 | Shorter = higher score |

All 23 signals are included. See `scoring_weights.py` for the full table.

---

## Honeypot & Fraud Detection

The dataset contains ~80 honeypot candidates with statistically impossible profiles. The `HoneypotScorer` applies the following checks:

| Check | Risk Added | Logic |
|-------|-----------|-------|
| Junior experience + senior title | +0.40 | < 4 years XP with Staff/Principal/Director title |
| Skills inflation | +0.25 | < 2 years XP with > 25 skills |
| Over-experienced for role | +0.30 | > 15 years XP claiming Junior/Intern |
| Career timeline inconsistency | +0.30 | Total career months > years × 12 + 36 |
| Signal perfection anomaly | +0.20 | GitHub score > 0.95 AND recruiter rate > 0.95 simultaneously |

Final score is discounted by `1 - (honeypot_risk × 0.40)`. Candidates with honeypot risk above threshold are naturally deprioritized in ranking.

---

## Project Structure

```
candidate-ranking-engine/
│
├── main.py                          # Entry point
├── requirements.txt
├── README.md
│
├── assets/
│   ├── job_description.txt
│   ├── candidates.jsonl             # Full 100k dataset (extract from .gz)
│   ├── candidates_sample.jsonl      # First 50 candidates
│   └── redrob_behavioral_signals.txt
│
└── src/
    ├── data_loaders/
    │   ├── candidate_dataset_loader.py   # Streaming JSONL reader
    │   └── job_description_loader.py
    │
    ├── models/
    │   ├── candidate.py                  # Candidate dataclass
    │   ├── job_description.py            # JD dataclass
    │   ├── candidate_score.py
    │   ├── ranking_result.py
    │   └── ranking_config.py
    │
    ├── pipeline/
    │   ├── retrieval/
    │   │   ├── candidate_retriever.py    # Term-based prefilter
    │   │   ├── query_expander.py         # Ontology expansion
    │   │   └── ontology.py               # Skill synonym graph
    │   ├── semantic_ranker.py            # Batch SBERT scoring
    │   ├── final_ranker.py               # Score combination
    │   └── reasoning_generator.py        # Explainable output
    │
    ├── scorers/
    │   ├── base_scorer.py
    │   ├── experience_scorer.py
    │   ├── skill_scorer.py
    │   ├── signal_scorer.py
    │   ├── honeypot_scorer.py
    │   ├── semantic_score_aggregator.py
    │   └── experience/
    │       ├── domain_analyzer.py         # Keyword depth scoring
    │       ├── evidence_analyzer.py       # Quantified impact detection
    │       ├── growth_analyzer.py         # Career level progression
    │       ├── company_analyzer.py        # Product vs. consulting classification
    │       └── domain_penalty_analyzer.py # CV/unrelated domain penalty
    │
    ├── services/
    │   ├── embedding_service.py           # SentenceTransformer wrapper
    │   ├── jd_analyzer.py                 # JD parsing (skills, XP, seniority)
    │   ├── candidate_text_builder.py      # Candidate text for embedding
    │   ├── document_loader.py             # PDF / DOCX / TXT JD loader
    │   ├── csv_export_service.py
    │   ├── cadidate_file_loader.py        # JSON / JSONL / JSONL.GZ
    │   └── role_classifier.py
    │
    └── utils/
        ├── scoring_weights.py             # All weights and normalizers
        └── text_preprocessing.py
```

---

## Setup & Installation

**Requirements:** Python 3.8+, pip, ~2 GB RAM, CPU-only (no GPU required)

```bash
# 1. Clone and enter the project
git clone https://github.com/your-team/candidate-ranking-engine.git
cd candidate-ranking-engine

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Linux/Mac
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Extract the candidate dataset
gunzip -k assets/candidates.jsonl.gz
wc -l assets/candidates.jsonl   # should output 100000
```

**`requirements.txt`**
```
sentence-transformers>=2.2.0
pandas
numpy
tqdm
torch>=2.3.0
transformers
PyPDF2
python-docx
```

The sentence transformer model (`all-MiniLM-L6-v2`) is downloaded automatically on first run (~80 MB). To pre-download:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## How to Run

### Quick Test (Sample Data)

```bash
# Edit main.py: set data_path = "assets/candidates_sample.jsonl"
python main.py
```

Produces a ranked CSV for the first 50 candidates in seconds.

### Full Run (100k Candidates)

```bash
python main.py
```

**Expected performance:**
- Retrieval prefilter: ~1–2 min
- Scoring (skill + experience + signal): ~3–5 min
- Semantic encoding (top 2000 candidates): ~2–4 min
- Total: **~8–12 minutes on a standard laptop CPU**

Output: `ranked_candidates.csv` — top 100 candidates, sorted by final score.

### Configurable Parameters (in `main.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_RETRIEVAL_SCORE` | `5` | Minimum term hits to survive prefilter |
| `TOP_SEMANTIC_POOL` | `2000` | Candidates entering the semantic stage |
| `TOP_OUTPUT` | `100` | Final shortlist size |
| `DEBUG` | `True` | Verbose stage-by-stage output |

---

## Output Format

The engine produces a CSV with exactly these four columns:

| Column | Type | Description |
|--------|------|-------------|
| `candidate_id` | string | From the dataset (e.g., `CAND_0000031`) |
| `rank` | integer | 1-based rank (1 = best fit) |
| `score` | float | Final hybrid score [0.0, 1.0], 4 decimal places |
| `reasoning` | string | 1–2 sentence explainable justification |

**Example row:**
```
CAND_0000031,1,0.8063,"Recommendation Systems Engineer at Swiggy with 6.0 years of experience; matched skills: Embeddings, Information Retrieval, Python; product company background; strong retrieval experience (4 matching signals); high recruiter engagement; strong fit."
```

---

## Design Decisions

**Why a retrieval prefilter before semantic scoring?**
Embedding 100,000 candidates is expensive and noisy. The term-based prefilter (ontology-expanded BM25-style scoring) eliminates clearly irrelevant profiles before any neural computation, cutting semantic overhead by ~70–80% with minimal recall loss.

**Why not just use cosine similarity as the final score?**
Semantic similarity captures thematic fit but ignores signal quality. A candidate whose profile is written to sound like the JD (keyword stuffer) would rank highly on cosine alone. The multi-component scoring penalizes profiles that look semantically aligned but lack real domain depth, behavioral engagement, or quantified evidence.

**Why separate domain analyzers vs. a monolithic scorer?**
Each sub-analyzer (domain, evidence, growth, company, penalty) is independently testable and configurable. This makes weight tuning and debugging tractable — you can inspect each component in isolation, as the `DEBUG` mode demonstrates.

**Why explicit honeypot rules rather than anomaly detection?**
The `redrob_signals_doc.md` describes specific trap patterns. Explicit rules are interpretable, auditable, and directly map to the documented signal envelopes. A statistical model trained on the same dataset would overfit to the specific traps rather than generalizing.

---

## Validation

Run the provided validator before submitting:

```bash
python validate_submission.py ranked_candidates.csv
```

The validator checks:
- Correct header: `candidate_id,rank,score,reasoning`
- Exactly 100 rows
- Sequential integer ranks starting at 1
- Scores are floats in [0.0, 1.0]
- No duplicate candidate IDs
- Reasoning column is non-empty

---

## Submission Checklist

- [ ] `ranked_candidates.csv` — top 100 candidates, passes validator
- [ ] GitHub repository — public, contains all source code
- [ ] `approach.pdf` — slide deck explaining architecture and design choices
- [ ] Working sandbox — HuggingFace Spaces / Streamlit Cloud / Colab link
- [ ] `submission_metadata_template.yaml` — completed with team name, repo URL, sandbox link, AI tools declaration
- [ ] Honeypot rate in top 100 < 10% (verify with `validate_submission.py`)

---

## Acknowledgments

Built for the **Redrob Data & AI Challenge: Intelligent Candidate Discovery**.

- Embeddings: [sentence-transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2`
- Candidate data and behavioral signal schema: Redrob participant bundle