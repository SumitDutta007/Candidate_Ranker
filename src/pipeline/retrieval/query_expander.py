from .ontology import SKILL_ONTOLOGY

class QueryExpander:

    @staticmethod
    def expand(jd):

        expanded = set()

        for skill in jd.required_skills:

            expanded.add(skill.lower())

            if skill.lower() in SKILL_ONTOLOGY:
                expanded.update(
                    SKILL_ONTOLOGY[
                        skill.lower()
                    ]
                )

        return expanded