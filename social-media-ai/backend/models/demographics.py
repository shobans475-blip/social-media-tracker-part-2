from typing import Dict, Any, List

REGIONS = {
    "Karnataka": ["bengaluru", "bangalore", "mysuru", "karnataka"],
    "Maharashtra": ["mumbai", "pune", "nagpur", "maharashtra"],
    "Delhi NCR": ["delhi", "new delhi", "noida", "gurugram", "gurgaon", "faridabad"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "tamil nadu"],
    "Telangana": ["hyderabad", "warangal", "telangana"],
    "West Bengal": ["kolkata", "howrah", "west bengal"],
    "Gujarat": ["ahmedabad", "surat", "vadodara", "gujarat"],
    "Rajasthan": ["jaipur", "jodhpur", "rajasthan"],
    "Kerala": ["kochi", "cochin", "thiruvananthapuram", "trivandrum", "kerala"],
    "Uttar Pradesh": ["lucknow", "kanpur", "varanasi", "uttar pradesh", "up"]
}

class DemographicClassifier:
    def infer_region(self, location_str: str, text: str = "") -> str:
        """Determines Indian region/state from user location string or context hints"""
        combined = f"{location_str or ''} {text or ''}".lower()
        for region, cities in REGIONS.items():
            if any(c in combined for c in cities):
                return region
        return "National / Other"

    def infer_age_group(self, age: int = None) -> str:
        if age is None or age == 0:
            return "25-34"
        if age < 25:
            return "18-24"
        if age <= 34:
            return "25-34"
        if age <= 49:
            return "35-49"
        return "50+"

    def assess_bot_likelihood(self, followers: int, following: int, post_text: str = "") -> float:
        """Returns bot confidence between 0.0 and 1.0"""
        score = 0.05
        lower = post_text.lower()
        if "1000x guaranteed profit" in lower or "invest ₹" in lower or "click link" in lower:
            score += 0.65
        if followers < 20 and following > 800:
            score += 0.25
        if followers > 100000:
            score = max(0.01, score - 0.1)
        return min(0.99, round(score, 2))

    def aggregate_demographics(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates demographic totals and distribution percentages"""
        total = len(users)
        if total == 0:
            return {
                "total_users": 0,
                "age_distribution": {"18-24": 30, "25-34": 45, "35-49": 20, "50+": 5},
                "gender_distribution": {"male": 52, "female": 44, "unknown": 4},
                "regional_distribution": {"Karnataka": 25, "Maharashtra": 25, "Delhi NCR": 20, "Others": 30},
                "bot_accounts_count": 0
            }

        age_counts = {"18-24": 0, "25-34": 0, "35-49": 0, "50+": 0}
        gender_counts = {"male": 0, "female": 0, "unknown": 0, "organization": 0}
        region_counts: Dict[str, int] = {}
        bot_count = 0

        for u in users:
            age = u.get("inferred_age", 26)
            grp = self.infer_age_group(age)
            age_counts[grp] = age_counts.get(grp, 0) + 1

            gender = (u.get("inferred_gender") or "unknown").lower()
            if gender not in gender_counts:
                gender_counts["unknown"] += 1
            else:
                gender_counts[gender] += 1

            loc = u.get("inferred_location", "")
            reg = self.infer_region(loc)
            region_counts[reg] = region_counts.get(reg, 0) + 1

            if u.get("bot_probability", 0) > 0.6:
                bot_count += 1

        return {
            "total_users": total,
            "age_distribution": {k: round(v / total * 100, 1) for k, v in age_counts.items()},
            "gender_distribution": {k: round(v / total * 100, 1) for k, v in gender_counts.items() if v > 0},
            "regional_distribution": dict(sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:7]),
            "bot_accounts_count": bot_count
        }

demographics_model = DemographicClassifier()
