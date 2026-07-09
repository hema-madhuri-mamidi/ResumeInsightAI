document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");
    const errorMessage = document.getElementById("error-message");
    const loading = document.getElementById("loading");
    const resultsContainer = document.getElementById("results-container");

    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const fileInput = document.getElementById("resume");
            const jobDescriptionInput = document.getElementById("job-description");
            const formData = new FormData();

            errorMessage.textContent = "";
            loading.style.display = "block";

            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                loading.style.display = "none";
                errorMessage.textContent = "Please select a PDF file.";
                return;
            }

            formData.append("resume", fileInput.files[0]);
            if (jobDescriptionInput) {
                formData.append("job_description", jobDescriptionInput.value.trim());
            }

            try {
                const response = await fetch("/api/parse", {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json().catch(() => null);

                if (!response.ok || !result || !result.success) {
                    throw new Error(result?.message || "Unable to parse the uploaded resume.");
                }

                sessionStorage.setItem("parsedResumeData", JSON.stringify(result.data));
                window.location.href = "/result";
            } catch (error) {
                loading.style.display = "none";
                errorMessage.textContent = error.message || "An unexpected error occurred.";
            }
        });
    }

    if (resultsContainer) {
        const storedData = sessionStorage.getItem("parsedResumeData");
        if (!storedData) {
            resultsContainer.innerHTML = '<div class="result-card"><p>No resume data found.</p></div>';
            return;
        }

        let data;
        try {
            data = JSON.parse(storedData);
        } catch (error) {
            resultsContainer.innerHTML = '<div class="result-card"><p>Unable to load resume data.</p></div>';
            return;
        }

        const sections = [
            { key: "name", title: "Name" },
            { key: "contact", title: "Contact" },
            { key: "education", title: "Education" },
            { key: "experience", title: "Experience" },
            { key: "projects", title: "Projects" },
            { key: "skills", title: "Skills" },
            { key: "certifications", title: "Certifications" },
            { key: "activities", title: "Activities" },
        ];

        const atsSection = renderAtsScore(data.ats_score);
        const jobMatchSection = renderJobMatch(data.job_match);
        const skillGapSection = renderSkillGap(data.skill_gap);
        const cards = sections.map(({ key, title }) => {
            const value = data[key];
            const extraClass = key === "projects"
                ? " result-card-projects"
                : key === "contact"
                    ? " result-card-contact"
                    : key === "education"
                        ? " result-card-education"
                        : key === "name"
                            ? " result-card-name"
                            : "";

            return `
                <section class="result-card${extraClass}">
                    <h2>${title}</h2>
                    ${renderSectionValue(value, key)}
                </section>
            `;
        }).join("");

        resultsContainer.innerHTML = `${jobMatchSection}${skillGapSection}${atsSection}${cards}`;
    }
});

