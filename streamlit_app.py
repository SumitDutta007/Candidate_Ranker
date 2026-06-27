import json
import tempfile
import pandas as pd
import streamlit as st

from src.models.candidate import Candidate

from src.data_loaders.candidate_dataset_loader import (
    CandidateDatasetLoader
)

from src.services.jd_analyzer import JDAnalyzer
from src.services.embedding_service import EmbeddingService
from src.services.candidate_text_builder import (
    CandidateTextBuilder
)

from src.pipeline.retrieval.query_expander import (
    QueryExpander
)

from src.pipeline.retrieval.candidate_retriever import (
    CandidateRetriever
)

from src.pipeline.semantic_ranker import (
    SemanticRanker
)

from src.pipeline.final_ranker import (
    FinalRanker
)

from src.pipeline.reasoning_generator import (
    ReasoningGenerator
)

from src.scorers.skill_scorer import SkillScorer
from src.scorers.experience_scorer import ExperienceScorer
from src.scorers.signal_scorer import SignalScorer
from src.scorers.honeypot_scorer import HoneypotScorer

from src.utils.text_preprocessing import (
    preprocess_text
)

progress = st.progress(0)
status = st.empty()
TOP_OUTPUT = 100
st.set_page_config(
    page_title="Redrob Candidate Ranker",
    layout="wide"
)

st.title(
    "Intelligent Candidate Discovery & Ranking Engine"
)

st.write(
    "Upload a Job Description and Candidate Sample"
)

jd_file = st.file_uploader(
    "Job Description"
)

candidate_file = st.file_uploader(
    "Candidate Sample",
)
with st.expander(
    "Ranking Pipeline"
):

    st.markdown("""
    Job Description
        ↓
    JD Analyzer
        ↓
    Query Expansion
        ↓
    Ontology Expansion
        ↓
    Candidate Retrieval
        ↓
    Semantic Ranking
        ↓
    Hybrid Scoring
        ↓
    Honeypot Detection
        ↓
    Explanation Generation
        ↓
    Top 100 Candidates
    """)

