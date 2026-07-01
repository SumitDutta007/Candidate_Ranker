#!/usr/bin/env python3
"""
Intelligent Candidate Discovery & Ranking Engine

This script reads a job description and a candidate dataset (JSONL format),
then outputs a ranked list of candidates with explainable reasoning.

Approach:
 1. Load the job description.
 2. Stream the candidate dataset to avoid memory issues.
 3. For each candidate, compute:
      - Semantic similarity score (using sentence embeddings) between JD and candidate's textual profile.
      - Skill match score based on desired skills from JD.
      - Experience and pedigree score (years of experience, product company background).
      - Behavioral signal score (recruiter response rate, profile completeness, GitHub activity, etc.).
 4. Combine scores using a weighted hybrid model.
 5. Rank candidates and output CSV with columns: candidate_id, rank, score, reasoning.
"""
import os
import pandas as pd
from tqdm import tqdm
import time

# Import our structured modules
from src.data_loaders.job_description_loader import JobDescriptionLoader
from src.data_loaders.candidate_dataset_loader import CandidateDatasetLoader

from src.models.candidate import Candidate

from src.pipeline.retrieval.query_expander import QueryExpander
from src.pipeline.retrieval.candidate_retriever import CandidateRetriever

from src.scorers.skill_scorer import SkillScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.signal_scorer import SignalScorer
from src.scorers.honeypot_scorer import HoneypotScorer

from src.pipeline.semantic_ranker import SemanticRanker
from src.pipeline.final_ranker import FinalRanker
from src.pipeline.reasoning_generator import ReasoningGenerator

from src.services.candidate_text_builder import CandidateTextBuilder
from src.services.embedding_service import EmbeddingService
from src.services.jd_analyzer import JDAnalyzer

from src.utils.text_preprocessing import preprocess_text

