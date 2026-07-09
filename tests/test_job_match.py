import unittest

from v2.job_match import _extract_job_skills, _extract_resume_skills, calculate_job_match


class JobMatchTests(unittest.TestCase):
    def test_calculate_job_match_returns_expected_matches(self) -> None:
        parsed_data = {
            "skills": ["Python", "Django", "Flask", "SQL"],
            "projects": [{"title": "Resume Analyzer", "technologies": ["Python", "Flask"]}],
            "experience": [{"title": "Software Engineer", "organization": "Example Corp"}],
        }

        result = calculate_job_match(
            parsed_data,
            "Looking for a Python Django backend engineer with SQL experience and REST APIs.",
        )

        self.assertGreaterEqual(result["match_percentage"], 0)
        self.assertIn("Python", result["matched_skills"])
        self.assertIn("Django", result["matched_skills"])
        self.assertIn("SQL", result["matched_skills"])
        self.assertIn("REST API", result["missing_skills"])

    def test_skill_extractors_detect_technologies_inside_resume_skill_strings(self) -> None:
        parsed_data = {
            "skills": [
                "Languages Python",
                "Developer Tools Git",
                "Web Development HTML5",
                "Web Development CSS3",
                "ML TensorFlow",
                "DSA & OOP Arrays",
            ]
        }

        self.assertEqual(
            _extract_resume_skills(parsed_data),
            ["Python", "Git", "HTML", "CSS", "TensorFlow"],
        )
        self.assertEqual(
            _extract_job_skills("Python Django React Docker Git REST API AWS"),
            ["REST API", "React", "Django", "Python", "Docker", "AWS", "Git"],
        )

    def test_extract_resume_skills_uses_projects_experience_certifications_and_activities(self) -> None:
        parsed_data = {
            "skills": ["Python"],
            "projects": [
                {
                    "title": "React Dashboard",
                    "technologies": ["Chart.js"],
                    "description": "Built with TensorFlow and JavaScript.",
                }
            ],
            "experience": [
                {
                    "description": "Worked with Node.js and Docker for deployment.",
                }
            ],
            "certifications": [{"name": "AWS Certified"}],
            "activities": [{"description": "Used Kubernetes for orchestration."}],
        }

        extracted_skills = _extract_resume_skills(parsed_data)

        self.assertIn("Python", extracted_skills)
        self.assertIn("React", extracted_skills)
        self.assertIn("Chart.js", extracted_skills)
        self.assertIn("TensorFlow", extracted_skills)
        self.assertIn("JavaScript", extracted_skills)
        self.assertIn("Node.js", extracted_skills)
        self.assertIn("Docker", extracted_skills)
        self.assertIn("AWS", extracted_skills)
        self.assertIn("Kubernetes", extracted_skills)
        self.assertEqual(len(extracted_skills), len(set(extracted_skills)))

    def test_calculate_job_match_handles_empty_job_description(self) -> None:
        result = calculate_job_match({}, "")

        self.assertEqual(result["match_percentage"], 0)
        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])


if __name__ == "__main__":
    unittest.main()