function renderSkillGap(skillGap) {
    if (!skillGap || typeof skillGap !== "object") {
        return "";
    }

    const priority = skillGap.priority || "Medium";
    const priorityClass = `priority-${String(priority).toLowerCase()}`;
    const missingSkills = Array.isArray(skillGap.missing_skills) ? skillGap.missing_skills : [];
    const recommendedSkills = Array.isArray(skillGap.recommended_skills_to_learn)
        ? skillGap.recommended_skills_to_learn
        : [];
    const guideItems = Array.isArray(skillGap.skill_guide)
        ? skillGap.skill_guide
        : Array.isArray(skillGap.skill_guides)
            ? skillGap.skill_guides
            : [];

    const missingChips = missingSkills.length > 0
        ? `<div class="skills-chip-list">${missingSkills.map((skill) => `<span class="skill-gap-chip">${formatValue(skill)}</span>`).join("")}</div>`
        : `<p class="empty-state">No missing skills detected.</p>`;

    const recommendedChips = recommendedSkills.length > 0
        ? `<div class="skills-chip-list">${recommendedSkills.map((skill) => `<span class="skill-gap-chip">${formatValue(skill)}</span>`).join("")}</div>`
        : `<p class="empty-state">No recommended skills available.</p>`;

    const guideCards = guideItems.length > 0
        ? `<div class="skill-guide-grid">${guideItems.map((guide) => {
            const name = guide?.skill || guide?.name || "Skill";
            const reason = guide?.reason || "Recommended technology for this job role.";
            const resources = guide?.learning_path || guide?.resources || guide?.learning_resources || "No learning resources listed.";
            const estimatedTime = guide?.estimated_time || guide?.estimatedTime || "Not specified";
            const difficulty = guide?.difficulty || (String(guide?.priority || priority).toLowerCase() === "high" ? "Intermediate" : "Beginner");

            return `
                <article class="skill-guide-card">
                    <h3>${formatValue(name)}</h3>
                    <div class="skill-guide-section">
                        <span class="skill-guide-label">Why Learn</span>
                        <p>${formatValue(reason)}</p>
                    </div>
                    <div class="skill-guide-section">
                        <span class="skill-guide-label">Resources</span>
                        <p>${formatValue(resources)}</p>
                    </div>
                    <div class="skill-guide-section">
                        <span class="skill-guide-label">Estimated Time</span>
                        <p>${formatValue(estimatedTime)}</p>
                    </div>
                    <div class="skill-guide-section">
                        <span class="skill-guide-label">Difficulty</span>
                        <p>${formatValue(difficulty)}</p>
                    </div>
                </article>
            `;
        }).join("")}</div>`
        : `<p class="empty-state">No learning guide available.</p>`;

    return `
        <section class="result-card result-card-skill-gap">
            <h2>Skill Gap Analysis</h2>
            <div class="skill-gap-summary">
                <span class="priority-badge ${priorityClass}">${formatValue(priority)} Priority</span>
            </div>
            <div class="skill-gap-insights">
                <div>
                    <h3>Missing Skills</h3>
                    ${missingChips}
                </div>
                <div>
                    <h3>Recommended Skills To Learn</h3>
                    ${recommendedChips}
                </div>
            </div>
            <div>
                <h3>Learning Guide</h3>
                ${guideCards}
            </div>
        </section>
    `;
}

function renderAtsScore(atsScore) {
    if (!atsScore || typeof atsScore !== "object") {
        return "";
    }

    const sectionItems = Object.entries(atsScore.section_scores || {}).map(([key, value]) => `
        <li class="ats-section-item">
            <span class="ats-section-label">${formatValue(key)}</span>
            <span class="ats-section-value">${value}/${getWeight(key)}</span>
        </li>
    `).join("");

    const strengths = (atsScore.strengths || []).map((item) => `<li>${formatValue(item)}</li>`).join("");
    const improvements = (atsScore.improvements || []).map((item) => `<li>${formatValue(item)}</li>`).join("");

    return `
        <section class="result-card result-card-ats">
            <h2>ATS Score</h2>
            <div class="ats-score-summary">
                <div class="ats-score-circle">${atsScore.overall_score ?? 0}</div>
                <div class="ats-score-meta">
                    <p class="ats-score-label">Overall ATS Readiness</p>
                    <p class="ats-score-text">A simple rule-based score based on section completeness.</p>
                </div>
            </div>
            <ul class="ats-section-list">${sectionItems}</ul>
            <div class="ats-insights">
                <div>
                    <h3>Strengths</h3>
                    <ul class="ats-insight-list">${strengths || '<li>No strengths detected.</li>'}</ul>
                </div>
                <div>
                    <h3>Improvements</h3>
                    <ul class="ats-insight-list">${improvements || '<li>No improvements detected.</li>'}</ul>
                </div>
            </div>
        </section>
    `;
}

