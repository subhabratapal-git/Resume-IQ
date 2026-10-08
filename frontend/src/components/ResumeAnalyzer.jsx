import { useState, useRef } from "react";
import axios from "axios";
import { API_BASE } from "../config";

import ScoreCard from "./ScoreCard";
import { ROLE_PRESETS } from "../data/rolePresets";

function ResumeAnalyzer({
  onAnalysisSuccess,
  onAnalysisStateChange,
}) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef(null);

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSelectPreset = (preset) => {
    setSelectedPresetId(preset.id);
    setTargetRole(preset.title);
    setJobDescription(preset.description);
    setError("");
  };

  const handleClearPresets = () => {
    setSelectedPresetId("");
    setTargetRole("");
    setJobDescription("");
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const ext = file.name.split(".").pop().toLowerCase();
    if (ext !== "pdf" && ext !== "docx") {
      setError("Please upload a PDF or DOCX file.");
      return;
    }

    setResumeFile(file);
    setError("");
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (!event.currentTarget.contains(event.relatedTarget)) {
      setIsDragging(false);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      const ext = file.name.split(".").pop().toLowerCase();
      if (ext === "pdf" || ext === "docx") {
        setResumeFile(file);
        setError("");
      } else {
        setError("Please upload a PDF or DOCX file.");
      }
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!resumeFile) {
      setError("Please upload your resume.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please paste the job description.");
      return;
    }

    const token =
      localStorage.getItem("resumeiq-token");

    if (!token) {
      setError(
        "Your session has expired. Please log in again."
      );
      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      resumeFile
    );

    formData.append(
      "job_description",
      jobDescription.trim()
    );

    formData.append(
      "target_role",
      targetRole.trim()
    );

    try {
      setLoading(true);

      const response = await axios.post(
        `${API_BASE}/resume/analyze`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setResult(response.data);

      if (onAnalysisStateChange) {
        onAnalysisStateChange(true);
      }

      if (onAnalysisSuccess) {
        onAnalysisSuccess();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Something went wrong while analyzing your resume."
      );
    } finally {
      setLoading(false);
    }
  };

  const atsScore =
    result?.ats_score_details?.ats_score ?? 0;

  const skillMatch =
    result?.skill_match_percentage ?? 0;

  const keywordMatch =
    result?.keyword_analysis
      ?.keyword_match_percentage ?? 0;

  const matchedSkills =
    result?.matched_skills ?? [];

  const missingSkills =
    result?.missing_skills ?? [];

  const educationScore =
    result?.education_analysis
      ?.education_score ?? 0;

  const projectScore =
    result?.project_analysis
      ?.project_score ?? 0;

  const experienceScore =
    result?.experience_analysis
      ?.experience_score ?? 0;

  const structureScore =
    result?.structure_analysis
      ?.structure_score ?? 0;

  const isCompact =
    Boolean(result);

  return (
    <>
      <section
        className={`resume-analyzer-panel ${
          isCompact
            ? "analyzer-compact"
            : "analyzer-expanded"
        }`}
      >
        <div className="analyzer-top">
          <div className="analyzer-title">
            <div className="analyzer-title-icon">
              ▣
            </div>

            <div>
              <h2>Resume Analyzer</h2>

              <p>
                Upload your resume and add a job description
                to get detailed matching insights.
              </p>
            </div>
          </div>

          <span className="analyzer-top-label">
            ✦ NORMAL MODE ANALYSIS
          </span>
        </div>

        {error && (
          <div className="dashboard-error">
            {error}
          </div>
        )}

        <form
          className="analyzer-form"
          onSubmit={handleSubmit}
        >
          <div className="analyzer-main-grid">
            {/* Left: Upload Box with Drag and Drop */}
            <div className="analyzer-upload-col">
              <div
                className={`analyzer-upload-box ${
                  resumeFile ? "has-file" : ""
                } ${isDragging ? "is-dragging" : ""}`}
                onDragOver={handleDragOver}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />

                <div className="upload-cloud">
                  {resumeFile ? "📄" : isDragging ? "📥" : "⇧"}
                </div>

                {resumeFile ? (
                  <div className="upload-file-details">
                    <strong className="upload-file-title">
                      {resumeFile.name}
                    </strong>
                    <span className="upload-file-meta">
                      {(resumeFile.size / 1024 / 1024).toFixed(2)} MB • Selected
                    </span>
                    <button
                      type="button"
                      className="upload-remove-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setResumeFile(null);
                      }}
                    >
                      ✕ Remove Resume
                    </button>
                  </div>
                ) : (
                  <div className="upload-prompt-text">
                    <strong>
                      {isDragging
                        ? "Drop Resume Here"
                        : "Upload Resume (PDF / DOCX)"}
                    </strong>
                    <span>
                      {isDragging
                        ? "Release file to upload"
                        : "Drag & drop your file here, or click to browse"}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Right: Quick Presets, Target Role & Job Description */}
            <div className="analyzer-job-col">
              <div className="analyzer-presets-bar">
                <div className="analyzer-presets-header">
                  <span className="analyzer-presets-title">
                    ⚡ Quick Target Roles
                    <span className="analyzer-presets-subtitle">
                      (click to auto-fill Job Description)
                    </span>
                  </span>

                  {(targetRole || jobDescription) && (
                    <button
                      type="button"
                      className="analyzer-preset-clear-btn"
                      onClick={handleClearPresets}
                    >
                      ✕ Clear
                    </button>
                  )}
                </div>

                <div className="analyzer-preset-chips">
                  {ROLE_PRESETS.map((preset) => {
                    const isSelected =
                      selectedPresetId === preset.id ||
                      (targetRole &&
                        targetRole.trim().toLowerCase() ===
                          preset.title.toLowerCase());

                    return (
                      <button
                        key={preset.id}
                        type="button"
                        className={`analyzer-preset-chip ${
                          isSelected ? "active" : ""
                        }`}
                        onClick={() => handleSelectPreset(preset)}
                        title={`Select ${preset.title} (auto-fills description)`}
                      >
                        {preset.badge}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="analyzer-job-box">
                <div className="analyzer-job-label">
                  <strong>🎯 Target Role</strong>
                  <span style={{ fontSize: "11px", opacity: 0.75 }}>
                    Select preset above or type custom
                  </span>
                </div>

                <input
                  type="text"
                  list="target-roles-preset-list"
                  maxLength={120}
                  placeholder="e.g. Full Stack Developer, Python Developer..."
                  value={targetRole}
                  className="analyzer-role-input"
                  onChange={(event) => {
                    const val = event.target.value;
                    setTargetRole(val);
                    const matched = ROLE_PRESETS.find(
                      (p) =>
                        p.title.toLowerCase() ===
                        val.trim().toLowerCase()
                    );
                    if (matched) {
                      setJobDescription(matched.description);
                      setSelectedPresetId(matched.id);
                    } else {
                      setSelectedPresetId("");
                    }
                  }}
                />
                <datalist id="target-roles-preset-list">
                  {ROLE_PRESETS.map((preset) => (
                    <option key={preset.id} value={preset.title} />
                  ))}
                </datalist>
              </div>

              <div className="analyzer-job-box">
                <div className="analyzer-job-label">
                  <strong>▤ Job Description</strong>
                  <span>{jobDescription.length}/5000</span>
                </div>

                <textarea
                  maxLength={5000}
                  placeholder="Paste job description here or click a preset role above..."
                  value={jobDescription}
                  onChange={(event) => {
                    setJobDescription(event.target.value);
                  }}
                />
              </div>
            </div>
          </div>

          {/* Bottom Action Bar: Full Width Analyze Resume Button */}
          <div className="analyzer-bottom-bar">
            <button
              type="submit"
              className="analyze-resume-button"
              disabled={loading}
            >
              <span>✦</span>
              {loading ? "Analyzing Resume..." : "Analyze Resume"}
              {!loading && <span>→</span>}
            </button>
            <small>
              Get detailed ATS score, skill breakdown, and matching analysis
            </small>
          </div>
        </form>
      </section>

      {result && (
        <>
          <section className="results-overview-panel">
            <div className="result-panel-header">
              <div>
                <span className="result-heading-icon">
                  ▥
                </span>

                <h2>
                  Results Overview
                </h2>
              </div>

              <span>
                ANALYZE + IMPROVE + GET HIRED
              </span>
            </div>

            <div className="score-card-row">
              <ScoreCard
                type="ats"
                score={atsScore}
                title="ATS Score"
                description="Overall ATS compatibility"
              />

              <ScoreCard
                type="skill"
                score={skillMatch}
                title="Skill Match"
                description="Your skills match the job requirements"
              />

              <ScoreCard
                type="keyword"
                score={keywordMatch}
                title="Keywords"
                description="Key terms found in your resume"
              />
            </div>
          </section>

          <section className="detailed-analysis-panel">
            <div className="result-panel-header">
              <div>
                <span className="result-heading-icon">
                  ▤
                </span>

                <h2>
                  Detailed Analysis
                </h2>
              </div>

              <span>
                INSIGHTS THAT HELP YOU GROW
              </span>
            </div>

            <div className="skill-result-row">
              <article className="skill-result-box">
                <div className="skill-result-heading matched">
                  <span>✓</span>
                  Matched Skills
                </div>

                <div className="skill-chip-row">
                  {matchedSkills.length ? (
                    matchedSkills.map(
                      (skill, index) => (
                        <span
                          className="skill-chip matched"
                          key={`${skill}-${index}`}
                        >
                          {skill}
                        </span>
                      )
                    )
                  ) : (
                    <span className="empty-result">
                      No matched skills detected
                    </span>
                  )}
                </div>
              </article>

              <article className="skill-result-box">
                <div className="skill-result-heading missing">
                  <span>×</span>
                  Missing Skills
                </div>

                <div className="skill-chip-row">
                  {missingSkills.length ? (
                    missingSkills.map(
                      (skill, index) => (
                        <span
                          className="skill-chip missing"
                          key={`${skill}-${index}`}
                        >
                          {skill}
                        </span>
                      )
                    )
                  ) : (
                    <span className="empty-result">
                      No missing skills detected
                    </span>
                  )}
                </div>
              </article>
            </div>

            <div className="analysis-summary-row">
              <article className="summary-card">
                <div className="summary-icon">
                  ◇
                </div>

                <div>
                  <strong>
                    Education
                  </strong>

                  <span>
                    {educationScore}/10
                  </span>
                </div>


              </article>

              <article className="summary-card">
                <div className="summary-icon">
                  ◈
                </div>

                <div>
                  <strong>
                    Projects
                  </strong>

                  <span>
                    {projectScore}/10
                  </span>
                </div>


              </article>

              <article className="summary-card">
                <div className="summary-icon">
                  ▣
                </div>

                <div>
                  <strong>
                    Experience
                  </strong>

                  <span>
                    {experienceScore}/15
                  </span>
                </div>


              </article>

              <article className="summary-card">
                <div className="summary-icon">
                  ▤
                </div>

                <div>
                  <strong>
                    Structure
                  </strong>

                  <span className="structure-good">
                    {structureScore}/5
                  </span>
                </div>


              </article>
            </div>
          </section>
        </>
      )}
    </>
  );
}

export default ResumeAnalyzer;

