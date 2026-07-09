let currentReportData = null;

function sanitizeFileName(value) {
    return String(value || "ResumeInsightAI_Report")
        .replace(/[^a-z0-9]+/gi, "_")
        .replace(/^_+|_+$/g, "")
        .slice(0, 40) || "ResumeInsightAI_Report";
}

function getDisplayValue(value) {
    if (value === null || value === undefined || value === "") {
        return "Not Available";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}

function getCandidateName(data) {
    if (data?.name) {
        return data.name;
    }

    if (data?.contact?.name) {
        return data.contact.name;
    }

    if (data?.contact?.full_name) {
        return data.contact.full_name;
    }

    return "Not Available";
}

function getCandidateEmail(data) {
    return data?.contact?.email || "Not Available";
}

function getCandidatePhone(data) {
    return data?.contact?.phone || "Not Available";
}

function getCandidateLinkedIn(data) {
    return data?.contact?.linkedin || data?.contact?.linkedIn || data?.contact?.linked_in || "Not Available";
}

function getCandidateGitHub(data) {
    return data?.contact?.github || data?.contact?.gitHub || data?.contact?.git_hub || "Not Available";
}

function getCandidatePortfolio(data) {
    return data?.contact?.portfolio || "Not Available";
}

function getMissingSkillCount(data) {
    const jobMissing = Array.isArray(data?.job_match?.missing_skills) ? data.job_match.missing_skills : [];
    const skillGapMissing = Array.isArray(data?.skill_gap?.missing_skills) ? data.skill_gap.missing_skills : [];
    const combined = [...jobMissing, ...skillGapMissing];
    const unique = [...new Set(combined.map((skill) => String(skill).trim().toLowerCase()).filter(Boolean))];
    return unique.length;
}

function getUniqueSkills(values) {
    if (!Array.isArray(values)) {
        return [];
    }

    return [...new Set(values.map((skill) => String(skill).trim()).filter(Boolean))];
}

function getSkillGuideEntries(data) {
    const guideItems = Array.isArray(data?.skill_gap?.skill_guide)
        ? data.skill_gap.skill_guide
        : Array.isArray(data?.skill_gap?.skill_guides)
            ? data.skill_gap.skill_guides
            : [];
    const jobMissing = Array.isArray(data?.job_match?.missing_skills) ? data.job_match.missing_skills : [];
    const skillGapMissing = Array.isArray(data?.skill_gap?.missing_skills) ? data.skill_gap.missing_skills : [];
    const missingSkills = getUniqueSkills([...jobMissing, ...skillGapMissing]);

    return missingSkills.map((skill, index) => {
        const guide = guideItems.find((item) => {
            const itemName = String(item?.skill || item?.name || "").trim().toLowerCase();
            return itemName && itemName.includes(skill.toLowerCase());
        }) || guideItems[index] || {};

        return {
            skill,
            priority: guide?.priority || data?.skill_gap?.priority || "Medium",
            description: guide?.reason || guide?.description || `Develop proficiency in ${skill} to strengthen alignment with the target role.`,
            learningPath: guide?.learning_path || guide?.resources || guide?.learning_resources || "Follow structured tutorials, hands-on practice, and project-based learning to build practical knowledge.",
            estimatedTime: guide?.estimated_time || guide?.estimatedTime || "2-4 weeks",
        };
    });
}

function getSectionValueItems(data, key) {
    const value = data?.[key];
    if (key === "education") {
        if (Array.isArray(value)) {
            return value.map((item) => {
                if (typeof item === "object" && item !== null) {
                    const degree = item.degree || item.program || item.title || item.name || "Education";
                    const institution = item.institution || item.school || item.university || "";
                    const year = item.year || item.graduation_year || item.period || "";
                    return [degree, institution, year].filter(Boolean).join(" • ");
                }
                return String(item);
            });
        }
        return value ? [String(value)] : [];
    }

    if (key === "experience") {
        if (Array.isArray(value)) {
            return value.map((item) => {
                if (typeof item === "object" && item !== null) {
                    const title = item.title || item.role || item.designation || "Experience";
                    const company = item.company || item.organization || item.employer || "";
                    const period = item.period || item.duration || item.years || "";
                    return [title, company, period].filter(Boolean).join(" • ");
                }
                return String(item);
            });
        }
        return value ? [String(value)] : [];
    }

    if (key === "projects") {
        if (Array.isArray(value)) {
            return value.map((item) => {
                if (typeof item === "object" && item !== null) {
                    const title = item.title || item.name || item.project || "Project";
                    const description = Array.isArray(item.description) ? item.description.join(" ") : item.description || "";
                    return [title, description].filter(Boolean).join(" • ");
                }
                return String(item);
            });
        }
        return value ? [String(value)] : [];
    }

    if (key === "skills") {
        return Array.isArray(value) ? value.map((skill) => String(skill)) : value ? [String(value)] : [];
    }

    if (key === "certifications") {
        return Array.isArray(value) ? value.map((item) => String(item)) : value ? [String(value)] : [];
    }

    if (key === "activities") {
        return Array.isArray(value) ? value.map((item) => String(item)) : value ? [String(value)] : [];
    }

    return value ? [String(value)] : [];
}

function getJsPdfConstructor() {
    const candidates = [
        window?.jspdf?.jsPDF,
        window?.jspdf?.default?.jsPDF,
        window?.jspdf?.default,
        window?.jsPDF,
        window?.jspPDF,
    ];

    return candidates.find((candidate) => typeof candidate === "function") || null;
}

function getStoredReportData() {
    if (currentReportData) {
        return currentReportData;
    }

    const storedData = sessionStorage.getItem("parsedResumeData");
    if (!storedData) {
        return null;
    }

    try {
        return JSON.parse(storedData);
    } catch (error) {
        console.error("Unable to parse stored resume data for report export.", error);
        return null;
    }
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function buildPrintableReportHtml(data, fallbackReason) {
    const candidateName = getCandidateName(data);
    const email = getCandidateEmail(data);
    const phone = getCandidatePhone(data);
    const atsScore = getDisplayValue(data?.ats_score?.overall_score ?? "Not Available");
    const jobMatch = getDisplayValue(data?.job_match?.match_percentage ?? "Not Available");
    const matchedSkills = getUniqueSkills(Array.isArray(data?.job_match?.matched_skills) ? data.job_match.matched_skills : []);
    const missingSkills = getUniqueSkills(Array.isArray(data?.job_match?.missing_skills) ? data.job_match.missing_skills : []);
    const suggestions = Array.isArray(data?.suggestions?.suggestions) ? data.suggestions.suggestions : [];
    const skillGapEntries = getSkillGuideEntries(data);
    const sections = [
        { key: "education", title: "Education" },
        { key: "experience", title: "Experience" },
        { key: "projects", title: "Projects" },
        { key: "skills", title: "Skills" },
        { key: "certifications", title: "Certifications" },
        { key: "activities", title: "Activities" },
    ];

    const skillRows = skillGapEntries.length > 0
        ? skillGapEntries.map((entry) => `
            <li><strong>${escapeHtml(entry.skill)}</strong> — ${escapeHtml(entry.priority)}<br>${escapeHtml(entry.description)}</li>`).join("")
        : "<li>No skill gap guidance available.</li>";

    const suggestionRows = suggestions.length > 0
        ? suggestions.map((suggestion) => {
            if (typeof suggestion === "object" && suggestion !== null) {
                return `<li>${escapeHtml(suggestion.title || "Suggestion")}${suggestion.reason ? ` — ${escapeHtml(suggestion.reason)}` : ""}</li>`;
            }
            return `<li>${escapeHtml(String(suggestion))}</li>`;
        }).join("")
        : "<li>No suggestions available.</li>";

    const sectionRows = sections.map(({ key, title }) => {
        const items = getSectionValueItems(data, key);
        if (!items.length) {
            return "";
        }
        return `
            <section>
                <h3>${escapeHtml(title)}</h3>
                <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            </section>`;
    }).join("");

    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ResumeInsightAI Report</title>
<style>
  body { font-family: Arial, sans-serif; color: #0f172a; margin: 24px; line-height: 1.5; }
  h1, h2, h3 { color: #0f172a; }
  .meta { color: #475569; margin-bottom: 12px; }
  .card { border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
  ul { padding-left: 18px; }
</style>
</head>
<body>
  <h1>ResumeInsightAI Analysis Report</h1>
  <p class="meta">Generated from the current resume analysis results.</p>
  ${fallbackReason ? `<p class="meta">Note: ${escapeHtml(fallbackReason)}</p>` : ""}
  <div class="card">
    <h2>Candidate</h2>
    <p><strong>Name:</strong> ${escapeHtml(candidateName)}</p>
    <p><strong>Email:</strong> ${escapeHtml(email)}</p>
    <p><strong>Phone:</strong> ${escapeHtml(phone)}</p>
  </div>
  <div class="card">
    <h2>Summary</h2>
    <p><strong>ATS Score:</strong> ${escapeHtml(atsScore)}</p>
    <p><strong>Job Match:</strong> ${escapeHtml(jobMatch)}</p>
    <p><strong>Matched Skills:</strong> ${escapeHtml(matchedSkills.join(", ") || "None")}</p>
    <p><strong>Missing Skills:</strong> ${escapeHtml(missingSkills.join(", ") || "None")}</p>
  </div>
  <div class="card">
    <h2>Skill Gap Guidance</h2>
    <ul>${skillRows}</ul>
  </div>
  <div class="card">
    <h2>Suggestions</h2>
    <ul>${suggestionRows}</ul>
  </div>
  <div class="card">
    <h2>Resume Sections</h2>
    ${sectionRows}
  </div>
</body>
</html>`;
}

function openPrintableReport(data, fallbackReason) {
    const printWindow = window.open("", "_blank", "width=900,height=800");
    if (!printWindow) {
        window.alert("Please allow popups for this site so the report preview can open.");
        return;
    }

    printWindow.document.open();
    printWindow.document.write(buildPrintableReportHtml(data, fallbackReason));
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        try {
            printWindow.print();
        } catch (error) {
            console.error("Unable to launch print preview for report.", error);
        }
    }, 250);
}

function buildAnalysisReportPdf(data, jsPdfConstructor = getJsPdfConstructor()) {
    if (typeof jsPdfConstructor !== "function") {
        throw new Error("jsPDF library is unavailable.");
    }

    const doc = new jsPdfConstructor({ orientation: "portrait", unit: "pt", format: "a4" });
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 40;
    const contentWidth = pageWidth - margin * 2;
    let y = 40;
    let currentPage = 1;

    const setDocTextColor = (color) => {
        if (Array.isArray(color)) {
            if (color.length >= 4) {
                doc.setTextColor(color[0], color[1], color[2], color[3]);
            } else {
                doc.setTextColor(color[0], color[1], color[2]);
            }
            return;
        }

        doc.setTextColor(color);
    };

    const addFooter = () => {
        const footerText = "Generated by ResumeInsightAI • Version 1.0 • © 2026 ResumeInsightAI";
        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        setDocTextColor([100, 116, 139]);
        doc.text(footerText, margin, pageHeight - 24);
        doc.text(`Page ${currentPage}`, pageWidth - margin - 40, pageHeight - 24);
    };

    const ensureSpace = (requiredHeight) => {
        if (y + requiredHeight > pageHeight - 60) {
            addFooter();
            doc.addPage();
            currentPage += 1;
            y = 40;
        }
    };

    const addDivider = () => {
        doc.setDrawColor(226, 232, 240);
        doc.line(margin, y, pageWidth - margin, y);
        y += 10;
    };

    const addHeading = (title, subtitle, size = 18) => {
        ensureSpace(36);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(size);
        setDocTextColor([15, 23, 42]);
        doc.text(title, margin, y);
        y += 18;
        if (subtitle) {
            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);
            setDocTextColor([100, 116, 139]);
            const lines = doc.splitTextToSize(subtitle, contentWidth);
            doc.text(lines, margin, y);
            y += lines.length * 12 + 8;
        }
    };

    const addSectionTitle = (title, subtitle) => {
        ensureSpace(30);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(13);
        setDocTextColor([37, 99, 235]);
        doc.text(title, margin, y);
        y += 14;
        doc.setFont("helvetica", "normal");
        doc.setFontSize(9.5);
        setDocTextColor([100, 116, 139]);
        if (subtitle) {
            const lines = doc.splitTextToSize(subtitle, contentWidth);
            doc.text(lines, margin, y);
            y += lines.length * 11 + 6;
        }
    };

    const addParagraph = (text, options = {}) => {
        const { size = 10, color = [51, 65, 85], indent = 0, lineHeight = 12 } = options;
        ensureSpace(24);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(size);
        setDocTextColor(color);
        const lines = doc.splitTextToSize(String(text || "Not Available"), contentWidth - indent);
        doc.text(lines, margin + indent, y);
        y += lines.length * lineHeight + 4;
    };

    const addBullet = (text, options = {}) => {
        const { color = [51, 65, 85], bulletColor = [37, 99, 235], indent = 8 } = options;
        ensureSpace(18);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        setDocTextColor(color);
        setDocTextColor(bulletColor);
        doc.text("•", margin + indent, y);
        setDocTextColor(color);
        const lines = doc.splitTextToSize(String(text || "Not Available"), contentWidth - indent - 12);
        doc.text(lines, margin + indent + 8, y);
        y += lines.length * 12 + 2;
    };

    const addProgressBar = (label, percent, color = [37, 99, 235]) => {
        ensureSpace(20);
        const barHeight = 8;
        const barWidth = 190;
        const fillWidth = Math.max(0, Math.min(100, Number(percent) || 0)) / 100 * barWidth;
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        setDocTextColor([51, 65, 85]);
        doc.text(label, margin, y);
        doc.setDrawColor(226, 232, 240);
        doc.rect(margin + 120, y - 6, barWidth, barHeight, "S");
        doc.setFillColor(...color);
        doc.rect(margin + 120, y - 6, fillWidth, barHeight, "F");
        doc.setFontSize(10);
        setDocTextColor([15, 23, 42]);
        doc.text(`${Math.round(Number(percent) || 0)}%`, margin + 120 + barWidth + 10, y);
        y += 16;
    };

    const addSimpleTable = (rows) => {
        ensureSpace(40);
        const rowHeight = 22;
        doc.setFillColor(248, 250, 252);
        doc.rect(margin, y, contentWidth, rowHeight * rows.length, "F");
        rows.forEach((row, index) => {
            const rowY = y + index * rowHeight;
            doc.setDrawColor(226, 232, 240);
            doc.line(margin, rowY + rowHeight, pageWidth - margin, rowY + rowHeight);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(10);
            setDocTextColor([51, 65, 85]);
            doc.text(row.label, margin + 12, rowY + 14);
            doc.setFont("helvetica", "normal");
            setDocTextColor([15, 23, 42]);
            doc.text(row.value, pageWidth - margin - 140, rowY + 14);
        });
        y += rowHeight * rows.length + 12;
    };

    addHeading("ResumeInsightAI", "Smart Resume Analysis, ATS Evaluation, Job Matching & Skill Gap Insights");
    addDivider();

    addSectionTitle("Document Information", "Professional analysis report generated from the current dashboard results.");
    addParagraph(`Resume File: ${data?.resume_file || "Uploaded Resume"}`);
    addParagraph(`Generated On: ${new Date().toLocaleDateString()}`);
    addParagraph(`Generated At: ${new Date().toLocaleTimeString()}`);
    addDivider();

    addSectionTitle("Candidate Information", "Extracted contact details from the available resume data.");
    addBullet(`Name: ${getDisplayValue(getCandidateName(data))}`);
    addBullet(`Email: ${getDisplayValue(getCandidateEmail(data))}`);
    addBullet(`Phone: ${getDisplayValue(getCandidatePhone(data))}`);
    addBullet(`LinkedIn: ${getDisplayValue(getCandidateLinkedIn(data))}`);
    addBullet(`GitHub: ${getDisplayValue(getCandidateGitHub(data))}`);
    addBullet(`Portfolio: ${getDisplayValue(getCandidatePortfolio(data))}`);
    addDivider();

    addSectionTitle("Dashboard Summary", "A concise snapshot of the current analysis results.");
    addSimpleTable([
        { label: "ATS Score", value: getDisplayValue(data?.ats_score?.overall_score ?? "Not Available") },
        { label: "Job Match %", value: getDisplayValue(data?.job_match?.match_percentage ?? "Not Available") },
        { label: "Skills Found", value: getDisplayValue(Array.isArray(data?.skills) ? data.skills.length : 0) },
        { label: "Missing Skills Count", value: getDisplayValue(getMissingSkillCount(data)) },
    ]);
    addDivider();

    addSectionTitle("ATS Breakdown", "Section completeness across the main ATS dimensions.");
    const sectionScores = data?.ats_score?.section_scores || {};
    const breakdownSections = [
        { key: "education", label: "Education", value: sectionScores.education },
        { key: "projects", label: "Projects", value: sectionScores.projects },
        { key: "skills", label: "Skills", value: sectionScores.skills },
        { key: "experience", label: "Experience", value: sectionScores.experience },
        { key: "certifications", label: "Certifications", value: sectionScores.certifications },
        { key: "activities", label: "Activities", value: sectionScores.activities },
    ];
    breakdownSections.forEach((section) => {
        const percent = Number(section.value);
        addProgressBar(section.label, Number.isFinite(percent) ? percent : 0, [37, 99, 235]);
    });
    addDivider();

    addSectionTitle("Job Match Analysis", "Matched and missing competencies compared against the target role.");
    const matchedSkills = getUniqueSkills(Array.isArray(data?.job_match?.matched_skills) ? data.job_match.matched_skills : []);
    const missingSkills = getUniqueSkills(Array.isArray(data?.job_match?.missing_skills) ? data.job_match.missing_skills : []);
    addParagraph("Matched Skills", { size: 11, color: [22, 101, 52] });
    matchedSkills.length > 0
        ? matchedSkills.forEach((skill) => addBullet(skill, { bulletColor: [22, 101, 52] }))
        : addBullet("No matched skills identified.", { bulletColor: [22, 101, 52] });
    addParagraph("Missing Skills", { size: 11, color: [185, 28, 28] });
    missingSkills.length > 0
        ? missingSkills.forEach((skill) => addBullet(skill, { bulletColor: [185, 28, 28] }))
        : addBullet("No missing skills identified.", { bulletColor: [185, 28, 28] });
    addDivider();

    addSectionTitle("Skill Gap Analysis", "Learning guidance for the missing skills identified in the analysis.");
    const skillGuides = getSkillGuideEntries(data);
    if (skillGuides.length > 0) {
        skillGuides.forEach((guide) => {
            addParagraph(`Skill Name: ${guide.skill}`, { size: 11, color: [15, 23, 42] });
            addBullet(`Priority: ${guide.priority}`);
            addBullet(`Description: ${guide.description}`);
            addBullet(`Learning Roadmap: ${guide.learningPath}`);
            addBullet(`Estimated Learning Time: ${guide.estimatedTime}`);
            addDivider();
        });
    } else {
        addParagraph("No missing skill guides available.");
    }

    addSectionTitle("Resume Sections", "The extracted sections from the parsed resume, formatted for review.");
    ["education", "experience", "projects", "skills", "certifications", "activities"].forEach((sectionKey) => {
        const items = getSectionValueItems(data, sectionKey);
        if (!items.length) {
            return;
        }
        addParagraph(sectionKey.charAt(0).toUpperCase() + sectionKey.slice(1), { size: 11, color: [15, 23, 42] });
        items.forEach((item) => addBullet(item));
    });
    addDivider();

    addSectionTitle("Suggestions", "Actionable improvement recommendations based on the analysis.");
    const suggestions = Array.isArray(data?.suggestions?.suggestions) ? data.suggestions.suggestions : [];
    if (suggestions.length > 0) {
        suggestions.forEach((suggestion) => {
            if (typeof suggestion === "object" && suggestion !== null) {
                addBullet(`${suggestion.title || "Suggestion"}${suggestion.reason ? ` — ${suggestion.reason}` : ""}`);
            } else {
                addBullet(String(suggestion));
            }
        });
    } else {
        addParagraph("No suggestions available.");
    }

    addFooter();
    const candidateName = getCandidateName(data);
    const fileName = candidateName === "Not Available"
        ? "ResumeInsightAI_Report.pdf"
        : `ResumeInsightAI_Report_${sanitizeFileName(candidateName)}.pdf`;
    doc.save(fileName);
}

function exportReportToPdf() {
    const data = getStoredReportData();
    if (!data) {
        window.alert("No analysis data is available to export yet. Please return to the results page and try again.");
        return;
    }

    const jsPdfConstructor = getJsPdfConstructor();
    if (!jsPdfConstructor) {
        openPrintableReport(data, "The PDF library could not be loaded in this browser session, so a printable preview is opening instead.");
        return;
    }

    try {
        buildAnalysisReportPdf(data, jsPdfConstructor);
    } catch (error) {
        console.error("The report could not be generated automatically.", error);
        openPrintableReport(data, "The PDF export failed, so a printable preview is opening instead.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");
    const errorMessage = document.getElementById("error-message");
    const loading = document.getElementById("loading");
    const resultsContainer = document.getElementById("results-container");
    const fileDropzone = document.querySelector(".file-dropzone");
    const resumeInput = document.getElementById("resume");

    const showLoadingOverlay = () => {
        if (loading) {
            loading.classList.add("is-visible");
            loading.setAttribute("aria-hidden", "false");
            const items = loading.querySelectorAll(".loading-item");
            items.forEach((item, index) => {
                setTimeout(() => item.classList.add("is-active"), index * 220);
            });
        }
    };

    const hideLoadingOverlay = () => {
        if (loading) {
            loading.classList.remove("is-visible");
            loading.setAttribute("aria-hidden", "true");
            loading.querySelectorAll(".loading-item").forEach((item) => item.classList.remove("is-active"));
        }
    };

    if (fileDropzone && resumeInput) {
        fileDropzone.addEventListener("dragover", (event) => {
            event.preventDefault();
            fileDropzone.classList.add("is-dragging");
        });

        fileDropzone.addEventListener("dragleave", () => fileDropzone.classList.remove("is-dragging"));
        fileDropzone.addEventListener("drop", (event) => {
            event.preventDefault();
            fileDropzone.classList.remove("is-dragging");
            const files = event.dataTransfer?.files;
            if (files && files.length) {
                resumeInput.files = files;
                const fileName = files[0]?.name || "Selected PDF";
                const label = fileDropzone.querySelector(".dropzone-text");
                if (label) {
                    label.textContent = fileName;
                }
            }
        });
    }

    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const fileInput = document.getElementById("resume");
            const jobDescriptionInput = document.getElementById("job-description");
            const formData = new FormData();

            errorMessage.textContent = "";
            showLoadingOverlay();

            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                hideLoadingOverlay();
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
                hideLoadingOverlay();
                errorMessage.textContent = error.message || "An unexpected error occurred.";
            }
        });
    }

    const backToTopButton = document.querySelector(".back-to-top");
    if (backToTopButton) {
        const toggleBackToTop = () => {
            if (window.scrollY > 220) {
                backToTopButton.classList.add("is-visible");
            } else {
                backToTopButton.classList.remove("is-visible");
            }
        };

        toggleBackToTop();
        window.addEventListener("scroll", toggleBackToTop, { passive: true });
    }

    const downloadPdfBtn = document.getElementById("download-pdf-btn");
    const printReportBtn = document.getElementById("print-report-btn");

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener("click", () => {
            exportReportToPdf();
        });
    }

    if (printReportBtn) {
        printReportBtn.addEventListener("click", () => window.print());
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

        currentReportData = data;
        renderDashboardHeader(data);
        renderResultsNav();

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
        const suggestionsSection = renderSuggestions(data.suggestions);
        const cards = sections.map(({ key, title }) => {
            const value = data[key];
            return renderResumeSectionAccordion(value, key, title);
        }).join("");

        resultsContainer.innerHTML = `${jobMatchSection}${skillGapSection}${atsSection}${suggestionsSection}<div id="resume-sections" class="results-sections-grid">${cards}</div>`;
        initResultsNavigation();
        initResumeAccordions();
        initSkillGapRoadmap();
        initAtsProgressBars();
        initDashboardAnimations();
    }
});

function renderResumeSectionAccordion(value, key, title) {
    const contentId = `resume-section-${key}`;
    const isOpen = key === "education";
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
        <article class="result-card result-card-accordion${extraClass} result-card-animated">
            <button class="resume-accordion-trigger${isOpen ? " is-active" : ""}" type="button" data-accordion-key="${key}" aria-expanded="${isOpen ? "true" : "false"}" aria-controls="${contentId}">
                <div class="resume-accordion-heading">
                    <span class="resume-accordion-icon" aria-hidden="true">${getSectionIcon(key)}</span>
                    <div class="resume-accordion-title-wrap">
                        <h2>${title}</h2>
                        <p class="resume-accordion-subtitle">${getSectionSubtitle(key)}</p>
                    </div>
                </div>
                <span class="resume-accordion-chevron" aria-hidden="true">+</span>
            </button>
            <div id="${contentId}" class="resume-accordion-panel${isOpen ? " is-open" : ""}" role="region" aria-labelledby="${key}" ${isOpen ? "" : 'aria-hidden="true"'}>
                <div class="resume-accordion-panel-inner">
                    ${renderSectionValue(value, key)}
                </div>
            </div>
        </article>
    `;
}

function initResumeAccordions() {
    const triggers = document.querySelectorAll(".resume-accordion-trigger");
    if (!triggers.length) {
        return;
    }

    let activeKey = null;

    triggers.forEach((trigger) => {
        const key = trigger.dataset.accordionKey;
        const panel = document.getElementById(`resume-section-${key}`);
        if (!panel) {
            return;
        }

        if (trigger.getAttribute("aria-expanded") === "true") {
            activeKey = key;
        }

        trigger.addEventListener("click", () => {
            const shouldOpen = trigger.getAttribute("aria-expanded") !== "true";

            if (activeKey && activeKey !== key) {
                const previousTrigger = document.querySelector(`.resume-accordion-trigger[data-accordion-key="${activeKey}"]`);
                const previousPanel = document.getElementById(`resume-section-${activeKey}`);
                if (previousTrigger) {
                    previousTrigger.setAttribute("aria-expanded", "false");
                    previousTrigger.classList.remove("is-active");
                }
                if (previousPanel) {
                    previousPanel.classList.remove("is-open");
                    previousPanel.setAttribute("aria-hidden", "true");
                }
            }

            if (shouldOpen) {
                trigger.setAttribute("aria-expanded", "true");
                trigger.classList.add("is-active");
                panel.classList.add("is-open");
                panel.setAttribute("aria-hidden", "false");
                activeKey = key;
            } else {
                trigger.setAttribute("aria-expanded", "false");
                trigger.classList.remove("is-active");
                panel.classList.remove("is-open");
                panel.setAttribute("aria-hidden", "true");
                activeKey = null;
            }
        });
    });
}

function getSectionIcon(key) {
    const icons = {
        education: "🎓",
        experience: "💼",
        projects: "🛠️",
        skills: "🧠",
        certifications: "🏅",
        activities: "🌟",
    };

    return icons[key] || "📄";
}

function getSectionSubtitle(key) {
    const subtitles = {
        education: "Academic background",
        experience: "Career timeline",
        projects: "Selected work",
        skills: "Core capabilities",
        certifications: "Professional credentials",
        activities: "Community and leadership",
    };

    return subtitles[key] || "Resume details";
}

function initSkillGapRoadmap() {
    const triggers = document.querySelectorAll(".skill-roadmap-trigger");
    if (!triggers.length) return;
    let activeCard = null;
    triggers.forEach((trigger) => {
        const panel = trigger.nextElementSibling;
        if (!panel) return;
        if (trigger.getAttribute("aria-expanded") === "true") activeCard = trigger;
        trigger.addEventListener("click", () => {
            const isExpanded = trigger.getAttribute("aria-expanded") === "true";
            if (activeCard && activeCard !== trigger) {
                const prevPanel = activeCard.nextElementSibling;
                if (prevPanel) {
                    activeCard.setAttribute("aria-expanded", "false");
                    activeCard.classList.remove("is-active");
                    prevPanel.classList.remove("is-open");
                    prevPanel.setAttribute("aria-hidden", "true");
                }
            }
            if (isExpanded) {
                trigger.setAttribute("aria-expanded", "false");
                trigger.classList.remove("is-active");
                panel.classList.remove("is-open");
                panel.setAttribute("aria-hidden", "true");
                activeCard = null;
            } else {
                trigger.setAttribute("aria-expanded", "true");
                trigger.classList.add("is-active");
                panel.classList.add("is-open");
                panel.setAttribute("aria-hidden", "false");
                activeCard = trigger;
            }
        });
    });
}

function initAtsProgressBars() {
    const rows = document.querySelectorAll(".ats-breakdown-row");
    if (!rows.length) return;

    if (typeof window.IntersectionObserver === "undefined") {
        rows.forEach((row) => animateAtsRow(row));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                animateAtsRow(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    rows.forEach((row) => observer.observe(row));
}

function animateAtsRow(row) {
    if (!row || row.dataset.animated === "true") return;

    const fill = row.querySelector(".ats-breakdown-progress-fill");
    const targetPercentage = parseInt(row.getAttribute("data-percentage"), 10) || 0;

    if (fill) {
        requestAnimationFrame(() => {
            fill.style.width = `${Math.max(0, Math.min(100, targetPercentage))}%`;
        });
    }

    row.dataset.animated = "true";
}

function initDashboardAnimations() {
    const reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) {
        document.querySelectorAll(".result-card-animated, .ats-breakdown-row, .js-progress-fill, .js-counter").forEach((element) => {
            element.classList.add("is-visible");
            if (element.classList.contains("js-progress-fill")) {
                element.style.width = `${element.dataset.progress || 0}%`;
            }
        });
        return;
    }

    const animatedElements = document.querySelectorAll(".result-card-animated, .ats-breakdown-row");
    const counters = document.querySelectorAll(".js-counter");
    const progressBars = document.querySelectorAll(".js-progress-fill");

    if (typeof window.IntersectionObserver !== "undefined") {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.18 });

        animatedElements.forEach((element) => revealObserver.observe(element));
    } else {
        animatedElements.forEach((element) => element.classList.add("is-visible"));
    }

    if (typeof window.IntersectionObserver !== "undefined") {
        const progressObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const fill = entry.target;
                    const target = fill.dataset.progress || 0;
                    fill.style.width = `${target}%`;
                    progressObserver.unobserve(fill);
                }
            });
        }, { threshold: 0.3 });

        progressBars.forEach((bar) => progressObserver.observe(bar));
    } else {
        progressBars.forEach((bar) => {
            bar.style.width = `${bar.dataset.progress || 0}%`;
        });
    }

    counters.forEach((counter) => animateCounter(counter));
}

