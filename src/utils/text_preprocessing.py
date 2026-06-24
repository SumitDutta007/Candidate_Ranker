"""
Text preprocessing utilities
"""
import re
from typing import Any


def preprocess_text(text: str) -> str:
    """Basic text preprocessing: lowercase, remove extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_candidate_text(candidate: Any) -> str:
    """
    Extract and combine textual fields from a candidate for embedding.
    Expects candidate to have profile and career_history attributes/dicts.
    """
    parts = []
    # Profile summary and headline
    profile = getattr(candidate, 'profile', None) or candidate.get('profile', {}) if isinstance(candidate, dict) else {}
    if isinstance(profile, dict):
        if 'summary' in profile:
            parts.append(profile['summary'])
        if 'headline' in profile:
            parts.append(profile['headline'])
    # Career history descriptions
    career_history = getattr(candidate, 'career_history', None) or candidate.get('career_history', []) if isinstance(candidate, dict) else []
    if isinstance(career_history, list):
        for exp in career_history:
            if isinstance(exp, dict) and 'description' in exp:
                parts.append(exp['description'])
    # Combine and preprocess
    full_text = " ".join(parts)
    return preprocess_text(full_text)


def extract_skills(candidate: Any) -> list:
    """Extract skills list from candidate."""
    if isinstance(candidate, dict):
        return candidate.get('skills', [])
    return getattr(candidate, 'skills', [])