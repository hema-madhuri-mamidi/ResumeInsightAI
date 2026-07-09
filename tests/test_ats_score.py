import unittest

from v2.ats_score import calculate_ats_score


class AtsScoreTests(unittest.TestCase):
    def test_calculate_ats_score_returns_full_points_for_complete_resume(self) -> None:
        parsed_data = {
            "contact": {
                "email": "user@example.com",
                "phone": "1234567890",
                "github": "https://github.com/user",
                "linkedin": "https://linkedin.com/in/user",
            },
            "education": {
                "degree": "B.Tech",
                "branch": "Computer Science",
                "college": "Example University",
                "cgpa": "9.2",
            },
            "skills": ["Python", "Django", "Flask", "SQL"],
            "projects": [
                {
                    "title": "Resume Analyzer",
                    "technologies": ["Python", "Flask"],
                    "description": ["Built a parser for resumes"],
                }
            ],
            "experience": [
                {
                    "title": "Software Engineer",
                    "organization": "Example Corp",
                    "duration": "2022 - Present",
                }
            ],
            "certifications": ["AWS Certified Developer"],
        }

        score = calculate_ats_score(parsed_data)

        self.assertEqual(score["overall_score"], 100)
        self.assertEqual(score["section_scores"], {
            "contact": 15,
            "education": 15,
            "skills": 20,
            "projects": 25,
            "experience": 15,
            "certifications": 10,
        })
        self.assertTrue(any("Strong technical projects" in strength for strength in score["strengths"]))
        self.assertEqual(score["improvements"], [])

    def test_calculate_ats_score_flags_missing_sections(self) -> None:
        parsed_data = {
            "contact": {
                "email": "user@example.com",
            },
            "education": {},
            "skills": [],
            "projects": [],
            "experience": [],
            "certifications": [],
        }

        score = calculate_ats_score(parsed_data)

        self.assertLess(score["overall_score"], 100)
        self.assertIn("contact", score["section_scores"])
        self.assertIn("Add professional experience", score["improvements"])
        self.assertIn(
            "GitHub link could not be verified. Ensure the full GitHub URL is visible and ATS-readable.",
            score["improvements"],
        )
        self.assertIn(
            "LinkedIn link could not be verified. Ensure the full LinkedIn URL is visible and ATS-readable.",
            score["improvements"],
        )


if __name__ == "__main__":
    unittest.main()
