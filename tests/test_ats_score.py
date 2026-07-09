import unittest

from v2.ats_score import calculate_ats_score
from v2.suggestions import generate_suggestions


class AtsScoreTests(unittest.TestCase):
    def test_calculate_ats_score_rewards_detailed_resume_sections(self) -> None:
        parsed_data = {
            "contact": {
                "name": "Alex Morgan",
                "email": "user@example.com",
                "phone": "1234567890",
                "github": "https://github.com/user",
                "linkedin": "https://linkedin.com/in/user",
                "portfolio": "https://alex.dev",
            },
            "education": {
                "degree": "B.Tech",
                "branch": "Computer Science",
                "college": "Example University",
                "cgpa": "9.2",
                "year": "2024",
            },
            "skills": ["Python", "Django", "Flask", "React", "SQL", "AWS", "Git", "Docker"],
            "projects": [
                {
                    "title": "Resume Analyzer",
                    "technologies": ["Python", "Flask"],
                    "description": ["Built a parser for resumes"],
                    "highlights": ["Reduced processing time by 40%"],
                },
                {
                    "title": "Warehouse Dashboard",
                    "technologies": ["React", "Node"],
                    "description": ["Built monitoring dashboard"],
                    "highlights": ["Improved visibility"],
                },
            ],
            "experience": [
                {
                    "title": "Software Engineer",
                    "organization": "Example Corp",
                    "duration": "2022 - Present",
                    "description": ["Led API modernization"],
                }
            ],
            "certifications": ["AWS Certified Developer", "Google Cloud Associate"],
            "activities": ["Hackathon Winner", "Open Source Maintainer"],
        }

        score = calculate_ats_score(parsed_data)

        self.assertEqual(score["overall_score"], 100)
        self.assertEqual(score["section_scores"]["contact"], 15)
        self.assertGreaterEqual(score["section_scores"]["education"], 13)
        self.assertEqual(score["section_scores"]["projects"], 25)
        self.assertGreaterEqual(score["section_scores"]["skills"], 15)
        self.assertGreaterEqual(score["section_scores"]["experience"], 15)
        self.assertGreaterEqual(score["section_scores"]["certifications"], 10)
        self.assertTrue(any("Strong technical projects" in strength for strength in score["strengths"]))
        self.assertEqual(score["improvements"], [])

    def test_calculate_ats_score_reduces_scores_for_incomplete_sections(self) -> None:
        parsed_data = {
            "contact": {
                "name": "Alex Morgan",
                "email": "user@example.com",
            },
            "education": {
                "degree": "B.Tech",
                "college": "Example University",
            },
            "skills": ["Python", "Flask", "SQL"],
            "projects": [{"title": "Resume Parser"}],
            "experience": [{"title": "Research Assistant"}],
            "certifications": [],
            "activities": [],
        }

        score = calculate_ats_score(parsed_data)

        self.assertLess(score["overall_score"], 100)
        self.assertLess(score["section_scores"]["contact"], 15)
        self.assertLess(score["section_scores"]["education"], 15)
        self.assertLess(score["section_scores"]["projects"], 25)
        self.assertLess(score["section_scores"]["skills"], 20)
        self.assertLess(score["section_scores"]["experience"], 15)
        self.assertTrue(any("Improve your project descriptions" in improvement for improvement in score["improvements"]))
        self.assertTrue(any("Add more relevant frameworks and technical tools." in improvement for improvement in score["improvements"]))

    def test_generate_suggestions_uses_section_quality(self) -> None:
        parsed_data = {
            "contact": {"name": "Alex Morgan"},
            "education": {"degree": "B.Tech"},
            "skills": ["Python", "Flask"],
            "projects": [{"title": "Resume Parser"}],
            "experience": [{"title": "Research Assistant"}],
            "certifications": [],
            "activities": [],
        }

        suggestions = generate_suggestions(parsed_data)

        self.assertIn("Add your email address.", suggestions["suggestions"])
        self.assertIn("Add your phone number.", suggestions["suggestions"])
        self.assertIn("Include graduation year or CGPA.", suggestions["suggestions"])
        self.assertIn("Add more relevant frameworks and technical tools.", suggestions["suggestions"])
        self.assertIn("Improve your project descriptions by adding technologies and achievements.", suggestions["suggestions"])


if __name__ == "__main__":
    unittest.main()