function animateCounter(element) {
    if (!element || element.dataset.animated === "true") return;

    const target = Number(element.dataset.target);
    if (!Number.isFinite(target)) {
        element.dataset.animated = "true";
        return;
    }

    const duration = 700;
    const startTime = performance.now();
    const suffix = element.dataset.suffix || "";
    const prefix = element.dataset.prefix || "";
    const decimals = Number(element.dataset.decimals || 0);

    const step = (timestamp) => {
        const elapsed = timestamp - startTime;
        const progress = Math.min(1, elapsed / duration);
        const eased = 1 - Math.pow(1 - progress, 3);
        const value = target * eased;
        const formatted = `${prefix}${value.toFixed(decimals)}${suffix}`;
        element.textContent = formatted;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.textContent = `${prefix}${target.toFixed(decimals)}${suffix}`;
            element.dataset.animated = "true";
        }
    };

    requestAnimationFrame(step);
}

function getCounterTarget(value) {
    if (value === null || value === undefined || value === "") {
        return null;
    }

    const numericValue = Number(value);
    return Number.isFinite(numericValue) ? numericValue : null;
}

function renderDashboardHeader(data) {
    const hero = document.getElementById("results-hero");
    if (!hero) {
        return;
    }

    const candidateName = getDisplayValue(getCandidateName(data));
    const professionalTitle = getProfessionalTitle(data);
    const email = getDisplayValue(getCandidateEmail(data));
    const atsScore = getDisplayValue(data?.ats_score?.overall_score ?? "—");
    const jobMatch = getDisplayValue(data?.job_match?.match_percentage ?? "—");
    const skillsFound = Array.isArray(data?.skills) ? data.skills.length : 0;
    const atsScoreTarget = getCounterTarget(data?.ats_score?.overall_score);
    const jobMatchTarget = getCounterTarget(data?.job_match?.match_percentage);
    const skillsFoundTarget = Number.isFinite(skillsFound) ? skillsFound : 0;

    hero.innerHTML = `
        <div id="overview" class="results-hero-card">
            <div class="results-hero-content">
                <div class="results-hero-copy">
                    <div class="results-eyebrow">Resume Insights</div>
                    <h1>Resume Analysis Dashboard</h1>
                    <p class="results-hero-lead">A polished view of the parsed resume and its analysis highlights.</p>
                    <div class="results-hero-profile">
                        <div class="results-hero-profile-main">
                            <div class="results-hero-name">${candidateName}</div>
                            ${professionalTitle ? `<div class="results-hero-title">${escapeHtml(professionalTitle)}</div>` : ""}
                        </div>
                        <div class="results-hero-profile-meta">
                            <div class="results-hero-email">${email}</div>
                            <span class="results-hero-badge">Resume Upload Success</span>
                        </div>
                    </div>
                </div>
                <div class="results-hero-summary" role="list" aria-label="Resume summary metrics">
                    <article class="results-hero-metric" role="listitem">
                        <div class="results-hero-metric-icon" aria-hidden="true">📈</div>
                        <div class="results-hero-metric-main">
                            <div class="results-hero-metric-label">
                                <span class="results-hero-metric-name">ATS Score</span>
                                <span class="results-hero-metric-value js-counter" data-target="${atsScoreTarget ?? 0}">${atsScore}</span>
                            </div>
                            <div class="results-hero-metric-status">Readiness signal</div>
                            <div class="results-hero-metric-progress" aria-hidden="true"><span class="js-progress-fill" data-progress="${getMetricProgress(atsScore)}" style="width: 0%"></span></div>
                        </div>
                        <span class="results-hero-metric-badge">Live</span>
                    </article>
                    <article class="results-hero-metric" role="listitem">
                        <div class="results-hero-metric-icon" aria-hidden="true">🎯</div>
                        <div class="results-hero-metric-main">
                            <div class="results-hero-metric-label">
                                <span class="results-hero-metric-name">Job Match</span>
                                <span class="results-hero-metric-value js-counter" data-target="${jobMatchTarget ?? 0}">${jobMatch}</span>
                            </div>
                            <div class="results-hero-metric-status">Role alignment</div>
                            <div class="results-hero-metric-progress" aria-hidden="true"><span class="js-progress-fill" data-progress="${getMetricProgress(jobMatch)}" style="width: 0%"></span></div>
                        </div>
                        <span class="results-hero-metric-badge">Matched</span>
                    </article>
                    <article class="results-hero-metric" role="listitem">
                        <div class="results-hero-metric-icon" aria-hidden="true">🧠</div>
                        <div class="results-hero-metric-main">
                            <div class="results-hero-metric-label">
                                <span class="results-hero-metric-name">Skills Found</span>
                                <span class="results-hero-metric-value js-counter" data-target="${skillsFoundTarget}">${skillsFound}</span>
                            </div>
                            <div class="results-hero-metric-status">Parsed skills</div>
                            <div class="results-hero-metric-progress" aria-hidden="true"><span class="js-progress-fill" data-progress="${getMetricProgress(skillsFound, true)}" style="width: 0%"></span></div>
                        </div>
                        <span class="results-hero-metric-badge">Parsed</span>
                    </article>
                </div>
            </div>
        </div>
    `;
}

