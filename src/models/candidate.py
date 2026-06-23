"""
Candidate data model
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Candidate:
    candidate_id: str

    profile: Dict[str, Any] = field(default_factory=dict)

    career_history: List[Dict[str, Any]] = field(default_factory=list)

    skills: List[Dict[str, Any]] = field(default_factory=list)

    education: List[Dict[str, Any]] = field(default_factory=list)

    certifications: List[Dict[str, Any]] = field(default_factory=list)

    languages: List[Dict[str, Any]] = field(default_factory=list)

    redrob_signals: Dict[str, Any] = field(default_factory=dict)

    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candidate":
        """Create Candidate instance from raw dictionary."""
        # Extract known fields, keep rest in raw_data for extensibility
        known_fields = {
            "candidate_id",
            "profile",
            "career_history",
            "skills",
            "education",
            "certifications",
            "languages",
            "redrob_signals",
        }
        init_kwargs = {k: data[k] for k in known_fields if k in data}
        init_kwargs['raw_data'] = {k: v for k, v in data.items() if k not in known_fields}
        return cls(**init_kwargs)