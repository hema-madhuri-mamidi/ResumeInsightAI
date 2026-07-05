import re

INVALID_NAME_WORDS = {
    "RESUME",
    "CURRICULUM VITAE",
    "CURRICULUM",
    "VITAE",
    "FUNCTIONAL RESUME SAMPLE",
    "RESUME SAMPLE",
    "PROFILE",
    "OBJECTIVE",
    "SUMMARY",
    "ABOUT",
    "CONTACT",

    # Add these
    "CAREER SUMMARY",
    "CAREER OBJECTIVE",
    "PROFESSIONAL SUMMARY",
    "EXECUTIVE SUMMARY",
    "PERSONAL PROFILE",
    "ABOUT ME"
}

SECTION_HEADINGS = {

    "EDUCATION": [
        "EDUCATION",
        "ACADEMIC BACKGROUND",
        "EDUCATIONAL QUALIFICATIONS",
        "QUALIFICATIONS"
    ],

    "SKILLS": [
        "SKILLS",
        "TECHNICAL SKILLS",
        "CORE SKILLS",
        "TECHNICAL EXPERTISE",
        "SKILLS & TOOLS"
    ],

    "PROJECTS": [
        "PROJECTS",
        "ACADEMIC PROJECTS",
        "PERSONAL PROJECTS",
        "PROFESSIONAL PROJECTS",
        "RELEVANT PROJECTS",
        "KEY PROJECTS"
    ],

    "EXPERIENCE": [
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "EMPLOYMENT HISTORY",
        "INTERNSHIPS",
        "INTERNSHIP",
        "CAREER HISTORY",
        "WORK HISTORY",
        "EMPLOYMENT",
        "INDUSTRIAL EXPERIENCE"
    ],

    "CERTIFICATIONS": [
        "CERTIFICATIONS",
        "CERTIFICATES",
        "LICENSES & CERTIFICATIONS",
        "COURSES",
        "ONLINE COURSES"
    ],

    "ACTIVITIES": [
        "ACTIVITIES",
        "ACTIVITIES & COMPETITIONS",
        "ACHIEVEMENTS",
        "EXTRA CURRICULAR ACTIVITIES",
        "LEADERSHIP & ACTIVITIES",
        "EXTRACURRICULAR ACTIVITIES",
        "HOBBIES",
        "INTERESTS",
        "LEADERSHIP",
        "VOLUNTEERING"
    ],
    "REFERENCES": [
        "REFERENCES",
        "REFEREES"
    ],
}
JOB_TITLES = {
    "ENGINEER",
    "SOFTWARE ENGINEER",
    "DEVELOPER",
    "WEB DEVELOPER",
    "BACKEND DEVELOPER",
    "FRONTEND DEVELOPER",
    "FULL STACK DEVELOPER",
    "ANALYST",
    "DATA SCIENTIST",
    "DATA ANALYST",
    "AI ENGINEER",
    "ML ENGINEER",
    "CONSULTANT",
    "MANAGER",
    "INTERN",
    "STUDENT",
    "PROGRAMMER",
    "DESIGNER",
    "TESTER"
}
DEGREES = {
    "B.Tech",
    "B.E",
    "B.Sc",
    "BCA",
    "B.Com",
    "BA",
    "BBA",
    "B.Pharm",
    "LLB",

    "M.Tech",
    "M.E",
    "M.Sc",
    "MCA",
    "MBA",
    "M.Com",
    "MA",
    "M.Pharm",
    "LLM",

    "PhD",
    "Diploma",
    "Intermediate",
    "PUC",
    "HSC",
    "SSC",
    "10th",
    "12th"
}

# def contains_invalid_name_word(line):

#     return line.strip().upper() in INVALID_NAME_WORDS

def normalize_heading(text):

    return text.upper().replace(":", "").strip()

def is_heading(line):

    line = normalize_heading(line)

    for headings in SECTION_HEADINGS.values():

        if line in headings:
            return True

    return False

def clean_text(text):

    # Remove PDF artifacts like (cid:131)
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Join words split across lines
    # Example: Mat-\nplotlib -> Matplotlib
    text = re.sub(r"-\s*\n\s*", "", text)

    # Replace remaining newlines with spaces
    text = re.sub(r"\n+", "\n", text)

    # Remove multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove empty lines
    text = "\n".join(
        line.strip()
        for line in text.split("\n")
        if line.strip()
    )

    return text