function getMetricProgress(value, isCount = false) {
    if (value === null || value === undefined || value === "" || value === "—") {
        return 0;
    }

    const numericValue = Number(value);
    if (!Number.isFinite(numericValue)) {
        return 0;
    }

    if (isCount) {
        return Math.min(100, Math.max(10, numericValue * 8));
    }

    return Math.min(100, Math.max(10, numericValue));
}

function getCandidateName(data) {
    if (data?.name) {
        return data.name;
    }

    if (data?.contact?.name) {
        return data.contact.name;
    }

    return "Candidate Name Not Available";
}

function getProfessionalTitle(data) {
    if (data?.professional_title) {
        return data.professional_title;
    }

    if (data?.title) {
        return data.title;
    }

    if (Array.isArray(data?.experience) && data.experience.length > 0) {
        const firstExperience = data.experience[0];
        if (firstExperience && typeof firstExperience === "object") {
            const role = firstExperience.title || firstExperience.role || firstExperience.designation;
            if (role) {
                return role;
            }
        }
    }

    const educationTitle = inferTitleFromEducation(data?.education);
    if (educationTitle) {
        return educationTitle;
    }

    const skillsTitle = inferTitleFromSkills(data?.skills);
    if (skillsTitle) {
        return skillsTitle;
    }

    return null;
}

