from ast import pattern

import pdfplumber
import re
import os
from pprint import pprint
# import spacy
from utils import DEGREES,extract_section,calculate_name_score, find_email_line, find_phone_line,clean_text,SECTION_HEADINGS, is_entry_title,normalize_heading,is_heading,contains_email,contains_phone,contains_url
from skills import SKILLS

# nlp = spacy.load("en_core_web_sm")


def extract_name(text):

    lines = text.split("\n")

    best_name = None
    best_score = -999
    email_line = find_email_line(lines)

    phone_line = find_phone_line(lines)

    for i, line in enumerate(lines[:12]):

        score = calculate_name_score(line, i, email_line, phone_line)

        print(f"{line} ---> {score}")

        if score > best_score:
            best_score = score
            best_name = line.strip()

    return best_name




def extract_skills(text):

    found_skills = []

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):

            found_skills.append(skill)

    return sorted(set(found_skills))

def extract_text(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
    text = clean_text(text)
    return text


def extract_email(text):
    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None



def extract_phone(text):
    pattern = r'(\+91[\s-]?\d{10}|\d{10})'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None
def extract_degree(education_section):

    

    for line in education_section:

        for degree in DEGREES:

            pattern = rf"\b{re.escape(degree)}\b"

            if re.search(pattern, line, re.IGNORECASE):
                return degree

    return None


def extract_branch(education_section):

    for line in education_section:

        if " in " in line.lower():

            branch = line.split(" in ", 1)[1]

            # Remove years like 2024-2028 or 2024 – 2028
            branch = re.sub(r'\b20\d{2}\s*[–-]\s*20\d{2}\b', '', branch)

            return branch.strip()

    return None


def extract_college(education_section):
    COLLEGE_KEYWORDS = {
    "institute",
    "university",
    "college",
    "iit",
    "nit",
    "school"
    }

    for line in education_section:

        lower = line.lower()

        if any(word in lower for word in COLLEGE_KEYWORDS):
            line = re.sub(
                r'(CGPA|GPA).*',
                '',
                line, 
                flags=re.IGNORECASE
                ).strip()
            return line

    return None
def extract_cgpa(education_section):

    pattern = r'(?:CGPA|GPA)\s*[:\-]?\s*(\d+(\.\d+)?)'

    for line in education_section:

        match = re.search(pattern, line, re.IGNORECASE)

        if match:
            return match.group(1)

    return None


def extract_graduation_year(education_section):

    years = []

    pattern = r'\b20\d{2}\b'

    for line in education_section:

        matches = re.findall(pattern, line)

        years.extend(matches)

    if years:
        return max(years)

    return None

def extract_education(text):

    lines = text.split("\n")

    education_section = extract_section(lines, "EDUCATION")
    education = {
        "degree": extract_degree(education_section),
        "branch": extract_branch(education_section),
        "college": extract_college(education_section),
        "cgpa": extract_cgpa(education_section),
        "graduation_year": extract_graduation_year(education_section)
    }
    return education

def extract_entries(text, section_name, has_technologies=False):

    lines = text.split("\n")

    section = extract_section(lines, section_name)

    if not section:
        return []

    entries = []

    i = 0

    while i < len(section):

        line = section[i].strip()

        if not line:
            i += 1
            continue

        if is_entry_title(line):

            title = line

            if "|" in title:
                title = title.split("|")[0].strip()

            if "—" in title:
                title = title.split("—")[0].strip()

            entry = {
                "title": title,
                "technologies": [],
                "description": []
            }

            # Technologies (Projects only)
            if has_technologies and i + 1 < len(section):

                tech_line = section[i + 1]

                entry["technologies"] = extract_skills(tech_line)

                i += 1

            i += 1

            while i < len(section):

                current = section[i].strip()

                if is_entry_title(current):
                    i -= 1
                    break

                if current.startswith("•"):

                    entry["description"].append(
                        current.lstrip("•").strip()
                    )

                elif entry["description"]:

                    entry["description"][-1] += " " + current

                i += 1

            entries.append(entry)

        i += 1

    return entries

# def extract_projects(text):

#     return extract_entries(
#         text,
#         "PROJECTS",
#         has_technologies=True
#     )

def is_project_title(line):

    line = line.strip()

    if not line:
        return False

    if is_heading(line):
        return False

    if contains_email(line):
        return False

    if contains_phone(line):
        return False

    if contains_url(line):
        return False

    if line.startswith("•"):
        return False

    if extract_skills(line):
        return False

    if len(line.split()) > 8:
        return False

    return True

def extract_projects(text):

    lines = text.split("\n")

    section = extract_section(lines, "PROJECTS")

    if not section:
        return []

    projects = []

    i = 0

    while i < len(section):

        line = section[i].strip()

        if not line:
            i += 1
            continue

        if not is_project_title(line):
            i += 1
            continue

        project = {
            "title": line,
            "technologies": [],
            "description": []
        }

        i += 1

        # Technology line (usually immediately after title)
        if i < len(section):

            techs = extract_skills(section[i])

            if techs:
                project["technologies"] = techs
                i += 1

        # Description
        while i < len(section):

            current = section[i].strip()

            if not current:
                i += 1
                continue

            # Stop if next project starts
            if is_project_title(current):
                break

            if current.startswith("•"):
                project["description"].append(
                    current.lstrip("•").strip()
                )

            elif project["description"]:
                project["description"][-1] += " " + current

            i += 1

        projects.append(project)

    return projects


def extract_experience(text):

    return extract_entries(
        text,
        "EXPERIENCE",
        has_technologies=False
    )
def extract_certifications(text):

    lines = text.split("\n")

    certification_section = extract_section(lines, "CERTIFICATIONS")

    certifications = []

    for line in certification_section:

        line = line.strip()

        if not line:
            continue

        if line.startswith("•") or line.startswith("-"):

            certifications.append(line.lstrip("•- ").strip())

    return certifications

def extract_activities(text):

    lines = text.split("\n")

    activity_section = extract_section(lines, "ACTIVITIES")

    activities = []
    current_activity = ""

    for line in activity_section:

        line = line.strip()

        if not line:
            continue

        if line.startswith("•") or line.startswith("-"):

            if current_activity:
                activities.append(current_activity)

            current_activity = line.lstrip("•- ").strip()

        else:
            current_activity += " " + line

    if current_activity:
        activities.append(current_activity)


    return activities


# pdf_path = "uploads/resume1.pdf"

def parse_resume(pdf_path):

    text = extract_text(pdf_path)

    data = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "education": extract_education(text),

        "projects": extract_projects(text),

        "experience": extract_experience(text),

        "certifications": extract_certifications(text),

        "activities": extract_activities(text)

    }

    return data



# text = extract_text(pdf_path)


# pdf_path = "uploads/resume1.pdf"
# resume_data = parse_resume(pdf_path)
# pprint(resume_data)
# pprint(extract_projects(text))

# print()

# pprint(extract_experience(text))


if __name__ == "__main__":
    for file in os.listdir("uploads"):

        if file.endswith(".pdf"):

            print("\n" + "=" * 80)
            print(file)
            print("=" * 80)

            pdf_path = os.path.join("uploads", file)

            data = parse_resume(pdf_path)

            pprint(data)


    


