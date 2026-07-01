import re

from ..models.job_description import JobDescription
from .skill_taxonomy import TECHNOLOGY_ALIASES

class JDAnalyzer:

    SENIORITY_PATTERNS = {
        "staff": r"\bstaff\b",
        "principal": r"\bprincipal\b",
        "senior": r"\bsenior\b",
        "lead": r"\blead\b",
        "manager": r"\bmanager\b",
    }

    EXPERIENCE_PATTERNS = [
        r"(\d+)\+?\s*years",
        r"minimum\s*(\d+)\s*years",
        r"at least\s*(\d+)\s*years"
    ]
    PREFERRED_HEADERS = [
        "preferred",
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "good to have",
        "bonus",
        "desired",
        "plus"
    ]

    SECTION_HEADERS = [
        "responsibilities",
        "requirements",
        "qualifications",
        "about",
        "benefits",
        "what you'll do",
        "what you will do",
        "must have",
        "minimum qualifications"
    ]

    @staticmethod
    def extract_bullet_points(text):

        bullets = []

        for line in text.splitlines():

            line = line.strip()

            if (
                line.startswith("-")
                or line.startswith("•")
                or line.startswith("*")
            ):
                bullets.append(
                    line[1:].strip()
                )

        return bullets

    @staticmethod
    def analyze(jd_text):
        text = jd_text.lower()
        bullets = JDAnalyzer.extract_bullet_points(jd_text)
        
        

        required_skills = []

        for canonical_skill, aliases in TECHNOLOGY_ALIASES.items():

            for alias in aliases:

                if alias in text:

                    required_skills.append(canonical_skill)

                    break

        required_skills = sorted(
            list(set(required_skills))
        )

        preferred_skills = []

        preferred_sections = []

        capture = False

        for line in jd_text.splitlines():
            lower = line.lower().strip()
            if any(header in lower for header in JDAnalyzer.PREFERRED_HEADERS):
                capture = True
                continue

            if capture:
                # stop when next section starts
                if any(lower.startswith(section) for section in JDAnalyzer.SECTION_HEADERS):
                    break

                preferred_sections.append(lower)

        preferred_text = " ".join(preferred_sections).lower()

        for canonical_skill, aliases in TECHNOLOGY_ALIASES.items():

            for alias in aliases:

                if re.search(r"\b" + re.escape(alias) + r"\b", text):
                    required_skills.append(canonical_skill)
                    break

        preferred_skills = sorted(
            list(set(preferred_skills))
        )
        
        min_experience = 0
        max_experience = 0
        target_experience = 0

        range_match = re.search(
            r"(\d+)\s*-\s*(\d+)\s*years",
            text
        )

        if range_match:

            min_experience = float(
                range_match.group(1)
            )

            max_experience = float(
                range_match.group(2)
            )

            target_experience = (
                min_experience +
                max_experience
            ) / 2

        else:

            for pattern in JDAnalyzer.EXPERIENCE_PATTERNS:

                match = re.search(
                    pattern,
                    text
                )

                if match:

                    min_experience = float(
                        match.group(1)
                    )

                    max_experience = min_experience + 3

                    target_experience = (
                        min_experience +
                        max_experience
                    ) / 2

                    break

        seniority = "mid"

        for level, pattern in JDAnalyzer.SENIORITY_PATTERNS.items():
            if re.search(pattern, text):
                seniority = level
                break

        domain_keywords = sorted(
            list(
                set(
                    required_skills +
                    preferred_skills
                )
            )
        )

        return JobDescription(
            required_skills=required_skills,
            preferred_skills=preferred_skills,

            must_have_terms=required_skills,
            nice_to_have_terms=preferred_skills,

            domain_keywords=domain_keywords,

            min_experience=min_experience,
            max_experience=max_experience,
            target_experience=target_experience,
            seniority=seniority
        )