function inferTitleFromEducation(education) {
    if (!education) {
        return null;
    }

    let eduList = Array.isArray(education) ? education : [education];
    if (eduList.length === 0) {
        return null;
    }

    const firstEdu = eduList[0];
    if (!firstEdu || typeof firstEdu !== "object") {
        return null;
    }

    const degree = firstEdu.degree || firstEdu.level || "";
    const field = firstEdu.field || firstEdu.major || firstEdu.branch || firstEdu.specialization || firstEdu.course || "";

    if (!degree && !field) {
        return null;
    }

    const degreeKeywords = {
        "bachelor": "B.Sc",
        "btech": "B.Tech",
        "be": "B.E",
        "bca": "B.C.A",
        "b.sc": "B.Sc",
        "b.tech": "B.Tech",
        "bachelor of": "B.Sc",
        "masters": "M.Sc",
        "master": "M.Sc",
        "mtech": "M.Tech",
        "m.tech": "M.Tech",
        "mca": "M.C.A"
    };

    const degreeLower = degree.toLowerCase().trim();
    let degreePrefix = degree;

    for (const [key, prefix] of Object.entries(degreeKeywords)) {
        if (degreeLower.includes(key)) {
            degreePrefix = prefix;
            break;
        }
    }

    const fieldNormalized = field.trim();
    if (fieldNormalized) {
        return `${fieldNormalized} ${degreePrefix}`;
    }

    return `${degreePrefix} Student`;
}

