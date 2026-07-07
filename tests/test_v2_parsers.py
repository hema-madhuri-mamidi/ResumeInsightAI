import unittest

from v2.certification_parser import extract_certifications
from v2.experience_parser import extract_experience
from v2.project_parser import extract_projects
from v2.section_detector import detect_sections
from v2.skills_parser import extract_skills


class V2ParserTests(unittest.TestCase):
    def test_extract_projects_parses_title_technologies_and_description(self) -> None:
        section_lines = [
            "Smart Attendance System",
            "Python, Django, React",
            "• Built a full-stack attendance platform",
            "• Reduced manual errors by 40%",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Smart Attendance System")
        self.assertEqual(projects[0]["technologies"], ["Python", "Django", "React"])
        self.assertEqual(
            projects[0]["description"],
            [
                "Built a full-stack attendance platform",
                "Reduced manual errors by 40%",
            ],
        )

    def test_extract_experience_parses_title_organization_and_description(self) -> None:
        section_lines = [
            "Software Engineer",
            "ABC Corp | Jan 2023 - Present",
            "• Built REST APIs",
            "• Improved uptime to 99.9%",
        ]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Corp")
        self.assertEqual(experience[0]["duration"], "Jan 2023 - Present")
        self.assertEqual(
            experience[0]["description"],
            ["Built REST APIs", "Improved uptime to 99.9%"],
        )

    def test_extract_projects_stops_before_new_section_headings(self) -> None:
        section_lines = [
            "Smart Attendance System",
            "Python, Django",
            "• Built a platform",
            "Activities",
            "Volunteered for hackathons",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Smart Attendance System")
        self.assertEqual(projects[0]["description"], ["Built a platform"])

    def test_extract_projects_treats_technology_lines_as_technologies(self) -> None:
        section_lines = [
            "Niyo Voice Job Portal",
            "React, Django, Web Speech API",
            "• Built a voice-first platform",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Niyo Voice Job Portal")
        self.assertEqual(projects[0]["technologies"], ["React", "Django", "Web Speech API"])

    def test_extract_projects_strips_link_metadata_from_titles(self) -> None:
        section_lines = [
            "Wallet Watch — Expense Tracker (Deployed) Live Demo | GitHub",
            "HTML, CSS, Bootstrap, Python, Django, Chart.js | Render",
            "• Built a full-stack expense management application",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Wallet Watch — Expense Tracker")
        self.assertEqual(
            projects[0]["technologies"],
            ["HTML", "CSS", "Bootstrap", "Python", "Django", "Chart.js"],
        )

    def test_extract_projects_keeps_first_project_when_followed_by_technology_lines(self) -> None:
        section_lines = [
            "Niyo Voice Job Portal",
            "React, Django, Web Speech API",
            "• Built a voice-first platform",
            "Wallet Watch — Expense Tracker",
            "HTML, CSS, Bootstrap, Python, Django, Chart.js",
            "• Built a full-stack expense management application",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "Niyo Voice Job Portal")
        self.assertEqual(projects[1]["title"], "Wallet Watch — Expense Tracker")

    def test_extract_projects_separates_multiple_project_titles(self) -> None:
        section_lines = [
            "Student Performance Analysis",
            "Mini Web Game (HTML, CSS, JavaScript)",
            "• Built a small browser game",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "Student Performance Analysis")
        self.assertEqual(projects[1]["title"], "Mini Web Game")

    def test_extract_projects_detects_titles_with_technology_names(self) -> None:
        section_lines = [
            "AI Career Portal Web Application",
            "React, Django, PostgreSQL",
            "• Built a portal",
            "Student Management System",
            "Python | Django | SQLite",
            "• Built a management system",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "AI Career Portal Web Application")
        self.assertEqual(projects[1]["title"], "Student Management System")

    def test_extract_projects_keeps_first_project_when_title_has_parenthetical_technologies(self) -> None:
        section_lines = [
            "Niyo Voice Job Portal (React, Django, Web Speech API)",
            "React, Django, Web Speech API",
            "• Built a voice-first platform",
            "Wallet Watch — Expense Tracker (Deployed) Live Demo | GitHub",
            "HTML, CSS, Bootstrap, Python, Django, Chart.js",
            "• Built a full-stack expense management application",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "Niyo Voice Job Portal")
        self.assertEqual(projects[1]["title"], "Wallet Watch — Expense Tracker")

    def test_extract_projects_detects_titles_with_technology_names_and_metadata(self) -> None:
        section_lines = [
            "AI Career Portal Web Application (React, Django, PostgreSQL)",
            "React, Django, PostgreSQL",
            "• Built a portal",
            "Student Management System",
            "Python | Django | SQLite",
            "• Built a management system",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "AI Career Portal Web Application")
        self.assertEqual(projects[1]["title"], "Student Management System")

    def test_extract_projects_restores_resume6_style_project_detection(self) -> None:
        section_lines = [
            "AI Career Portal Web Application",
            "Django • Bootstrap • SQLite",
            "Developed a web portal",
            "Student Management System",
            "Django • Python • SQLite",
            "Developed a management system",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0]["title"], "AI Career Portal Web Application")
        self.assertEqual(projects[0]["technologies"], ["Django", "Bootstrap", "SQLite"])
        self.assertEqual(projects[0]["description"], ["Developed a web portal"])
        self.assertEqual(projects[1]["title"], "Student Management System")
        self.assertEqual(projects[1]["technologies"], ["Django", "Python", "SQLite"])
        self.assertEqual(projects[1]["description"], ["Developed a management system"])

    def test_extract_experience_parses_inline_entry(self) -> None:
        section_lines = ["2023–2024 Software Engineer, ABC Pvt Ltd"]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["duration"], "2023–2024")
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Pvt Ltd")

    def test_extract_experience_parses_multi_line_entry(self) -> None:
        section_lines = ["Software Engineer", "ABC Pvt Ltd", "2023–2024"]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Pvt Ltd")
        self.assertEqual(experience[0]["duration"], "2023–2024")

    def test_extract_experience_stops_before_skills_section(self) -> None:
        section_lines = ["Software Engineer", "ABC Pvt Ltd", "Developed REST APIs.", "Skills", "Python", "Django"]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Pvt Ltd")
        self.assertEqual(experience[0]["description"], ["Developed REST APIs."])

    def test_extract_experience_stops_before_activities_section(self) -> None:
        section_lines = ["Software Engineer", "ABC Pvt Ltd", "Built backend systems.", "Activities", "Hackathon Winner"]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Pvt Ltd")
        self.assertEqual(experience[0]["description"], ["Built backend systems."])

    def test_extract_experience_stops_before_references_section(self) -> None:
        section_lines = ["Software Engineer", "ABC Pvt Ltd", "References", "Available on request"]

        experience = extract_experience(section_lines)

        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Software Engineer")
        self.assertEqual(experience[0]["organization"], "ABC Pvt Ltd")
        self.assertEqual(experience[0]["description"], [])

    def test_extract_experience_ignores_template_text(self) -> None:
        section_lines = ["Tip:", "Include your work experience here."]

        experience = extract_experience(section_lines)

        self.assertEqual(experience, [])

    def test_extract_experience_ignores_instructional_and_reference_lines(self) -> None:
        section_lines = [
            "Include any volunteering, community participation or leadership roles.",
            "when applying for advertised roles, use action words such as demonstrated.",
            "Available on request",
            "Example: Add your experience here.",
        ]

        experience = extract_experience(section_lines)

        self.assertEqual(experience, [])

    def test_extract_experience_ignores_contact_lines(self) -> None:
        section_lines = ["+91 9876543210", "john@email.com"]

        experience = extract_experience(section_lines)

        self.assertEqual(experience, [])

    def test_detect_sections_treats_activities_header_variants_as_activities(self) -> None:
        text = "Skills\nPython\nACTIVITIES & COMPETITIONS\nHackathon Winner\n"

        sections = detect_sections(text)

        self.assertEqual(sections["skills"], ["Python"])
        self.assertEqual(sections["activities"], ["Hackathon Winner"])

    def test_extract_skills_ignores_template_lines_and_stops_at_new_sections(self) -> None:
        section_lines = [
            "Tip: Add your skills here.",
            "For example, list tools you used.",
            "Python",
            "Django",
            "Achievements",
            "Leadership",
            "React",
        ]

        skills = extract_skills(section_lines)

        self.assertEqual(skills, ["Python", "Django"])

    def test_extract_skills_ignores_instructional_template_lines(self) -> None:
        section_lines = [
            "Include any relevant skills and achievements.",
            "when applying for advertised roles, use action words such as demonstrated.",
            "where and how you’ve used the skill through your studies.",
            "Python",
        ]

        skills = extract_skills(section_lines)

        self.assertEqual(skills, ["Python"])

    def test_extract_certifications_stops_before_activities_text(self) -> None:
        section_lines = [
            "AWS Certified Developer",
            "Google Cloud Associate",
            "ACTIVITIES & COMPETITIONS",
            "Hackathon Winner",
        ]

        certifications = extract_certifications(section_lines)

        self.assertEqual(certifications, ["AWS Certified Developer", "Google Cloud Associate"])

    def test_extract_projects_treats_description_sentences_as_descriptions(self) -> None:
        section_lines = [
            "Sample Project",
            "Used Python libraries such as NumPy, Pandas for analysis",
            "Implemented a start page using HTML",
            "Developed a dashboard using React and Django",
        ]

        projects = extract_projects(section_lines)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["title"], "Sample Project")
        self.assertEqual(
            projects[0]["description"],
            [
                "Used Python libraries such as NumPy, Pandas for analysis",
                "Implemented a start page using HTML",
                "Developed a dashboard using React and Django",
            ],
        )
        self.assertEqual(projects[0]["technologies"], [])


if __name__ == "__main__":
    unittest.main()
