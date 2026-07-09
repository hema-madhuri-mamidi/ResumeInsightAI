<!-- Resume Insight AI Parser (Version 1)

✓ Name extraction
✓ Email extraction
✓ Phone extraction
✓ Education extraction
✓ Skills extraction
✓ Certifications extraction
✓ Activities extraction
✓ Rule-based Project extraction
✓ JSON output

Current limitations:
- Experience extraction is conservative.
- Complex resume layouts may not be fully supported.
-->

# 🚀 ResumeInsightAI

> A modern Resume Analysis platform that helps job seekers evaluate their resumes through ATS analysis, job matching, skill gap identification, and personalized improvement suggestions.

---

# 🌐 Live Demo

🔗 **Application:** https://resumeinsightai.onrender.com

🔗 LinkedIn: https://www.linkedin.com/posts/hema-madhuri-mamidi_python-flask-fullstackdevelopment-ugcPost-7481005467637493760-RXI6/

💻 GitHub: https://github.com/hema-madhuri-mamidi/ResumeInsightAI
---

# 👩‍💻 Author

**Hema Madhuri Mamidi**

🎓 B.Tech – Artificial Intelligence & Data Science

🏫 Vignan's Institute of Information Technology

🔗 LinkedIn: https://www.linkedin.com/in/hema-madhuri-mamidi/

💻 GitHub: https://github.com/hema-madhuri-mamidi

---

# ✨ Features

- 📄 Upload PDF resumes
- 🔍 Automatic Resume Parsing
- 👤 Extract Candidate Information
- 🎯 ATS Resume Analysis
- 💼 Job Match Analysis
- 📚 Skill Gap Identification
- 💡 Personalized Resume Suggestions
- 📊 Interactive Dashboard
- 🌙 Dark / ☀️ Light Mode
- 📥 Download Analysis Report as PDF
- 💾 Database Storage for Resume Analysis
- 📱 Fully Responsive UI

---

# 🛠 Tech Stack

## Backend

- 🐍 Python
- 🌶 Flask
- 🗄 SQLAlchemy
- 🐘 PostgreSQL (Production)
- 🗃 SQLite (Development)

## Resume Parsing

- 📄 PDFPlumber
- 🔤 Regular Expressions (Regex)
- 🧩 Rule-Based Modular Parsing

## Frontend

- HTML5
- CSS3
- JavaScript

## Deployment

- Render
- GitHub

---

# 📂 Project Structure

```text
ResumeInsightAI/
│
├── app.py
├── database.py
├── requirements.txt
├── static/
│   ├── css/
│   └── js/
├── templates/
├── tests/
├── uploads/
└── v2/
    ├── ATS Score
    ├── Job Match
    ├── Skill Gap
    ├── Suggestions
    ├── Resume Parsers
    └── Routes

---

⚙️ How It Works

1. 📤 Upload a PDF resume.
2. 📄 Extract text from the document.
3. 🧩 Detect and parse resume sections.
4. 👤 Extract candidate information.
5. 🎯 Calculate ATS Score.
6. 💼 Compare resume with a job description.
7. 📚 Identify missing skills.
8. 💡 Generate improvement suggestions.
9. 📊 Display results on an interactive dashboard.
10. 💾 Store analysis results in the database.

---

🎯 ATS Analysis

ResumeInsightAI evaluates the following sections:

- 📞 Contact Information
- 🎓 Education
- 🛠 Skills
- 🚀 Projects
- 💼 Experience
- 📜 Certifications
- 🏆 Activities

The dashboard provides:

- ✅ Overall ATS Score
- 📈 Section-wise ATS Breakdown
- 💪 Resume Strengths
- 📝 Areas for Improvement

---

💼 Job Match Analysis

Paste any job description and ResumeInsightAI will identify:

- ✅ Matching Skills
- ❌ Missing Skills
- 📊 Job Match Percentage

This helps users understand how closely their resume aligns with a target role.

---

📚 Skill Gap Analysis

The application highlights skills missing from the resume compared with the selected job description.

Each missing skill includes:

- 🔥 Priority Level
- 📖 Learning Guidance
- 🎯 Recommended Learning Path

---

💡 Resume Suggestions

ResumeInsightAI provides actionable recommendations such as:

- Add missing profile links
- Improve project descriptions
- Strengthen technical skills
- Enhance resume completeness
- Increase ATS compatibility

---

💾 Database Integration

Every successful resume analysis is stored in the database.

Stored information includes:

- 👤 Candidate Details
- 🎓 Education
- 🛠 Skills
- 🚀 Projects
- 💼 Experience
- 📜 Certifications
- 🏆 Activities
- 🎯 ATS Score
- 💼 Job Match Score
- 📚 Missing Skills
- 💡 Suggestions
- 📊 Complete Analysis Data

Development: SQLite

Production: PostgreSQL

---

🎨 User Interface Highlights

- ✨ Modern Dashboard
- 📊 Interactive Cards
- 📈 Progress Bars
- 🌙 Dark / ☀️ Light Mode
- 📥 PDF Report Download
- 📱 Responsive Design
- 🎯 Professional Loading Experience

---

🚀 Future Enhancements

- 📄 DOCX Resume Support
- 🖼 OCR Support for Scanned Resumes
- 🧠 Semantic Skill Matching
- 📈 Advanced ATS Scoring
- 👤 User Authentication
- 📚 Resume History
- 🔍 Search & Filter
- 📊 Analytics Dashboard

---

🖥 Installation

Clone the repository:

git clone https://github.com/hema-madhuri-mamidi/ResumeInsightAI
cd ResumeInsightAI

Create a virtual environment:

python -m venv resu_env

Activate it (Windows):

resu_env\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

Open:

http://127.0.0.1:5000

---

🤝 Contributing

Contributions, suggestions, and improvements are welcome.

If you'd like to improve ResumeInsightAI, feel free to fork the repository and submit a pull request.

---

📄 License

This project is developed for educational, learning, and portfolio purposes.

---

⭐ If you found this project useful, consider giving it a Star on GitHub!