function inferTitleFromSkills(skills) {
    if (!Array.isArray(skills) || skills.length < 3) {
        return null;
    }

    const skillsLower = skills.map(s => String(s).toLowerCase());
    const skillsJoined = skillsLower.join(" ");

    const titleMappings = [
        {
            keywords: ["machine learning", "tensorflow", "pytorch", "data science", "numpy", "pandas", "scikit"],
            title: "AI & Machine Learning Developer"
        },
        {
            keywords: ["react", "vue", "angular", "javascript", "typescript", "frontend"],
            title: "Frontend Developer"
        },
        {
            keywords: ["python", "django", "flask", "fastapi", "backend", "api"],
            title: "Backend Developer"
        },
        {
            keywords: ["react", "node", "express", "mongodb", "sql", "full stack"],
            title: "Full Stack Developer"
        },
        {
            keywords: ["sql", "mysql", "postgresql", "database", "mongodb"],
            title: "Database Developer"
        },
        {
            keywords: ["java", "spring", "spring boot"],
            title: "Java Developer"
        },
        {
            keywords: ["aws", "docker", "kubernetes", "devops", "ci/cd"],
            title: "DevOps Engineer"
        },
        {
            keywords: ["ios", "swift", "android", "kotlin", "react native", "flutter"],
            title: "Mobile Developer"
        },
        {
            keywords: ["c++", "c#", "graphics", "game"],
            title: "Software Engineer"
        }
    ];

    for (const mapping of titleMappings) {
        const matchCount = mapping.keywords.filter(keyword => skillsJoined.includes(keyword)).length;
        if (matchCount >= 2) {
            return mapping.title;
        }
    }

    return "Software Developer";
}

