"""
Skill match scorer
"""
import re
import numpy as np
from typing import Tuple, Dict, Any, List
from .base_scorer import BaseScorer
from ..models.candidate import Candidate
from ..utils.text_preprocessing import extract_skills


class SkillScorer(BaseScorer):
    """Computes skill match score against desired skills from the JD."""

    def __init__(self, jd):
        self.jd = jd

        desired_skills = jd.required_skills

        self.desired_norm = [
            re.sub(r'[-_]', ' ', s.lower())
            for s in desired_skills
        ]

    def score(self, candidate: Candidate) -> Tuple[float, Dict[str, Any]]:
        """Return skill match score in [0, 1] and details."""
        skills = extract_skills(candidate)
        if not skills:
            return 0.0, {'matched_skills': [], 'skill_score': 0.0}

        matched = []
        total_weight = 0.0
        weighted_sum = 0.0

        for skill in skills:
            skill_name = skill.get('name', '').lower()
            skill_name_norm = re.sub(r'[-_]', ' ', skill_name)
            match_found = False
            for i, desired in enumerate(self.desired_norm):
                if desired in skill_name_norm or skill_name_norm in desired:
                    match_found = True
                    matched.append(skill['name'])
                    # Proficiency weight
                    prof = skill.get('proficiency', 'beginner')
                    prof_weight = {'beginner': 0.25, 'intermediate': 0.5, 'advanced': 0.75, 'expert': 1.0}.get(prof, 0.25)
                    # Endorsements weight (log scale)
                    endorsements = skill.get('endorsements', 0)
                    endorsements_weight = np.log1p(endorsements) / np.log1p(100)  # normalize assuming max 100 endorsements
                    # Duration weight (normalize assuming max 60 months)
                    duration = skill.get('duration_months', 0)
                    duration_weight = min(duration / 60.0, 1.0) if duration > 0 else 0.0
                    # Combined weight for this skill
                    skill_weight = prof_weight * 0.5 + endorsements_weight * 0.3 + duration_weight * 0.2
                    weighted_sum += skill_weight
                    total_weight += 1.0  # each matched skill contributes at most 1 to total_weight
                    break  # avoid double counting if multiple desired skills match
            # If no match, we don't add to total_weight

        if total_weight > 0:
            score = min(weighted_sum / total_weight, 1.0)
        else:
            score = 0.0

        details = {
            'matched_skills': matched,
            'skill_score': score,
            'total_skills_considered': len(skills)
        }
        return score, details