def main():
    # Paths
    DEBUG = True
    jd_path = os.path.join(
        "assets",
        "job_description.txt"
    )

    data_path = os.getenv(
        "CANDIDATES_PATH",
        os.path.join(
            "assets",
            "candidates.jsonl"
        )
    )

    output_path = os.getenv(
        "OUTPUT_PATH",
        "ranked_candidates.csv"
    )
    MIN_RETRIEVAL_SCORE = 0.35

    # Load job description
    print("Loading job description...")
    jd_loader = JobDescriptionLoader(jd_path)
    jd_text = jd_loader.load()
    jd = JDAnalyzer.analyze(
        jd_text
    )
    expanded_terms = QueryExpander.expand(
        jd
    )

    if DEBUG:
        print("\n========== JD ANALYZER ==========")
        print("Required Skills:")
        print(jd.required_skills)

        print("\nDomain Keywords:")
        print(jd.domain_keywords)

        print(
            "Min Experience:",
            jd.min_experience
        )

        print(
            "Max Experience:",
            jd.max_experience
        )

        print(
            "Target Experience:",
            jd.target_experience
        )

        print("\nSeniority:")
        print(jd.seniority)
    
    if DEBUG:
        print("\n========== QUERY EXPANDER ==========")
        print(
            sorted(
                expanded_terms
            )
        )
    jd_text_processed = preprocess_text(jd_text)

    # Initialize embedding model
    print("Loading embedding model...")
    embedding_service = EmbeddingService()

    # Encode job description
    jd_embedding = embedding_service.embed_query(
        jd_text_processed
    )

    # Initialize scorers
    skill_scorer = SkillScorer(jd)
    experience_scorer = ExperienceScorer(jd)
    signal_scorer = SignalScorer()
    honeypot_scorer = HoneypotScorer()
    # First pass: extract all candidate texts and metadata for batch processing
    print("Extracting candidate data...")
    prefilter_candidates = []

    # Process candidates file to extract data for batch processing
    candidate_loader = CandidateDatasetLoader(data_path)
    for line_num, candidate_dict in enumerate(tqdm(candidate_loader.load(), desc="Extracting candidate data")):
        try:
            candidate = Candidate.from_dict(candidate_dict)
            if DEBUG and line_num == 0:
                print("\n========== FIRST CANDIDATE ==========")
                print(
                    "Candidate ID:",
                    candidate.candidate_id
                )
            candidate_id = candidate.candidate_id
            if not candidate_id:
                continue

            # Extract skills for skill matching
            candidate_text = CandidateTextBuilder.build(
                candidate
            )

            retrieval_hits, matched_terms = CandidateRetriever.score(
                candidate_text,
                expanded_terms
            )
            exp_score, exp_details = experience_scorer.score(candidate)
            signal_score, signal_details = signal_scorer.score(candidate)
            skill_score, skill_details = skill_scorer.score(candidate)

            if DEBUG and line_num == 0:
                print("\n========== RETRIEVAL ==========")
                print(
                    "Hits:",
                    retrieval_hits
                )

            normalized_hits = min(retrieval_hits / 10.0, 1.0)
            retrieval_score = (
                0.25 * normalized_hits
                + 0.45 * skill_score
                + 0.30 * exp_score
            )

            if retrieval_score < MIN_RETRIEVAL_SCORE:
                continue

            prefilter_candidates.append({
                "candidate": candidate,
                "exp_score": exp_score,
                "exp_details": exp_details,
                "signal_score": signal_score,
                "signal_details": signal_details,
                "skill_score": skill_score,
                "retrieval_score": retrieval_score,
                "skill_details": skill_details
            })

        except Exception as e:
            print(f"Error processing line {line_num}: {e}")
            continue

    total_candidates = len(prefilter_candidates)
    print(f"Candidates surviving retrieval: {total_candidates}")
    TOP_SEMANTIC_POOL = 10000
    print(
        f"\nSemantic Pool Size: {TOP_SEMANTIC_POOL}"
    )
    prefilter_candidates.sort(
        key=lambda x: x["retrieval_score"],
        reverse=True
    )
    if DEBUG:
        print("\n========== RETRIEVAL STAGE ==========")
        print(
            "Candidates after retrieval:",
            len(prefilter_candidates)
        )

    prefilter_candidates = prefilter_candidates[:TOP_SEMANTIC_POOL]
    candidate_texts = []

    for item in prefilter_candidates:
        candidate = item["candidate"]

        candidate_text = (
            CandidateTextBuilder.build(
                candidate
            )
        )
        candidate_texts.append(
            candidate_text
        )
        
    if DEBUG:
        print(
            "\nSemantic Pool Size:",
            len(candidate_texts)
        )
    # Batch-encode all candidate texts
    semantic_start = time.time()
    print(
        "Computing semantic similarities in batches..."
    )
    semantic_ranker = SemanticRanker(
        embedding_service.model
    )

    semantic_scores = (
        semantic_ranker.compute_scores(
            candidate_texts,
            jd_embedding
        )
    )
    print(
        f"\nSemantic stage took "
        f"{time.time() - semantic_start:.2f} sec"
    )
    if DEBUG:
        print("\n========== SEMANTIC RANKER ==========")
        print(
            "Candidates scored:",
            len(semantic_scores)
        )

    for i, score in enumerate(semantic_scores):
        prefilter_candidates[i][
            "semantic_score"
        ] = float(score)

    prefilter_candidates.sort(
        key=lambda x: x[
            "semantic_score"
        ],
        reverse=True
    )

    prefilter_candidates = (
        prefilter_candidates[:5000]
    )
    semantic_scores = [
        item["semantic_score"]
        for item in prefilter_candidates
    ]

    # Compute final scores and generate reasoning
    if DEBUG:
        print("\n========== FINAL RANKER ==========")
        print("Computing final scores and generating reasoning...")
    results = []  # each element: dict with candidate_id, final_score, reasoning
    for idx, item in enumerate(prefilter_candidates):
        candidate = item["candidate"]
        candidate_id = candidate.candidate_id

        exp_score = item["exp_score"]
        exp_details = item["exp_details"]

        signal_score = item["signal_score"]
        signal_details = item["signal_details"]

        skill_score = item["skill_score"]
        skill_details = item["skill_details"]

        # Get pre-computed scores
        semantic_score = semantic_scores[idx]

        matched_skills = skill_details.get("matched_skills", [])

        honeypot_risk = (
            honeypot_scorer.score(
                candidate,
                signal_details
            )
        )

        # Hybrid score
        final_score = (
            FinalRanker.score(
                semantic_score,
                exp_score,
                skill_score,
                signal_score,
                exp_details,
                honeypot_risk
            )
        )
        if DEBUG and idx < 5:
            print("\nCandidate:")
            print(candidate_id)

            print(
                "Semantic:",
                semantic_score
            )

            print(
                "Skill:",
                skill_score
            )

            print(
                "Experience:",
                exp_score
            )

            print(
                "Signal:",
                signal_score
            )

            print(
                "Final:",
                final_score
            )

        # Generate Reasoning
        scores_dict = {
            'semantic': semantic_score,
            'skill': skill_score,
            'experience': exp_score,
            'signals': signal_score,
            'final': final_score
        }
        
        reasoning = (
            ReasoningGenerator.generate(
                {
                    "profile":
                    candidate.profile
                },
                scores_dict,
                matched_skills,
                exp_details,
                signal_details
            )
        )

        results.append({
            'candidate_id': candidate_id,
            'final_score': final_score,
            'reasoning': reasoning
        })

    # Deterministic tie-break: higher score first, then candidate_id lexicographically ascending
    print("Sorting candidates...")
    results.sort(
        key=lambda x: (
            -round(x["final_score"], 4),
            x["candidate_id"]
        )
    )

    # Assign ranks and prepare output
    print("Generating output...")
    output_data = []
    TOP_OUTPUT = 100
    for rank, res in enumerate(results[:TOP_OUTPUT], start=1):
        output_data.append({
            'candidate_id': res['candidate_id'],
            'rank': rank,
            'score': round(res['final_score'], 4),
            'reasoning': res['reasoning']
        })

    # Write to CSV
    df = pd.DataFrame(output_data)
    df.to_csv(
        output_path,
        index=False,
        float_format="%.4f"
    )
    # Show top 10
    print("\nTop 10/100 candidates:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()