# def is_entry_title(line):

#     line = line.strip()

#     if not line:
#         return False

#     if line.startswith("•"):
#         return False

#     if is_heading(line):
#         return False
    
#     if "—" in line or "|" in line: 
#         return True

#     if contains_email(line):
#         return False

#     if contains_phone(line):
#         return False

#     if contains_url(line):
#         return False

#     # Project/Experience titles usually contain these
    

#     return True

def is_entry_title(line):

    line = line.strip()

    if not line:
        return False

    if line.startswith("•"):
        return False

    if is_heading(line):
        return False

    if "—" in line or "|" in line:
        return True

    words = line.split()

    if (
        2 <= len(words) <= 8
        and line == line.title()
    ):
        return True

    return False


def contains_email(line):
    return "@" in line


def contains_phone(line):
    return bool(re.search(r"\d{10}", line))


def contains_url(line):

    social_words = {
        "LINKEDIN",
        "GITHUB",
        "PORTFOLIO",
        "HTTP",
        "HTTPS",
        "WWW",
    }

    upper = line.upper()

    return any(word in upper for word in social_words)

def is_heading(line):

    line = normalize_heading(line)

    for headings in SECTION_HEADINGS.values():

        if line in headings:
            return True

    return False

def is_job_title(line):
    return line.strip().upper() in JOB_TITLES


def contains_special_symbols(line):

    return bool(re.search(r"[|<>/=]", line))

def is_valid_word_count(line):

    words = line.split()

    return 2 <= len(words) <= 4

def is_alphabetic_name(line):

    words = line.split()

    for word in words:

        cleaned = (
            word.replace(".", "")
                .replace("-", "")
        )

        if not cleaned.isalpha():
            return False

    return True

def capitalization_score(line):

    if line.isupper():
        return 5

    if line.istitle():
        return 5

    return 0

def position_score(line_number):

    return max(0, 15 - line_number)

def find_email_line(lines):

    for i, line in enumerate(lines):

        if contains_email(line):
            return i

    return -1
def find_phone_line(lines):

    for i, line in enumerate(lines):

        if contains_phone(line):
            return i

    return -1
def phone_distance_bonus(line_number, phone_line):

    if phone_line == -1:
        return 0

    distance = abs(line_number - phone_line)

    if distance == 1:
        return 20

    elif distance == 2:
        return 10

    elif distance == 3:
        return 5

    return 0

def email_distance_bonus(line_number, email_line):

    if email_line == -1:
        return 0

    distance = abs(line_number - email_line)

    if distance == 1:
        return 20

    elif distance == 2:
        return 10

    elif distance == 3:
        return 5

    return 0

def extract_section(lines, section_name):

    section = []

    inside_section = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if not inside_section:

            found = False

            for heading in SECTION_HEADINGS[section_name]:

                if normalize_heading(line) == heading:
                    inside_section = True
                    found = True
                    break

            if not found:
                continue

            continue

        if is_heading(line):
            break

        section.append(line)

    return section

def calculate_name_score(line, line_number,email_line,phone_line):

    score = 0

    line = line.strip()

    if line.upper() in INVALID_NAME_WORDS:
        return -999

    if not line:
        return -999
    
    if any(ch.isdigit() for ch in line):
        score -= 40

    if line.isupper():
        score += 10

    # Reject invalid lines immediately
    if is_heading(line):
        return -999

    if contains_email(line):
        return -999

    if contains_phone(line):
        return -999

    if contains_url(line):
        return -999

    if is_job_title(line):
        return -999

    # Penalize special symbols
    if contains_special_symbols(line):
        score -= 20

    # Word count
    if is_valid_word_count(line):
        score += 15
    else:
        score -= 10

    # Alphabetic check
    if is_alphabetic_name(line):
        score += 20
    else:
        score -= 20

    # Capitalization
    score += capitalization_score(line)

    # Position bonus
    score += position_score(line_number)

    score += email_distance_bonus(line_number, email_line)

    score += phone_distance_bonus(line_number, phone_line)
    return score