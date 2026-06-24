from ...utils.scoring_weights import (
    PRODUCT_COMPANIES_INDICATORS, CONSULTING_FIRMS
)

class CompanyAnalyzer:
    @staticmethod
    def analyze(candidate):

        profile = candidate.profile

        # Product company signal
        current_company = profile.get('current_company', '').lower()
        career_history = candidate.career_history
        

        # Check current company
        is_product = any(indicator in current_company for indicator in PRODUCT_COMPANIES_INDICATORS)
        # Check past companies if current not product
        if not is_product:
            for exp in career_history:
                company_name = exp.get('company', '').lower()
                if any(indicator in company_name for indicator in PRODUCT_COMPANIES_INDICATORS):
                    is_product = True
                    break

        # Penalty for consulting firms (if currently or recently in consulting)
        consulting_companies = 0

        for exp in career_history:
            company_name = exp.get("company", "").lower()

            if any(
                firm in company_name
                for firm in CONSULTING_FIRMS
            ):
                consulting_companies += 1
        is_consulting = consulting_companies > 0
        consulting_only = (
            len(career_history) > 0 and
            consulting_companies == len(career_history)
        )
        # Combine: product company gives boost, consulting gives penalty
        product_score = 1.0 if is_product else 0.5

        consulting_score = (
            0.25 if consulting_only
            else (0.75 if is_consulting else 1.0)
        )

        return {
            "is_product": is_product,
            "is_consulting": is_consulting,
            "consulting_only": consulting_only,
            "product_score": product_score,
            "consulting_score": consulting_score,
        }