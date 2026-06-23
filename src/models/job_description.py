from dataclasses import dataclass


@dataclass
class JobDescription:

    required_skills: list[str]
    preferred_skills: list[str]

    must_have_terms: list[str]
    nice_to_have_terms: list[str]

    domain_keywords: list[str]

    min_experience: float
    max_experience: float
    target_experience: float
    
    seniority: str