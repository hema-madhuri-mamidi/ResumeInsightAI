import unittest

from v2.job_match import calculate_job_match
from v2.skill_gap import analyze_skill_gap


class SkillGapTests(unittest.TestCase):
    def test_analyze_skill_gap_returns_missing_and_recommended_skills(self) -> None:
        parsed_data = {
            "skills": ["Python", "Flask", "SQL"],
        }

        result = analyze_skill_gap(
            parsed_data,
            "Seeking a Python developer with Django, REST APIs, and PostgreSQL experience.",
        )

        self.assertIn("Django", result["missing_skills"])
        self.assertIn("REST API", result["missing_skills"])
        self.assertIn("PostgreSQL", result["missing_skills"])
        self.assertIn("Django", result["recommended_skills_to_learn"])
        self.assertIn("REST API", result["recommended_skills_to_learn"])
        self.assertIn(result["priority"], {"High", "Medium", "Low"})

    def test_analyze_skill_gap_returns_skill_guides_for_missing_skills(self) -> None:
        result = analyze_skill_gap(
            {"skills": ["Python"]},
            "Seeking a backend engineer with Docker and Kubernetes experience.",
        )

        self.assertIn("Docker", result["missing_skills"])
        self.assertIn("Kubernetes", result["missing_skills"])
        self.assertIn("Docker", result["recommended_skills_to_learn"])
        self.assertIn("Kubernetes", result["recommended_skills_to_learn"])

        guides = {item["skill"]: item for item in result["skill_guides"]}
        self.assertIn("Docker", guides)
        self.assertEqual(guides["Docker"]["priority"], "High")
        self.assertIn("Docker Basics", guides["Docker"]["learning_path"])
        self.assertIn("Containerization", guides["Docker"]["reason"])

    def test_analyze_skill_gap_uses_job_match_missing_skills(self) -> None:
        parsed_data = {"skills": ["Python", "Flask", "SQL"]}
        job_description = "Seeking a Python developer with Django, REST APIs, and PostgreSQL experience."

        job_match_result = calculate_job_match(parsed_data, job_description)
        skill_gap_result = analyze_skill_gap(parsed_data, job_description)

        self.assertEqual(skill_gap_result["missing_skills"], job_match_result["missing_skills"])
        self.assertEqual(skill_gap_result["recommended_skills_to_learn"], job_match_result["missing_skills"])
        self.assertEqual(len(skill_gap_result["skill_guides"]), len(job_match_result["missing_skills"]))

    def test_analyze_skill_gap_handles_empty_inputs(self) -> None:
        result = analyze_skill_gap({}, "")

        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["recommended_skills_to_learn"], [])
        self.assertEqual(result["priority"], "Low")
        self.assertEqual(result["skill_guides"], [])


if __name__ == "__main__":
    unittest.main()