if st.button("Run Ranking"):

    if not jd_file or not candidate_file:
        st.error(
            "Please upload both files."
        )
        st.stop()

    with st.spinner(
        "Ranking candidates..."
    ):

        jd_text = (
            jd_file.read()
            .decode("utf-8")
        )
        status.write(
            "Analyzing JD..."
        )

        progress.progress(10)
        jd = JDAnalyzer.analyze(
            jd_text
        )

        status.write(
            "Expanding query..."
        )
        progress.progress(20)
        expanded_terms = (
            QueryExpander.expand(jd)
        )

        st.success(
            f"Detected {len(jd.required_skills)} skills"
        )

        embedding_service = (
            EmbeddingService()
        )

        jd_embedding = (
            embedding_service.embed_query(
                preprocess_text(
                    jd_text
                )
            )
        )

        skill_scorer = (
            SkillScorer(jd)
        )

        experience_scorer = (
            ExperienceScorer(jd)
        )

        signal_scorer = (
            SignalScorer()
        )

        honeypot_scorer = (
            HoneypotScorer()
        )

        candidates = []

        if candidate_file.name.endswith(
            ".json"
        ):

            candidates_raw = json.load(
                candidate_file
            )

        else:

            candidates_raw = []

            for line in (
                candidate_file
                .read()
                .decode("utf-8")
                .splitlines()
            ):

                if line.strip():

                    candidates_raw.append(
                        json.loads(line)
                    )

        # Funnel statistics
        total_candidates = len(candidates_raw)
        retrieved_count = 0

        for row in candidates_raw:

            candidate = (
                Candidate.from_dict(row)
            )

            candidate_text = CandidateTextBuilder.build(candidate)

            hits = CandidateRetriever.score(
                candidate_text,
                expanded_terms
            )
            

            if hits <= 0:
                continue
            retrieved_count += 1

            exp_score, exp_details = (
                experience_scorer.score(
                    candidate
                )
            )

            signal_score, signal_details = (
                signal_scorer.score(
                    candidate
                )
            )

            skill_score, skill_details = (
                skill_scorer.score(
                    candidate
                )
            )

            candidates.append({
                "candidate": candidate,
                "candidate_text": candidate_text,
                "exp_score": exp_score,
                "exp_details": exp_details,
                "signal_score": signal_score,
                "signal_details": signal_details,
                "skill_score": skill_score,
                "skill_details": skill_details
            })
            status.write(
                f"Retrieved {len(candidates)} candidates..."
            )
            progress.progress(30 + int(70 * len(candidates) / len(candidates_raw))
            )
        TOP_SEMANTIC_POOL = 2000

        candidates = sorted(
            candidates,
            key=lambda x: (
                x["exp_score"] +
                x["skill_score"] +
                x["signal_score"]
            ),
            reverse=True
        )

        candidates = candidates[
            :TOP_SEMANTIC_POOL
        ]
        candidate_texts = [
            item["candidate_text"]
            for item in candidates
        ]

        semantic_pool_size = len(candidates)
        semantic_ranker = (
            SemanticRanker(
                embedding_service.model
            )
        )
        status.write(
            f"Computing semantic scores for {len(candidates)} candidates..."
        )
        progress.progress(70)

        st.write(
            f"Retrieved: {retrieved_count:,}"
        )

        st.write(
            f"Semantic Pool: {len(candidates):,}"
        )

        st.write(
            f"Texts to Embed: {len(candidate_texts):,}"
        )
        semantic_scores = (
            semantic_ranker.compute_scores(
                candidate_texts,
                jd_embedding
            )
        )
        st.subheader("Candidate Funnel")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Input Pool",
            f"{total_candidates:,}"
        )

        col2.metric(
            "Retrieved",
            f"{retrieved_count:,}"
        )

        col3.metric(
            "Semantic Pool",
            f"{semantic_pool_size:,}"
        )

        col4.metric(
            "Final Output",
            "100"
        )

        results = []
        for idx, item in enumerate(
            candidates
        ):

            candidate = item[
                "candidate"
            ]

            semantic_score = (
                semantic_scores[idx]
            )

            honeypot_risk = (
                honeypot_scorer.score(
                    candidate,
                    item["signal_details"]
                )
            )

            final_score = (
                FinalRanker.score(
                    semantic_score,
                    item["exp_score"],
                    item["skill_score"],
                    item["signal_score"],
                    item["exp_details"],
                    honeypot_risk
                )
            )
            status.write(
                f"Generating reasoning for candidate {idx + 1} / {len(candidates)}..."
            )
            progress.progress(70 + int(30 * (idx + 1) / len(candidates))
            )

            reasoning = (
                ReasoningGenerator.generate(
                    {
                        "profile":
                        candidate.profile
                    },
                    {
                        "semantic":
                        semantic_score,
                        "skill":
                        item["skill_score"],
                        "experience":
                        item["exp_score"],
                        "signals":
                        item["signal_score"],
                        "final":
                        final_score
                    },
                    item[
                        "skill_details"
                    ].get(
                        "matched_skills",
                        []
                    ),
                    item[
                        "exp_details"
                    ],
                    item[
                        "signal_details"
                    ]
                )
            )

            results.append({
                "candidate_id":
                candidate.candidate_id,

                "score":
                final_score,

                "reasoning":
                reasoning
            })

        progress.progress(100)
        status.write(
            "Ranking complete!"
        )
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        output = []

        for rank, row in enumerate(
            results[:TOP_OUTPUT],
            start=1
        ):

            output.append({
                "candidate_id":
                row["candidate_id"],

                "rank":
                rank,

                "score":
                round(
                    row["score"],
                    4
                ),

                "reasoning":
                row["reasoning"]
            })

        df = pd.DataFrame(
            output
        )

        st.markdown(
            f"""
        ### Ranking Pipeline

        {total_candidates:,} Candidates
        ↓
        {retrieved_count:,} Retrieved
        ↓
        {semantic_pool_size:,} Semantic Ranking
        ↓
        100 Final Candidates
        """
        )

        st.dataframe(
            df
        )

        csv = (
            df.to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            "Download CSV",
            csv,
            "Certified Accident.csv",
            "text/csv"
        )