function renderJobMatch(jobMatch) {
    if (!jobMatch || typeof jobMatch !== "object") {
        return "";
    }

    const matchPercentage = jobMatch.match_percentage ?? 0;
    const matchedSkills = Array.isArray(jobMatch.matched_skills) ? jobMatch.matched_skills : [];
    const missingSkills = Array.isArray(jobMatch.missing_skills) ? jobMatch.missing_skills : [];
    const summaryText = matchedSkills.length || missingSkills.length
        ? "Keyword overlap between your resume and the role description."
        : "Add a job description to compare your resume against this role.";

    const matchedList = matchedSkills.length > 0
        ? `<ul class="job-match-list">${matchedSkills.map((skill) => `<li>${formatValue(skill)}</li>`).join("")}</ul>`
        : `<p class="empty-state">No matched keywords found yet.</p>`;

    const missingList = missingSkills.length > 0
        ? `<ul class="job-match-list">${missingSkills.map((skill) => `<li>${formatValue(skill)}</li>`).join("")}</ul>`
        : `<p class="empty-state">No missing keywords detected.</p>`;

    return `
        <section class="result-card result-card-job-match">
            <h2>Job Match</h2>
            <div class="job-match-summary">
                <div class="job-match-score">${matchPercentage}%</div>
                <div class="job-match-meta">
                    <p class="job-match-label">Role Alignment</p>
                    <p class="job-match-text">${summaryText}</p>
                </div>
            </div>
            <div class="job-match-insights">
                <div>
                    <h3>Matched Keywords</h3>
                    ${matchedList}
                </div>
                <div>
                    <h3>Missing Keywords</h3>
                    ${missingList}
                </div>
            </div>
        </section>
    `;
}

function getWeight(key) {
    const weights = {
        contact: 15,
        education: 15,
        skills: 20,
        projects: 25,
        experience: 15,
        certifications: 10,
    };

    return weights[key] || 0;
}

function renderSectionValue(value, key) {
    if (key === "name") {
        return renderName(value);
    }

    if (key === "projects") {
        return renderProjects(value);
    }

    if (key === "contact") {
        return renderContact(value);
    }

    if (key === "skills") {
        return renderSkills(value);
    }

    if (value === null || value === undefined || value === "") {
        return `<p class="empty-state">${getEmptyStateMessage(key)}</p>`;
    }

    if (Array.isArray(value)) {
        if (value.length === 0) {
            return `<p class="empty-state">${getEmptyStateMessage(key)}</p>`;
        }
        return `<ul class="section-list">${value.map((item) => `<li class="section-list-item">${renderListItem(item)}</li>`).join("")}</ul>`;
    }

    if (typeof value === "object") {
        if (Object.keys(value).length === 0) {
            return `<p class="empty-state">${getEmptyStateMessage(key)}</p>`;
        }
        return renderObjectDetails(value);
    }

    return `<p>${formatValue(value)}</p>`;
}

function renderName(value) {
    if (value === null || value === undefined || value === "") {
        return `<p class="empty-state">${getEmptyStateMessage("name")}</p>`;
    }

    return `<div class="hero-name">${formatValue(value)}</div>`;
}

function renderListItem(item) {
    if (item && typeof item === "object" && !Array.isArray(item)) {
        return renderObjectDetails(item);
    }

    return `<span class="list-text">${formatValue(item)}</span>`;
}

function renderObjectDetails(value) {
    return `
        <div class="detail-grid">
            ${Object.entries(value).map(([entryKey, item]) => `
                <div class="detail-item">
                    <div class="detail-label">${formatValue(entryKey)}</div>
                    <div class="detail-value">${formatValue(item)}</div>
                </div>
            `).join("")}
        </div>
    `;
}

function renderProjects(value) {
    if (value === null || value === undefined || value === "") {
        return `<p class="empty-state">${getEmptyStateMessage("projects")}</p>`;
    }

    if (!Array.isArray(value)) {
        return `<p class="empty-state">${getEmptyStateMessage("projects")}</p>`;
    }

    if (value.length === 0) {
        return `<p class="empty-state">${getEmptyStateMessage("projects")}</p>`;
    }

    return `<div class="projects-list">${value.map((project) => renderProjectCard(project)).join("")}</div>`;
}

function renderProjectCard(project) {
    const title = project?.title || project?.name || project?.project || "Untitled project";
    const technologies = Array.isArray(project?.technologies) ? project.technologies : [];
    const description = Array.isArray(project?.description) ? project.description : [];

    const technologyChips = technologies.length > 0
        ? `<div class="project-tech-list">${technologies.map((tech) => `<span class="project-tech-chip">${formatValue(tech)}</span>`).join("")}</div>`
        : `<p class="empty-state">No technologies listed.</p>`;

    const descriptionBullets = description.length > 0
        ? `<ul class="project-bullets">${description.map((item) => `<li>${formatValue(item)}</li>`).join("")}</ul>`
        : `<p class="empty-state">No description provided.</p>`;

    return `
        <article class="project-card">
            <h3>${formatValue(title)}</h3>
            ${technologyChips}
            ${descriptionBullets}
        </article>
    `;
}

