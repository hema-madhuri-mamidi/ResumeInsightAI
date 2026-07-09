import unittest

from v2.suggestions import generate_suggestions


class SuggestionsTests(unittest.TestCase):
    def test_generate_suggestions_for_missing_sections(self) -> None:
        parsed_data = {
            "contact": {"email": "user@example.com"},
            "experience": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "activities": [],
        }

        suggestions = generate_suggestions(parsed_data)

        self.assertIn("Add LinkedIn profile", suggestions["suggestions"])
        self.assertIn("Add GitHub profile", suggestions["suggestions"])
        self.assertIn("Add portfolio link", suggestions["suggestions"])
        self.assertIn("Add experience section", suggestions["suggestions"])
        self.assertIn("Add more projects", suggestions["suggestions"])
        self.assertIn("Add more skills", suggestions["suggestions"])
        self.assertIn("Add certifications", suggestions["suggestions"])
        self.assertIn("Add activities", suggestions["suggestions"])

    def test_generate_suggestions_for_complete_resume(self) -> None:
        parsed_data = {
            "contact": {
                "linkedin": "https://linkedin.com/in/user",
                "github": "https://github.com/user",
                "portfolio": "https://example.com",
            },
            "experience": [{"title": "Developer"}],
            "projects": [{}, {}, {}],
            "skills": ["Python", "Django", "Flask", "React", "SQL"],
            "certifications": ["AWS"],
            "activities": ["Hackathons"],
        }

        suggestions = generate_suggestions(parsed_data)

        self.assertEqual(suggestions["suggestions"], [])


if __name__ == "__main__":
    unittest.main()