function getCandidateEmail(data) {
    if (data?.contact?.email) {
        return data.contact.email;
    }

    if (data?.email) {
        return data.email;
    }

    return "Email Not Available";
}

function getDisplayValue(value) {
    if (value === null || value === undefined || value === "") {
        return "Not available";
    }

    return escapeHtml(String(value));
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function renderResultsNav() {
    const nav = document.getElementById("results-nav");
    const toggle = document.getElementById("results-nav-toggle");
    if (!nav) {
        return;
    }

    const items = [
        { id: "overview", label: "Overview", icon: "◉" },
        { id: "ats-analysis", label: "ATS Analysis", icon: "📈" },
        { id: "resume-sections", label: "Resume Sections", icon: "🧾" },
        { id: "job-match", label: "Job Match", icon: "🎯" },
        { id: "missing-skills", label: "Missing Skills", icon: "🧩" },
        { id: "suggestions", label: "Suggestions", icon: "💡" },
    ];

    nav.innerHTML = items.map(({ id, label, icon }) => `
        <a href="#${id}" class="results-nav-item" data-section="${id}">
            <span class="results-nav-icon" aria-hidden="true">${icon}</span>
            <span>${label}</span>
        </a>
    `).join("");

    if (toggle) {
        toggle.addEventListener("click", () => {
            const expanded = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded", String(!expanded));
            nav.classList.toggle("is-open", !expanded);
        });
    }
}

function initResultsNavigation() {
    const navItems = Array.from(document.querySelectorAll(".results-nav-item"));
    const toggle = document.getElementById("results-nav-toggle");
    const nav = document.getElementById("results-nav");

    if (!navItems.length) {
        return;
    }

    const sections = navItems
        .map((item) => document.getElementById(item.dataset.section))
        .filter(Boolean);

    const setActiveItem = (activeId) => {
        navItems.forEach((item) => {
            item.classList.toggle("is-active", item.dataset.section === activeId);
        });
    };

    if (sections.length > 0) {
        const observer = new IntersectionObserver(
            (entries) => {
                const visibleEntry = entries
                    .filter((entry) => entry.isIntersecting)
                    .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

                if (visibleEntry) {
                    const activeId = visibleEntry.target.id;
                    setActiveItem(activeId);
                }
            },
            {
                rootMargin: "-30% 0px -55% 0px",
                threshold: [0.15, 0.35, 0.6],
            }
        );

        sections.forEach((section) => observer.observe(section));
    }

    navItems.forEach((item) => {
        item.addEventListener("click", () => {
            setActiveItem(item.dataset.section);
            if (window.innerWidth <= 900 && toggle && nav) {
                toggle.setAttribute("aria-expanded", "false");
                nav.classList.remove("is-open");
            }
        });
    });

    setActiveItem("overview");
}

function renderSkillGap(skillGap) {
    if (!skillGap || typeof skillGap !== "object") {
        return "";
    }

    const priority = skillGap.priority || "Medium";
    const priorityClass = `priority-${String(priority).toLowerCase()}`;
    const missingSkills = Array.isArray(skillGap.missing_skills) ? skillGap.missing_skills : [];
    const guideItems = Array.isArray(skillGap.skill_guide)
        ? skillGap.skill_guide
        : Array.isArray(skillGap.skill_guides)
            ? skillGap.skill_guides
            : [];

    const roadmapCards = guideItems.length > 0
        ? `<div class="skill-gap-roadmap">${guideItems.map((guide, index) => {
            const name = guide?.skill || guide?.name || "Skill";
            const reason = guide?.reason || "Recommended technology for this job role.";
            const resources = guide?.learning_path || guide?.resources || guide?.learning_resources || "No learning resources listed.";
            const estimatedTime = guide?.estimated_time || guide?.estimatedTime || "Not specified";
            const difficulty = guide?.difficulty || (String(guide?.priority || priority).toLowerCase() === "high" ? "Intermediate" : "Beginner");
            const badge = guide?.priority || priority;
            const badgeClass = `skill-priority-${String(badge).toLowerCase()}`;
            const isOpen = index === 0;
            const cardId = `skill-roadmap-${index}`;

            return `
                <article class="skill-roadmap-card" data-roadmap-skill="${name.toLowerCase().replace(/\s+/g, '-')}">
                    <button class="skill-roadmap-trigger${isOpen ? " is-active" : ""}" type="button" aria-expanded="${isOpen}" aria-controls="${cardId}">
                        <div class="skill-roadmap-trigger-header">
                            <div class="skill-roadmap-trigger-title">
                                <h3>${formatValue(name)}</h3>
                                <p class="skill-roadmap-trigger-reason">${formatValue(reason)}</p>
                            </div>
                            <div class="skill-roadmap-trigger-badges">
                                <span class="skill-roadmap-badge ${badgeClass}">${formatValue(badge)}</span>
                                <span class="skill-roadmap-badge skill-roadmap-badge-difficulty">${formatValue(difficulty)}</span>
                            </div>
                        </div>
                        <span class="skill-roadmap-chevron" aria-hidden="true">+</span>
                    </button>
                    <div id="${cardId}" class="skill-roadmap-panel${isOpen ? " is-open" : ""}" ${isOpen ? "" : 'aria-hidden="true"'}>
                        <div class="skill-roadmap-panel-inner">
                            <div class="skill-roadmap-meta-grid">
                                <div class="skill-roadmap-meta-item">
                                    <span class="skill-roadmap-label">Learning Time</span>
                                    <span class="skill-roadmap-value">${formatValue(estimatedTime)}</span>
                                </div>
                                <div class="skill-roadmap-meta-item">
                                    <span class="skill-roadmap-label">Difficulty</span>
                                    <span class="skill-roadmap-value">${formatValue(difficulty)}</span>
                                </div>
                            </div>
                            <div class="skill-roadmap-guide">
                                <span class="skill-roadmap-label">Learning Path</span>
                                <p>${formatValue(resources)}</p>
                            </div>
                        </div>
                    </div>
                </article>
            `;
        }).join("")}</div>`
        : `<p class="empty-state">No learning roadmap available.</p>`;

    return `
        <section class="result-card result-card-skill-gap" id="missing-skills">
            <div class="section-heading-row">
                <div>
                    <h2>Skill Gap Analysis</h2>
                    <p class="section-heading-copy">Your personalized learning roadmap based on the target role.</p>
                </div>
                <span class="priority-badge ${priorityClass}">${formatValue(priority)} Priority</span>
            </div>
            <div class="skill-gap-intro">
                <p>${missingSkills.length} skill${missingSkills.length !== 1 ? 's' : ''} identified for development</p>
            </div>
            ${roadmapCards}
        </section>
    `;
}

function renderSuggestions(suggestionsData) {
    const suggestions = suggestionsData?.suggestions;
    if (!Array.isArray(suggestions) || suggestions.length === 0) {
        return "";
    }

    return `
        <section class="result-card result-card-suggestions result-card-animated" id="suggestions">
            <h2>Suggestions</h2>
            <ul class="section-list">
                ${suggestions.map((suggestion) => `<li class="section-list-item">${formatValue(suggestion)}</li>`).join("")}
            </ul>
        </section>
    `;
}

function renderAtsScore(atsScore) {
    if (!atsScore || typeof atsScore !== "object") {
        return "";
    }

    const sectionBreakdown = Object.entries(atsScore.section_scores || {}).map(([key, value]) => {
        const weight = getWeight(key);
        const isAvailable = value !== null && value !== undefined && value !== "" && value !== 0;
        const percentage = isAvailable && weight > 0 ? Math.round((value / weight) * 100) : null;
        const status = percentage !== null ? getAtsStatus(percentage) : "Not Available";
        const statusClass = percentage !== null ? getAtsStatusClass(percentage) : "status-unavailable";
        const icon = getAtsIcon(key);
        const displayValue = percentage !== null ? `${percentage}%` : "Not Available";
        const displayLabel = getAtsSectionLabel(key);
        
        return `
            <div class="ats-breakdown-row" data-percentage="${percentage ?? 0}">
                <div class="ats-breakdown-icon" aria-hidden="true">${icon}</div>
                <div class="ats-breakdown-label">
                    <span class="ats-breakdown-name">${formatValue(displayLabel)}</span>
                </div>
                <div class="ats-breakdown-progress-container">
                    <div class="ats-breakdown-progress-bar">
                        <div class="ats-breakdown-progress-fill ${statusClass}" style="width: 0%"></div>
                    </div>
                </div>
                <div class="ats-breakdown-value">${displayValue}</div>
                <span class="ats-breakdown-badge ${statusClass}">${status}</span>
            </div>
        `;
    }).join("");

    const strengths = (atsScore.strengths || []).map((item) => `<li>${formatValue(item)}</li>`).join("");
    const improvements = (atsScore.improvements || []).map((item) => `<li>${formatValue(item)}</li>`).join("");

    return `
        <section class="result-card result-card-ats result-card-animated" id="ats-analysis">
            <h2>ATS Score</h2>
            <div class="ats-score-summary">
                <div class="ats-score-circle js-counter" data-target="${Number.isFinite(Number(atsScore.overall_score)) ? Number(atsScore.overall_score) : 0}">${atsScore.overall_score ?? 0}</div>
                <div class="ats-score-meta">
                    <p class="ats-score-label">Overall ATS Readiness</p>
                    <p class="ats-score-text">A quality-based score based on section depth and completeness.</p>
                </div>
            </div>

            <div class="ats-breakdown-section">
                <h3 class="ats-breakdown-title">Section Breakdown</h3>
                <div class="ats-breakdown-list">
                    ${sectionBreakdown}
                </div>
            </div>

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

    const matchedChips = matchedSkills.length > 0
        ? `<div class="job-match-chips">${matchedSkills.map((skill) => `<span class="job-match-chip job-match-chip-match">✓ ${formatValue(skill)}</span>`).join("")}</div>`
        : `<p class="empty-state">No matched keywords found yet.</p>`;

    const missingCards = missingSkills.length > 0
        ? `<div class="job-match-missing-list">${missingSkills.map((skill) => `
            <article class="job-match-missing-item">
                <div class="job-match-missing-header">
                    <h4>${formatValue(skill)}</h4>
                    <span class="job-match-missing-badge">Missing</span>
                </div>
                <p class="job-match-missing-text">Not found in your resume</p>
            </article>
        `).join("")}</div>`
        : `<p class="empty-state">No missing keywords detected.</p>`;

    return `
        <section class="result-card result-card-job-match result-card-animated" id="job-match">
            <div class="section-heading-row">
                <div>
                    <h2>Job Match</h2>
                    <p class="section-heading-copy">How well your resume aligns with the target role.</p>
                </div>
                <div class="job-match-score-pill js-counter" data-target="${Number.isFinite(Number(matchPercentage)) ? Number(matchPercentage) : 0}" data-suffix="%">${matchPercentage}%</div>
            </div>
            
            <div class="job-match-section">
                <div class="job-match-summary-row">
                    <div class="job-match-score-badge js-counter" data-target="${Number.isFinite(Number(matchPercentage)) ? Number(matchPercentage) : 0}" data-suffix="%">${matchPercentage}%</div>
                    <div>
                        <p class="job-match-summary-label">Role Alignment</p>
                        <p class="job-match-summary-text">${summaryText}</p>
                    </div>
                </div>
            </div>

            <div class="job-match-stacked-cards">
                <article class="job-match-card">
                    <div class="job-match-card-header">
                        <h3>Matched Skills</h3>
                        <span class="job-match-card-badge job-match-card-badge-match">${matchedSkills.length}</span>
                    </div>
                    ${matchedChips}
                </article>

                <article class="job-match-card">
                    <div class="job-match-card-header">
                        <h3>Missing Skills</h3>
                        <span class="job-match-card-badge job-match-card-badge-missing">${missingSkills.length}</span>
                    </div>
                    ${missingCards}
                </article>
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
        activities: 10,
    };

    return weights[key] || 0;
}

function getAtsStatus(percentage) {
    if (percentage >= 90) {
        return "Excellent";
    } else if (percentage >= 75) {
        return "Good";
    } else if (percentage >= 50) {
        return "Average";
    } else {
        return "Needs Improvement";
    }
}

function getAtsStatusClass(percentage) {
    if (percentage >= 90) {
        return "status-excellent";
    } else if (percentage >= 75) {
        return "status-good";
    } else if (percentage >= 50) {
        return "status-average";
    } else {
        return "status-needs-improvement";
    }
}

function getAtsIcon(key) {
    const icons = {
        contact: "📋",
        education: "🎓",
        skills: "🧠",
        projects: "🛠️",
        experience: "💼",
        certifications: "🏆",
        activities: "🌟",
    };
    return icons[key] || "📄";
}

function getAtsSectionLabel(key) {
    const labels = {
        contact: "Contact",
        education: "Education",
        skills: "Skills",
        projects: "Projects",
        experience: "Experience",
        certifications: "Certifications",
        activities: "Activities",
    };

    return labels[key] || String(key).replace(/[_-]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
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
