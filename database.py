from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analysis'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    candidate_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))

    education = db.Column(JSON)
    skills = db.Column(JSON)
    projects = db.Column(JSON)
    experience = db.Column(JSON)
    certifications = db.Column(JSON)
    activities = db.Column(JSON)

    ats_score = db.Column(db.Integer)
    job_match_score = db.Column(db.Integer)
    missing_skills = db.Column(JSON)
    suggestions = db.Column(JSON)
    analysis_json = db.Column(JSON)

def save_resume_analysis(data: dict) -> None:
    """Helper function to save parsed resume data to the database in an exception-safe manner."""
    try:
        # Extract candidate contact fields
        contact = data.get("contact") or {}
        email = contact.get("email") if isinstance(contact, dict) else data.get("email")
        phone = contact.get("phone") if isinstance(contact, dict) else data.get("phone")

        # Extract score fields
        ats = data.get("ats_score") or {}
        ats_overall = ats.get("overall_score") if isinstance(ats, dict) else None

        job_match = data.get("job_match") or {}
        match_percentage = job_match.get("match_percentage") if isinstance(job_match, dict) else None
        missing = job_match.get("missing_skills") if isinstance(job_match, dict) else None

        suggs = data.get("suggestions") or {}
        suggestions_list = suggs.get("suggestions") if isinstance(suggs, dict) else None

        analysis = ResumeAnalysis(
            candidate_name=data.get("name"),
            email=email,
            phone=phone,
            education=data.get("education"),
            skills=data.get("skills"),
            projects=data.get("projects"),
            experience=data.get("experience"),
            certifications=data.get("certifications"),
            activities=data.get("activities"),
            ats_score=ats_overall,
            job_match_score=match_percentage,
            missing_skills=missing,
            suggestions=suggestions_list,
            analysis_json=data
        )
        db.session.add(analysis)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log/Print error but do not raise, ensuring database errors do not halt execution.
        print(f"Database save failed: {e}")