function renderContact(value) {
    if (value === null || value === undefined || value === "") {
        return `<p class="empty-state">${getEmptyStateMessage("contact")}</p>`;
    }

    if (typeof value !== "object" || Array.isArray(value)) {
        return `<p class="empty-state">${getEmptyStateMessage("contact")}</p>`;
    }

    const contactFields = [
        { key: "email", label: "Email" },
        { key: "phone", label: "Phone" },
        { key: "github", label: "GitHub" },
        { key: "linkedin", label: "LinkedIn" },
        { key: "portfolio", label: "Portfolio" },
    ];

    return `
        <ul class="contact-list">
            ${contactFields.map(({ key, label }) => renderContactItem(label, value[key])).join("")}
        </ul>
    `;
}

function renderContactItem(label, rawValue) {
    const value = rawValue === null || rawValue === undefined || rawValue === "" ? "" : String(rawValue).trim();

    if (!value) {
        return `
            <li class="contact-item">
                <div class="contact-meta">
                    <span class="contact-icon" aria-hidden="true">${getContactIcon(label)}</span>
                    <div class="contact-copy">
                        <span class="contact-label">${label}</span>
                        <span class="contact-value empty-state">${getEmptyStateMessage("contact")}</span>
                    </div>
                </div>
            </li>
        `;
    }

    const href = getContactHref(label, value);
    const content = href
        ? `<a href="${href}" target="_blank" rel="noopener noreferrer">${value}</a>`
        : `<span>${value}</span>`;

    return `
        <li class="contact-item">
            <div class="contact-meta">
                <span class="contact-icon" aria-hidden="true">${getContactIcon(label)}</span>
                <div class="contact-copy">
                    <span class="contact-label">${label}</span>
                    <span class="contact-value">${content}</span>
                </div>
            </div>
        </li>
    `;
}

function getContactIcon(label) {
    const icons = {
        Email: "✉️",
        Phone: "📞",
        GitHub: "💻",
        LinkedIn: "🔗",
        Portfolio: "🌐",
    };

    return icons[label] || "•";
}

function getContactHref(label, value) {
    const normalized = String(value).trim();
    if (!normalized) {
        return "";
    }

    if (label === "Email") {
        return normalized.startsWith("mailto:") ? normalized : `mailto:${normalized}`;
    }

    if (label === "Phone") {
        const digits = normalized.replace(/[^\d+]/g, "");
        return digits ? `tel:${digits}` : "";
    }

    if (label === "GitHub" || label === "LinkedIn" || label === "Portfolio") {
        return normalized.startsWith("http://") || normalized.startsWith("https://")
            ? normalized
            : `https://${normalized}`;
    }

    return "";
}

function renderSkills(value) {
    if (value === null || value === undefined || value === "") {
        return `<p class="empty-state">${getEmptyStateMessage("skills")}</p>`;
    }

    if (!Array.isArray(value)) {
        return `<p class="empty-state">${getEmptyStateMessage("skills")}</p>`;
    }

    if (value.length === 0) {
        return `<p class="empty-state">${getEmptyStateMessage("skills")}</p>`;
    }

    return `
        <div class="skills-chip-list">
            ${value.map((skill) => `<span class="skill-chip">${formatValue(skill)}</span>`).join("")}
        </div>
    `;
}

function getEmptyStateMessage(key) {
    const messages = {
        projects: "No projects found.",
        experience: "No experience available.",
        certifications: "No certifications found.",
        skills: "No skills found.",
        contact: "No contact information found.",
        education: "No education details found.",
        activities: "No activities found.",
        name: "No name found.",
    };

    return messages[key] || "No information found.";
}

function formatValue(value) {
    if (value === null || value === undefined || value === "") {
        return "Not available";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}
