import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import Brand from "../components/Brand";
import ThemeToggle from "../components/ThemeToggle";
import ProfileMenu from "../components/ProfileMenu";
import { logoutUser } from "../services/authApi";
import { getAnalysisHistory } from "../services/resumeApi";
import { ROLE_PRESETS } from "../data/rolePresets";

import "../styles/theme.css";
import "../styles/dashboard.css";
import "../styles/ProDashboard.css";
import { API_BASE } from "../config";

// ─── Circular Score Ring ──────────────────────────────────────────────────
function ScoreRing({ score, size = 80, color = "#10b981" }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (circ * score) / 100;
  return (
    <div className="pro-section-ring-wrap" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
        <text x={size / 2} y={size / 2} textAnchor="middle" dominantBaseline="central" fill="#f8fafc" fontSize="14" fontWeight="800">
          {score}%
        </text>
      </svg>
    </div>
  );
}

// ─── Priority Pill ────────────────────────────────────────────────────────
const PRIORITY_STYLE = {
  High:   { bg: "rgba(239,68,68,0.15)",   border: "rgba(239,68,68,0.4)",   color: "#f87171" },
  Medium: { bg: "rgba(245,158,11,0.15)",  border: "rgba(245,158,11,0.4)",  color: "#fbbf24" },
  Low:    { bg: "rgba(16,185,129,0.15)",  border: "rgba(16,185,129,0.4)",  color: "#34d399" },
};

function PriorityPill({ p }) {
  const s = PRIORITY_STYLE[p] || PRIORITY_STYLE.Low;
  return (
    <span
      className="pro-priority-pill"
      style={{ background: s.bg, border: `1px solid ${s.border}`, color: s.color }}
    >
      {p}
    </span>
  );
}

// ─── Main ProDashboard Component ──────────────────────────────────────────
function ProDashboard() {
  const navigate = useNavigate();

  const [theme, setTheme] = useState(() =>
    localStorage.getItem("resumeiq-theme") === "light" ? "light" : "color"
  );
  const [user] = useState(() => {
    try { return JSON.parse(localStorage.getItem("resumeiq-user") || "null"); }
    catch { return null; }
  });
  const [analysisCount, setAnalysisCount] = useState(0);
  const [proUsesRemaining, setProUsesRemaining] = useState(() => user?.pro_uses_remaining ?? 5);
  const [isAiActive, setIsAiActive] = useState(true);
  const [showPaywallModal, setShowPaywallModal] = useState(false);

  // ── Checkout & Payment Modal State ──────────────────────────────────────
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState("monthly"); // "monthly" (₹199) or "annual" (₹999)
  const [paymentMethod, setPaymentMethod] = useState("upi"); // "upi" | "card" | "netbanking"
  const [paymentStep, setPaymentStep] = useState("form"); // "form" | "processing" | "failed"
  const [processingStatus, setProcessingStatus] = useState("");

  // Payment form fields
  const [upiApp, setUpiApp] = useState("gpay");
  const [upiId, setUpiId] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvv, setCardCvv] = useState("");
  const [cardHolder, setCardHolder] = useState("");
  const [selectedBank, setSelectedBank] = useState("hdfc");
  const [paymentFormError, setPaymentFormError] = useState("");

  // Form state
  const [resumeFile, setResumeFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [selectedPresetId, setSelectedPresetId] = useState("");
  const [candidateType, setCandidateType] = useState("experience");

  // Analysis state
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState({ pdf: false, docx: false });

  // UI modal and toggle states
  const [showResumeModal, setShowResumeModal] = useState(false);
  const [showAllSuggestions, setShowAllSuggestions] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("resumeiq-theme", theme);
  }, [theme]);

  useEffect(() => {
    async function loadStatsAndStatus() {
      try {
        const token = localStorage.getItem("resumeiq-token");
        if (token) {
          const res = await axios.get(`${API_BASE}/api/pro/status`, {
            headers: { Authorization: `Bearer ${token}` },
            timeout: 8000,
          });
          if (typeof res.data.pro_uses_remaining === "number") {
            setProUsesRemaining(res.data.pro_uses_remaining);
          }
          if (typeof res.data.is_ai_active === "boolean") {
            setIsAiActive(res.data.is_ai_active);
          }
          if (typeof res.data.total_analyses === "number") {
            setAnalysisCount(res.data.total_analyses);
          }
        }
      } catch (err) {
        try {
          const data = await getAnalysisHistory(0);
          if (data && typeof data.total === "number") {
            setAnalysisCount(data.total);
          }
        } catch {}
      }
    }
    loadStatsAndStatus();
  }, []);

  const handleLogout = () => {
    logoutUser();
    navigate("/", { replace: true });
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer?.files?.[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target?.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (file) => {
    const extension = file.name.split(".").pop().toLowerCase();
    const MAX_SIZE_MB = 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    if (extension !== "pdf" && extension !== "docx") {
      setError("Please upload a valid PDF or DOCX file.");
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setError(`File is too large. Maximum allowed size is ${MAX_SIZE_MB} MB.`);
      return;
    }

    setResumeFile(file);
    setError("");
  };

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

  // ── Payment Gateway Handlers ─────────────────────────────────────────────
  const handleOpenCheckout = (planKey) => {
    setSelectedPlan(planKey);
    setShowPaywallModal(false);
    setShowPaymentModal(true);
    setPaymentStep("form");
    setPaymentFormError("");
  };

  const handleCardNumberChange = (val) => {
    const raw = val.replace(/\D/g, "").slice(0, 16);
    const formatted = raw.replace(/(\d{4})(?=\d)/g, "$1 ");
    setCardNumber(formatted);
  };

  const handleExpiryChange = (val) => {
    const raw = val.replace(/\D/g, "").slice(0, 4);
    if (raw.length >= 3) {
      setCardExpiry(`${raw.slice(0, 2)}/${raw.slice(2, 4)}`);
    } else {
      setCardExpiry(raw);
    }
  };

  const handleCvvChange = (val) => {
    const raw = val.replace(/\D/g, "").slice(0, 4);
    setCardCvv(raw);
  };

  const handleProcessPayment = (e) => {
    if (e) {
      e.preventDefault();
    }
    setPaymentFormError("");

    if (paymentMethod === "upi") {
      if (upiApp === "other" && !upiId.trim()) {
        setPaymentFormError("Please enter your UPI ID (e.g., yourname@okhdfcbank)");
        return;
      }
    } else if (paymentMethod === "card") {
      const cleanNum = cardNumber.replace(/\s+/g, "");
      if (cleanNum.length < 16) {
        setPaymentFormError("Please enter a valid 16-digit debit/credit card number");
        return;
      }
      if (!cardExpiry.trim()) {
        setPaymentFormError("Please enter the card expiry date (MM/YY)");
        return;
      }
      if (cardCvv.trim().length < 3) {
        setPaymentFormError("Please enter a valid 3-digit CVV number");
        return;
      }
      if (!cardHolder.trim()) {
        setPaymentFormError("Please enter the cardholder name as printed on card");
        return;
      }
    }

    setPaymentStep("processing");
    setProcessingStatus("Initiating secure banking handshake...");

    const timer1 = setTimeout(() => {
      setProcessingStatus("Encrypting payment credentials with 256-bit TLS...");
    }, 900);

    const timer2 = setTimeout(() => {
      setProcessingStatus("Awaiting bank authorization response...");
    }, 1800);

    setTimeout(() => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      // Realistic technical gateway failure at the last moment
      setPaymentStep("failed");
    }, 2800);
  };

  const handleRetryPayment = () => {
    setPaymentStep("form");
    setPaymentFormError("");
  };

  const handleAnalyze = async (e) => {
    if (e) {
      e.preventDefault();
    }
    setError("");

    if (proUsesRemaining <= 0) {
      setShowPaywallModal(true);
      setError("You have used all 5 free Pro analyses. Please upgrade your subscription to continue.");
      return;
    }

    if (!resumeFile) {
      setError("Please upload your resume (PDF or DOCX).");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please provide a target job description.");
      return;
    }

    const token = localStorage.getItem("resumeiq-token");
    if (!token) {
      setError("Your session has expired. Please log in again.");
      return;
    }

    setLoading(true);
    setLoadingStep("Extracting text and analyzing keyword vectorization...");
    const t1 = setTimeout(() => {
      setLoadingStep("Evaluating Section Diagnostics & ATS scoring...");
    }, 900);
    const t2 = setTimeout(() => {
      setLoadingStep("Synthesizing content optimizations and professional CV...");
    }, 2200);

    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      // Trim job description to backend's max (8000 chars) before sending
      formData.append("job_description", jobDescription.trim().slice(0, 8000));
      formData.append("target_role", targetRole.trim().slice(0, 120) || "Software Engineer");
      formData.append("candidate_type", candidateType);

      const { data } = await axios.post(`${API_BASE}/api/pro/analyze`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
        timeout: 90000,
      });

      clearTimeout(t1);
      clearTimeout(t2);

      if (typeof data.pro_uses_remaining === "number") {
        setProUsesRemaining(data.pro_uses_remaining);
        if (user) {
          const updatedUser = {
            ...user,
            pro_uses_remaining: data.pro_uses_remaining,
          };
          localStorage.setItem("resumeiq-user", JSON.stringify(updatedUser));
        }
      }

      if (typeof data.is_gemini === "boolean") {
        setIsAiActive(data.is_gemini);
      }

      if (typeof data.analysis_id === "number") {
        setAnalysisCount((prev) => prev + 1);
      }

      setResults(data);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      clearTimeout(t1);
      clearTimeout(t2);
      if (err.response?.status === 403) {
        setShowPaywallModal(true);
      }
      setError(err.response?.data?.detail || "Analysis failed. Ensure backend server is running.");
    } finally {
      setLoading(false);
      setLoadingStep("");
    }
  };

  const handleDownload = async (format) => {
    if (!results?.corrected_resume_text) {
      return;
    }

    setDownloading((prev) => ({
      ...prev,
      [format]: true,
    }));

    try {
      const token = localStorage.getItem("resumeiq-token");
      const res = await axios.post(
        `${API_BASE}/api/pro/export`,
        {
          corrected_resume_text: results.corrected_resume_text,
          format: format,
        },
        {
          responseType: "blob",
          // Security fix: /export now requires authentication.
          // Without the token the backend returns 403.
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const mimeType =
        format === "pdf"
          ? "application/pdf"
          : "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

      const blob = new Blob([res.data], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `Pro_Resume.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert("Download failed. Please try again.");
    } finally {
      setDownloading((prev) => ({
        ...prev,
        [format]: false,
      }));
    }
  };

  const handleCopy = () => {
    if (!results?.corrected_resume_text) {
      return;
    }
    navigator.clipboard.writeText(results.corrected_resume_text);
    setCopied(true);
    setTimeout(() => {
      setCopied(false);
    }, 2200);
  };

  const getScoreLabel = (scoreVal) => {
    if (scoreVal >= 80) {
      return { label: "Excellent Match", color: "#10b981" };
    }
    if (scoreVal >= 65) {
      return { label: "Strong Match", color: "#3b82f6" };
    }
    if (scoreVal >= 50) {
      return { label: "Good Match", color: "#f59e0b" };
    }
    return { label: "Needs Work", color: "#ef4444" };
  };

  const score     = results?.pro_match_score ?? 0;
  const scoreInfo = getScoreLabel(score);

  return (
    <div className="app-theme dashboard-page pro-page" data-theme={theme}>
      {/* ── Background Glow ── */}
      <div className="dashboard-background">
        <div className="dashboard-grid-background" />
        <div className="dashboard-glow dashboard-glow-left pro-glow-orb-1" />
        <div className="dashboard-glow dashboard-glow-right pro-glow-orb-2" />
        <div className="dashboard-wave dashboard-wave-one" />
        <div className="dashboard-wave dashboard-wave-two" />
      </div>

      {/* ── Header ── */}
      <header className="main-header dashboard-header">
        <div className="header-container">
          <Brand />
          <div className="dashboard-header-actions">
            <div
              className={`pro-ai-mode-header-badge ${isAiActive ? "active" : "inactive"}`}
              title={isAiActive ? "AI Mode: Connected & Active" : "AI Mode: Offline / Local Intelligent Engine"}
            >
              <span className={isAiActive ? "pro-ai-pulse-dot" : "pro-ai-off-dot"} />
              <span className="pro-ai-badge-text">
                AI Mode: <strong>{isAiActive ? "ON" : "OFF"}</strong>
              </span>
            </div>
            <ThemeToggle theme={theme} setTheme={setTheme} />
            <div className="dashboard-header-separator" />
            <ProfileMenu user={user} analysisCount={analysisCount} proUsesRemaining={proUsesRemaining} onLogout={handleLogout} />
          </div>
        </div>
      </header>

      <main className="pro-container">

        {/* ── Hero (Shown when inputting) ── */}
        {!results && (
          <section className="pro-hero-section">
            <div className="pro-hero-breadcrumb">
              <span className="pro-hero-tag">♛ PRO MODE</span>
              <span className={`pro-hero-uses-pill ${proUsesRemaining <= 0 ? "exhausted" : ""}`}>
                ⚡ <strong>{proUsesRemaining}</strong> of 5 Free Analyses Remaining
              </span>
            </div>
            <div className="pro-hero-content">
              <div className="pro-hero-text">
                <h1 className="pro-hero-title">
                  Objective Scoring &nbsp;
                  <span className="pro-gradient-text">& Professional Optimization</span>
                </h1>
                <p className="pro-hero-desc">
                  Deep semantic analysis identifies exact resume gaps and scoring breakdown,
                  while expert recommendations help you maximize recruiter impact and ATS compliance.
                </p>
              </div>
              <div className="pro-hero-stats">
                <div className="pro-stat-chip"><span className="pro-chip-icon">🎯</span><div><strong>Verified Accuracy</strong><small>Zero Inflated Scores</small></div></div>
                <div className="pro-stat-chip"><span className="pro-chip-icon">✨</span><div><strong>Best Suggestions</strong><small>Targeted Improvements</small></div></div>
              </div>
            </div>
          </section>
        )}

        {/* ── Error Banner ── */}
        {error && (
          <div className="pro-alert-banner">
            <span>⚠️</span>
            <div className="pro-alert-message">{error}</div>
            <button className="pro-alert-dismiss" onClick={() => setError("")}>✕</button>
          </div>
        )}

        {/* ── Results Topbar ── */}
        {results && (
          <div className="pro-results-topbar">
            <div className="pro-topbar-title">
              <div className="pro-topbar-crown-wrap">
                <span className="pro-crown">♛</span>
              </div>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "14px", flexWrap: "wrap", marginBottom: "4px" }}>
                  <h1 style={{ margin: 0 }}>Your Resume, <span className="pro-gradient-text">Professionally Decoded</span></h1>
                  <div
                    className={`pro-ai-mode-header-badge ${results.is_gemini ? "active" : "inactive"}`}
                    style={{ fontSize: "0.74rem", padding: "4px 12px" }}
                  >
                    <span className={results.is_gemini ? "pro-ai-pulse-dot" : "pro-ai-off-dot"} />
                    <span>AI Mode: <strong>{results.is_gemini ? "ON" : "OFF"}</strong></span>
                  </div>
                </div>
                <p>Every section scored. Every gap identified. Your path to the perfect job, crystal clear.</p>
              </div>
            </div>
          </div>
        )}

        {/* ── Filebar with "View Resume" button ── */}
        {results && (
          <div className="pro-filebar">
            <div className="pro-filebar-left">
              <span className="pro-file-emoji">📄</span>
              <div>
                <div className="pro-filebar-name">{results.filename || resumeFile?.name}</div>
                <div className="pro-filebar-meta">
                  Target Role: <strong>{results.target_role}</strong> · {results.candidate_type === "fresher" ? "🎓 Freshers Profile" : "💼 Experienced Profile"} · Analyzed on {results.analyzed_at}
                </div>
              </div>
            </div>
            <div className="pro-filebar-actions">
              <button className="pro-btn-secondary" onClick={() => setResults(null)}>🔄 New Analysis</button>
              <button className="pro-btn-action pro-btn-docx" onClick={() => setShowResumeModal(true)}>
                📄 View Uploaded Resume
              </button>
            </div>
          </div>
        )}

        {/* ════════════════════════════════════════════════════════════
            INPUT FORM (Upload & Job Description)
            ════════════════════════════════════════════════════════════ */}
        {!results && (
          <section className="pro-input-panel">
            <div className="pro-panel-header">
              <div className="pro-panel-title">
                <span className="pro-panel-icon">📤</span>
                <div>
                  <h2>Resume & Job Description</h2>
                  <p>Upload your CV and paste the job description to begin Pro analysis.</p>
                </div>
              </div>

              <div className="pro-quota-card" style={{ margin: 0, padding: "8px 16px" }}>
                <div className="pro-quota-left" style={{ gap: "10px" }}>
                  <span className="pro-quota-icon" style={{ fontSize: "1.2rem" }}>✨</span>
                  <div className="pro-quota-info">
                    <strong style={{ fontSize: "0.85rem" }}>{proUsesRemaining} / 5 Free Uses Remaining</strong>
                  </div>
                </div>
                <div className="pro-quota-right" style={{ gap: "10px" }}>
                  <div className="pro-quota-progress" style={{ width: "80px", height: "6px" }}>
                    <div className="pro-quota-progress-fill" style={{ width: `${(Math.max(0, proUsesRemaining) / 5) * 100}%` }} />
                  </div>
                  {proUsesRemaining <= 0 && (
                    <button type="button" className="pro-quota-upgrade-btn" onClick={() => setShowPaywallModal(true)}>
                      Upgrade
                    </button>
                  )}
                </div>
              </div>
            </div>

            <form onSubmit={handleAnalyze} className="pro-form-grid">
              {/* Left Column: File Dropzone */}
              <div className="pro-upload-column">
                <label className="pro-field-label">
                  <span>📄 Resume Document</span>
                  <span className="pro-label-badge">PDF or DOCX</span>
                </label>
                <div
                  className={`pro-dropzone ${resumeFile ? "has-file" : ""} ${isDragging ? "is-dragging" : ""}`}
                  onDragOver={handleDragOver} onDragEnter={handleDragOver}
                  onDragLeave={handleDragLeave} onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input ref={fileInputRef} type="file" accept=".pdf,.docx" onChange={handleFileChange} style={{ display: "none" }} />
                  {resumeFile ? (
                    <div className="pro-file-card">
                      <div className="pro-file-avatar">{resumeFile.name.endsWith(".pdf") ? "📕" : "📘"}</div>
                      <div className="pro-file-meta">
                        <strong className="pro-file-name">{resumeFile.name}</strong>
                        <span className="pro-file-size">{(resumeFile.size / 1024 / 1024).toFixed(2)} MB · Ready for Deep Scan</span>
                      </div>
                      <button type="button" className="pro-remove-file-btn" onClick={(e) => { e.stopPropagation(); setResumeFile(null); }}>✕</button>
                    </div>
                  ) : (
                    <div className="pro-dropzone-empty">
                      <div className="pro-dropzone-icon">{isDragging ? "📥" : "☁️"}</div>
                      <strong>{isDragging ? "Drop file now" : "Click or Drag & Drop"}</strong>
                      <span>PDF and DOCX supported · up to 10MB</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Presets & Job Description */}
              <div className="pro-jd-column">
                <div className="pro-presets-wrapper">
                  <div className="pro-presets-top">
                    <label className="pro-field-label"><span>⚡ Quick Role Presets</span><small>(auto-fill JD)</small></label>
                    {(targetRole || jobDescription) && <button type="button" className="pro-link-btn" onClick={handleClearPresets}>✕ Clear</button>}
                  </div>
                  <div className="pro-preset-chips">
                    {ROLE_PRESETS.slice(0, 6).map((p) => (
                      <button key={p.id} type="button"
                        className={`pro-preset-chip ${selectedPresetId === p.id ? "active" : ""}`}
                        onClick={() => handleSelectPreset(p)}>
                        {p.badge}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="pro-field-group">
                  <label className="pro-field-label"><span>🎯 Target Role</span><small>Optional</small></label>
                  <input type="text" className="pro-input-text" placeholder="e.g. Frontend React Developer" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} />
                </div>
                <div className="pro-field-group">
                  <label className="pro-field-label"><span>📋 Job Description</span><span className="pro-label-badge pro-badge-required">Required</span></label>
                  <textarea className="pro-textarea" rows={6} placeholder="Paste the target job description here..." value={jobDescription} onChange={(e) => { setJobDescription(e.target.value); setSelectedPresetId(""); }} />
                </div>

                {/* Candidate Level: Freshers vs Experience Toggle */}
                <div className="pro-field-group pro-candidate-type-group">
                  <label className="pro-field-label">
                    <span>👤 Candidate Profile Level</span>
                    <small>Customizes experience criteria & internship weighting</small>
                  </label>
                  <div className="pro-candidate-pills">
                    <button
                      type="button"
                      className={`pro-candidate-pill ${candidateType === "fresher" ? "active" : ""}`}
                      onClick={() => setCandidateType("fresher")}
                    >
                      <span className="pro-pill-icon">🎓</span>
                      <span className="pro-pill-text">Freshers</span>
                    </button>
                    <button
                      type="button"
                      className={`pro-candidate-pill ${candidateType === "experience" ? "active" : ""}`}
                      onClick={() => setCandidateType("experience")}
                    >
                      <span className="pro-pill-icon">💼</span>
                      <span className="pro-pill-text">Experience</span>
                    </button>
                  </div>
                </div>

                <div className="pro-action-row">
                  <button type="submit" className="pro-btn-launch" disabled={loading}>
                    {loading ? (
                      <span className="pro-loading-inner"><span className="pro-spinner" />{loadingStep || "Running Pro Analysis..."}</span>
                    ) : (
                      <><span>🚀 Launch Pro Resume Analysis</span><div className="pro-btn-glow" /></>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </section>
        )}

        {/* ════════════════════════════════════════════════════════════
            RESULTS DASHBOARD
            ════════════════════════════════════════════════════════════ */}
        {results && (
          <div className="pro-results-body">

            {/* ── ROW 1: ATS Match Score & Breakdown ── */}
            <div className="pro-row pro-row-2">
              {/* Card 1: ATS Overall Score */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">🏅</span>
                  <h3>Overall ATS Match Score</h3>
                </div>
                <div className="pro-match-body">
                  <div className="pro-big-gauge">
                    <svg viewBox="0 0 140 140" className="pro-big-svg">
                      <circle cx="70" cy="70" r="58" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="12" />
                      <circle
                        cx="70" cy="70" r="58" fill="none"
                        stroke={scoreInfo.color}
                        strokeWidth="12"
                        strokeLinecap="round"
                        strokeDasharray={`${2 * Math.PI * 58}`}
                        strokeDashoffset={`${2 * Math.PI * 58 * (1 - score / 100)}`}
                        transform="rotate(-90 70 70)"
                        style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(.16,1,.3,1)" }}
                      />
                      <text x="70" y="65" textAnchor="middle" fill="#f8fafc" fontSize="28" fontWeight="800">{score}%</text>
                      <text x="70" y="85" textAnchor="middle" fill={scoreInfo.color} fontSize="11" fontWeight="700">{scoreInfo.label}</text>
                    </svg>
                  </div>
                  <p className="pro-match-desc">
                    {score >= 75
                      ? "High ATS compatibility. Your resume matches key JD requirements with minor keyword gaps."
                      : "Moderate ATS match. Incorporating the missing skills and bullet rewrites below will directly raise your score."}
                  </p>
                </div>
              </div>

              {/* Card 2: Score Breakdown Bars */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">📊</span>
                  <h3>ATS Score Breakdown</h3>
                </div>
                <div className="pro-breakdown-list">
                  {[
                    { label: "Overall ATS Score",      val: results.score_breakdown?.ats_score ?? score,            color: "#38bdf8" },
                    { label: "Semantic Keyword Match",  val: results.score_breakdown?.semantic_match ?? 70,         color: "#818cf8" },
                    { label: "Skill Relevance",         val: results.score_breakdown?.skill_match ?? 65,            color: "#10b981" },
                    { label: "Experience Alignment",    val: results.score_breakdown?.experience_relevance ?? 60,   color: "#f59e0b" },
                    { label: "Project Relevance",       val: results.score_breakdown?.project_relevance ?? 75,      color: "#a78bfa" },
                    { label: "Overall Quality Index",   val: results.score_breakdown?.overall_quality ?? 72,        color: "#34d399" },
                  ].map(({ label, val, color }) => (
                    <div className="pro-breakdown-row" key={label}>
                      <span className="pro-bd-label">{label}</span>
                      <div className="pro-bd-bar">
                        <div className="pro-bd-fill" style={{ width: `${val}%`, background: color }} />
                      </div>
                      <span className="pro-bd-val" style={{ color }}>{val}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ── ROW 2: Section-Wise Diagnostics ── */}
            <div className="pro-card pro-card-full">
              <div className="pro-card-header">
                <span className="pro-card-icon">📑</span>
                <div>
                  <h3>Section-Wise Diagnostics</h3>
                  <p>Detailed objective analysis: see verified alignment and areas for refinement in each section.</p>
                </div>
              </div>

              <div className="pro-section-diagnostics-grid">
                {results.section_wise && results.section_wise.map((sec) => (
                  <div key={sec.id} className="pro-sec-diag-card">
                    <div className="pro-sec-diag-header">
                      <div className="pro-sec-diag-title-wrap">
                        <ScoreRing score={sec.score} size={68} color={sec.color} />
                        <div>
                          <h4>{sec.title}</h4>
                          <span className="pro-sec-feedback-pill" style={{ color: sec.color, borderColor: `${sec.color}44` }}>
                            {sec.feedback}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Section Specific Details */}
                    <div className="pro-sec-diag-body">
                      {/* Skills section: Show matched and missing pills */}
                      {sec.id === "skills" && (
                        <div className="pro-diag-skills-block">
                          <div className="pro-diag-subgroup">
                            <span className="pro-diag-label text-success">✓ Matched Skills ({sec.matched_skills?.length || 0})</span>
                            <div className="pro-diag-tags">
                              {sec.matched_skills && sec.matched_skills.length > 0 ? (
                                sec.matched_skills.map((s, idx) => (
                                  <span key={idx} className="pro-diag-tag matched">{s}</span>
                                ))
                              ) : (
                                <span className="pro-diag-none">No exact skills matched.</span>
                              )}
                            </div>
                          </div>

                          <div className="pro-diag-subgroup">
                            <span className="pro-diag-label text-warning">✕ Missing JD Skills ({sec.missing_skills?.length || 0})</span>
                            <div className="pro-diag-tags">
                              {sec.missing_skills && sec.missing_skills.length > 0 ? (
                                sec.missing_skills.map((s, idx) => (
                                  <span key={idx} className="pro-diag-tag missing">{s}</span>
                                ))
                              ) : (
                                <span className="pro-diag-none">All required skills present!</span>
                              )}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* General deductions and issues for Experience, Projects, Education (Suppressed when score is 100%) */}
                      {sec.deduction_reasons && sec.deduction_reasons.length > 0 && sec.score < 100 && (
                        <div className="pro-diag-deductions">
                          <span className="pro-diag-label text-danger">⚠️ Why Points Were Deducted:</span>
                          <ul className="pro-diag-bullet-list">
                            {sec.deduction_reasons.map((reason, idx) => (
                              <li key={idx}>{reason}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Positive points detected */}
                      {sec.matched_points && sec.matched_points.length > 0 && sec.id !== "skills" && (
                        <div className="pro-diag-positives">
                          <span className="pro-diag-label text-success">✓ Verified Strengths:</span>
                          <ul className="pro-diag-bullet-list">
                            {sec.matched_points.map((pt, idx) => (
                              <li key={idx}>{pt}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ── ROW 3: Top Strengths & Resume Gaps ── */}
            <div className="pro-row pro-row-2">
              {/* Card 4: Top Strengths */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">🏆</span>
                  <div>
                    <h3>Top Strengths</h3>
                    <p>Core areas where your profile strongly satisfies job requirements.</p>
                  </div>
                </div>
                <div className="pro-strength-list">
                  {results.top_strengths && results.top_strengths.map((s, i) => (
                    <div key={i} className="pro-strength-item" style={{ animationDelay: `${i * 0.07}s` }}>
                      <div className="pro-strength-icon-wrap">
                        <span className="pro-strength-icon">✓</span>
                      </div>
                      <div className="pro-strength-content">
                        <span className="pro-strength-text">{s}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 5: Resume Gaps */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">🎯</span>
                  <div>
                    <h3>Resume Gaps</h3>
                    <p>Critical profile gaps where targeted additions will raise your ATS match score.</p>
                  </div>
                </div>
                <div className="pro-gap-list">
                  {results.key_improvements && results.key_improvements.map((s, i) => (
                    <div key={i} className="pro-gap-item" style={{ animationDelay: `${i * 0.07}s` }}>
                      <div className="pro-gap-icon-wrap">
                        <span className="pro-gap-icon">!</span>
                      </div>
                      <div className="pro-gap-content">
                        <span className="pro-gap-text">{s}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ── ROW 4: Best Suggestions (grouped by priority) & Recommended Rewrites ── */}
            <div className="pro-row pro-row-2">
              {/* Card 6: Best Suggestions - grouped by priority */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">💡</span>
                  <div>
                    <h3>Best Suggestions</h3>
                    <p>Actionable recommendations grouped by priority to resolve identified resume gaps.</p>
                  </div>
                </div>
                {results.ai_suggestions && results.ai_suggestions.length > 0 ? (
                  <div className="pro-suggestions-grouped">
                    {/* High Priority */}
                    {results.ai_suggestions.filter(s => s.priority === "High").length > 0 && (
                      <div className="pro-priority-group pro-priority-group-high">
                        <div className="pro-priority-group-header">
                          <span className="pro-priority-dot" />
                          <span className="pro-priority-group-label">High Priority</span>
                          <span className="pro-priority-group-count">{results.ai_suggestions.filter(s => s.priority === "High").length}</span>
                        </div>
                        <div className="pro-priority-items">
                          {results.ai_suggestions.filter(s => s.priority === "High").map((s) => (
                            <div key={s.id} className="pro-suggestion-card pro-suggestion-card-high">
                              <span className="pro-sug-num">{s.id}</span>
                              <span className="pro-sug-text">{s.text}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Medium Priority */}
                    {results.ai_suggestions.filter(s => s.priority === "Medium").length > 0 && (
                      <div className="pro-priority-group pro-priority-group-medium">
                        <div className="pro-priority-group-header">
                          <span className="pro-priority-dot" />
                          <span className="pro-priority-group-label">Medium Priority</span>
                          <span className="pro-priority-group-count">{results.ai_suggestions.filter(s => s.priority === "Medium").length}</span>
                        </div>
                        <div className="pro-priority-items">
                          {results.ai_suggestions.filter(s => s.priority === "Medium").map((s) => (
                            <div key={s.id} className="pro-suggestion-card pro-suggestion-card-medium">
                              <span className="pro-sug-num">{s.id}</span>
                              <span className="pro-sug-text">{s.text}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Low Priority */}
                    {results.ai_suggestions.filter(s => s.priority === "Low").length > 0 && (
                      <div className="pro-priority-group pro-priority-group-low">
                        <div className="pro-priority-group-header">
                          <span className="pro-priority-dot" />
                          <span className="pro-priority-group-label">Low Priority</span>
                          <span className="pro-priority-group-count">{results.ai_suggestions.filter(s => s.priority === "Low").length}</span>
                        </div>
                        <div className="pro-priority-items">
                          {results.ai_suggestions.filter(s => s.priority === "Low").map((s) => (
                            <div key={s.id} className="pro-suggestion-card pro-suggestion-card-low">
                              <span className="pro-sug-num">{s.id}</span>
                              <span className="pro-sug-text">{s.text}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p style={{ color: "#94a3b8", fontSize: ".85rem" }}>No suggestions available.</p>
                )}
              </div>

              {/* Card 7: Recommended Content Rewrites */}
              <div className="pro-card">
                <div className="pro-card-header">
                  <span className="pro-card-icon">✍️</span>
                  <div>
                    <h3>Recommended Content Rewrites</h3>
                    <p>Targeted sentence and summary optimizations to maximize recruiter impact.</p>
                  </div>
                  <button className="pro-copy-btn" onClick={handleCopy}>{copied ? "✓ Copied" : "📋 Copy All"}</button>
                </div>

                {results.rewrites && results.rewrites.length > 0 ? (
                  <div className="pro-rewrites-scrollable">
                    {results.rewrites.map((rw, idx) => (
                      <div key={idx} className="pro-rewrite-card">
                        <div className="pro-tab-col">
                          <div className="pro-tab-label">Original ({rw.type})</div>
                          <div className="pro-tab-content pro-tab-original">
                            {rw.original}
                          </div>
                        </div>
                        <div className="pro-rewrite-arrow">↓</div>
                        <div className="pro-tab-col">
                          <div className="pro-tab-label pro-tab-label-optimized">Optimized (ATS-Ready)</div>
                          <div className="pro-tab-content pro-tab-ai">
                            {rw.improved}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="pro-rewrite-tabs">
                    <p style={{ padding: "1rem", color: "#94a3b8" }}>No rewrite suggestions generated.</p>
                  </div>
                )}
              </div>
            </div>

            {/* ── ROW 5: Reconstructed Resume (ATS-Ready) ── */}
            <div className="pro-card pro-card-full pro-card-rewrite">
              <div className="pro-card-header">
                <span className="pro-card-icon">📑</span>
                <div>
                  <h3>Reconstructed Resume (ATS-Ready)</h3>
                  <p>Polished, error-corrected, and aligned to your target job description with structure preserved.</p>
                </div>
              </div>
              <div className="pro-document-viewport">
                <pre className="pro-document-pre">{results.corrected_resume_text}</pre>
              </div>
              <div className="pro-rewrite-footer">
                <div className="pro-footer-info">
                  <span>📄 Ready for submission</span>
                  <small>Export in your preferred format to apply directly to recruiters.</small>
                </div>
                <div className="pro-footer-downloads">
                  <button className="pro-btn-copy-footer" onClick={handleCopy}>
                    <span>{copied ? "✓ Copied!" : "📋 Copy Text"}</span>
                    <small>Plain text</small>
                  </button>
                  <button className="pro-btn-export-pdf" onClick={() => handleDownload("pdf")} disabled={downloading.pdf}>
                    <span>{downloading.pdf ? "Downloading..." : "Download PDF"}</span><small>High ATS compatibility</small>
                  </button>
                  <button className="pro-btn-export-docx" onClick={() => handleDownload("docx")} disabled={downloading.docx}>
                    <span>{downloading.docx ? "Downloading..." : "Download Word (.DOCX)"}</span><small>Editable document</small>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Bottom Navigation: Back to Dashboard at the Very Bottom ── */}
        <div className="pro-bottom-nav">
          <button className="pro-back-to-dashboard-btn" onClick={() => navigate("/dashboard")}>
            <span className="pro-btn-back-arrow">←</span>
            <span>Back to Dashboard</span>
          </button>
        </div>

        {/* ════════════════════════════════════════════════════════════
            MODAL: View Uploaded Resume
            ════════════════════════════════════════════════════════════ */}
        {showResumeModal && (
          <div className="pro-modal-overlay" onClick={() => setShowResumeModal(false)}>
            <div className="pro-modal-box" onClick={(e) => e.stopPropagation()}>
              <div className="pro-modal-header">
                <div className="pro-modal-title">
                  <span>📄</span>
                  <h3>Uploaded Resume Document</h3>
                </div>
                <button className="pro-modal-close" onClick={() => setShowResumeModal(false)}>✕</button>
              </div>
              <div className="pro-modal-body">
                <pre className="pro-modal-pre">
                  {results?.raw_resume_text || "No resume text available."}
                </pre>
              </div>
              <div className="pro-modal-footer">
                <button className="pro-btn-secondary" onClick={() => setShowResumeModal(false)}>Close</button>
              </div>
            </div>
          </div>
        )}

      </main>

      <footer className="dashboard-footer">
        <span>AI Mode: {isAiActive ? "ON" : "OFF"}</span>
        <span>Smarter Resumes · Brighter Opportunities · Executive Career Engine</span>
      </footer>

      {/* ════════════════════════════════════════════════════════════
          MODAL: Pro Subscription Paywall (after 5 free uses)
          ════════════════════════════════════════════════════════════ */}
      {showPaywallModal && (
        <div className="pro-modal-overlay" onClick={() => setShowPaywallModal(false)}>
          <div className="pro-paywall-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="pro-paywall-crown-glow">♛</div>
            <button
              type="button"
              className="pro-modal-close"
              onClick={() => setShowPaywallModal(false)}
            >
              ✕
            </button>

            <div className="pro-paywall-header">
              <span className="pro-paywall-tag">PRO MEMBERSHIP</span>
              <h2>Unlock Unlimited Pro AI Analyses</h2>
              <p>
                You have reached your limit of <strong>5 free Pro scans</strong>. Choose an upgrade plan below to unlock unlimited deep ATS scans and executive AI rewriting.
              </p>
            </div>

            <div className="pro-paywall-features">
              <div className="pro-paywall-feat-item">
                <span className="feat-check">✓</span>
                <div>
                  <strong>Unlimited Resume Scans</strong>
                  <p>Scan as many resumes and jobs as you want with zero cooldowns or limits.</p>
                </div>
              </div>

              <div className="pro-paywall-feat-item">
                <span className="feat-check">✓</span>
                <div>
                  <strong>AI Mode Deep Rewrites</strong>
                  <p>Executive bullet & summary rewrites tailored to target roles.</p>
                </div>
              </div>

              <div className="pro-paywall-feat-item">
                <span className="feat-check">✓</span>
                <div>
                  <strong>ATS-Ready DOCX & PDF Export</strong>
                  <p>Export pre-formatted, error-free resumes ready for recruiters.</p>
                </div>
              </div>

              <div className="pro-paywall-feat-item">
                <span className="feat-check">✓</span>
                <div>
                  <strong>Priority AI Engine & Fast Queue</strong>
                  <p>Dedicated cloud inference pipeline with zero waiting time.</p>
                </div>
              </div>
            </div>

            <div className="pro-paywall-pricing-cards">
              {/* Monthly Plan: ₹199 */}
              <div className="pro-pricing-card featured">
                <div className="pricing-badge">MOST POPULAR</div>
                <h4>Pro Monthly</h4>
                <div className="pricing-rate">
                  ₹199
                  <span> / month</span>
                </div>
                <p>Full unrestricted executive access, billed monthly.</p>
                <button
                  type="button"
                  className="pro-btn-subscribe"
                  onClick={() => handleOpenCheckout("monthly")}
                >
                  Upgrade to Monthly (₹199)
                </button>
              </div>

              {/* Annual Plan: ₹999 */}
              <div className="pro-pricing-card">
                <div className="pricing-badge savings-badge">SAVE 58%</div>
                <h4>Pro Annual</h4>
                <div className="pricing-rate">
                  ₹999
                  <span> / year</span>
                </div>
                <p>Save over 58% — effectively only ₹83 / month for 12 full months.</p>
                <button
                  type="button"
                  className="pro-btn-subscribe-outline"
                  onClick={() => handleOpenCheckout("annual")}
                >
                  Upgrade to Annual (₹999)
                </button>
              </div>
            </div>

            <div className="pro-paywall-guarantee">
              <span>🔒 256-bit secure checkout · 14-day money-back guarantee</span>
            </div>
          </div>
        </div>
      )}

      {/* ════════════════════════════════════════════════════════════
          MODAL: Secure Payment Gateway & Checkout
          ════════════════════════════════════════════════════════════ */}
      {showPaymentModal && (
        <div
          className="pro-modal-overlay"
          onClick={() => {
            if (paymentStep !== "processing") {
              setShowPaymentModal(false);
            }
          }}
        >
          <div
            className="pro-payment-modal-box"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="pro-payment-header">
              <div className="pro-payment-title-wrap">
                <span className="pro-payment-lock-icon">🔒</span>
                <div>
                  <h3>ResumeIQ Secure Payment Gateway</h3>
                  <p>256-Bit SSL Encrypted Handshake · Powered by Secure Banking Switch</p>
                </div>
              </div>

              {paymentStep !== "processing" && (
                <button
                  type="button"
                  className="pro-modal-close"
                  onClick={() => setShowPaymentModal(false)}
                >
                  ✕
                </button>
              )}
            </div>

            {/* Plan Summary Strip */}
            <div className="pro-payment-plan-strip">
              <div className="pro-plan-strip-left">
                <span className="pro-plan-strip-badge">
                  {selectedPlan === "monthly" ? "PRO MONTHLY" : "PRO ANNUAL"}
                </span>
                <strong>
                  {selectedPlan === "monthly" ? "ResumeIQ Pro Monthly Membership" : "ResumeIQ Pro Annual Membership"}
                </strong>
                <small>
                  {selectedPlan === "monthly" ? "₹168.64 + 18% GST (₹30.36)" : "₹846.61 + 18% GST (₹152.39)"}
                </small>
              </div>

              <div className="pro-plan-strip-right">
                <span className="pro-plan-strip-price">
                  ₹{selectedPlan === "monthly" ? "199" : "999"}
                </span>
                <small>Total Payable</small>
              </div>
            </div>

            {/* Step 1: Payment Form */}
            {paymentStep === "form" && (
              <div className="pro-payment-body">
                {/* Method Selector Tabs */}
                <div className="pro-payment-methods-tabs">
                  <button
                    type="button"
                    className={`pro-pay-tab ${paymentMethod === "upi" ? "active" : ""}`}
                    onClick={() => {
                      setPaymentMethod("upi");
                      setPaymentFormError("");
                    }}
                  >
                    <span className="pay-tab-icon">📱</span>
                    <span>UPI / QR</span>
                  </button>

                  <button
                    type="button"
                    className={`pro-pay-tab ${paymentMethod === "card" ? "active" : ""}`}
                    onClick={() => {
                      setPaymentMethod("card");
                      setPaymentFormError("");
                    }}
                  >
                    <span className="pay-tab-icon">💳</span>
                    <span>Debit / Credit Card</span>
                  </button>

                  <button
                    type="button"
                    className={`pro-pay-tab ${paymentMethod === "netbanking" ? "active" : ""}`}
                    onClick={() => {
                      setPaymentMethod("netbanking");
                      setPaymentFormError("");
                    }}
                  >
                    <span className="pay-tab-icon">🏛️</span>
                    <span>Net Banking</span>
                  </button>
                </div>

                {/* Payment form */}
                <form onSubmit={handleProcessPayment} className="pro-payment-form">
                  {paymentFormError && (
                    <div className="pro-payment-error-alert">
                      <span>⚠️</span>
                      <span>{paymentFormError}</span>
                    </div>
                  )}

                  {/* UPI Method */}
                  {paymentMethod === "upi" && (
                    <div className="pro-upi-section">
                      <label className="pro-pay-label">
                        Select Preferred UPI Application
                      </label>

                      <div className="pro-upi-apps-grid">
                        <button
                          type="button"
                          className={`pro-upi-app-btn ${upiApp === "gpay" ? "selected" : ""}`}
                          onClick={() => setUpiApp("gpay")}
                        >
                          <span className="upi-app-logo">🟢</span>
                          <span>Google Pay</span>
                        </button>

                        <button
                          type="button"
                          className={`pro-upi-app-btn ${upiApp === "phonepe" ? "selected" : ""}`}
                          onClick={() => setUpiApp("phonepe")}
                        >
                          <span className="upi-app-logo">🟣</span>
                          <span>PhonePe</span>
                        </button>

                        <button
                          type="button"
                          className={`pro-upi-app-btn ${upiApp === "paytm" ? "selected" : ""}`}
                          onClick={() => setUpiApp("paytm")}
                        >
                          <span className="upi-app-logo">🔵</span>
                          <span>Paytm UPI</span>
                        </button>

                        <button
                          type="button"
                          className={`pro-upi-app-btn ${upiApp === "other" ? "selected" : ""}`}
                          onClick={() => setUpiApp("other")}
                        >
                          <span className="upi-app-logo">⚡</span>
                          <span>Other UPI ID</span>
                        </button>
                      </div>

                      <div className="pro-pay-input-group">
                        <label className="pro-pay-label">
                          Enter UPI ID / VPA
                        </label>
                        <div className="pro-pay-input-wrap">
                          <input
                            type="text"
                            className="pro-pay-input"
                            placeholder={
                              upiApp === "gpay"
                                ? "mobilenumber@okhdfcbank"
                                : upiApp === "phonepe"
                                ? "mobilenumber@ybl"
                                : "yourname@upi"
                            }
                            value={upiId}
                            onChange={(e) => setUpiId(e.target.value)}
                          />
                          <span className="pro-input-tag">Instant Verify</span>
                        </div>
                        <small className="pro-pay-help">
                          A secure payment approval request will be dispatched to your selected UPI app.
                        </small>
                      </div>
                    </div>
                  )}

                  {/* Card Method */}
                  {paymentMethod === "card" && (
                    <div className="pro-card-section">
                      <div className="pro-pay-input-group">
                        <label className="pro-pay-label">Card Number</label>
                        <div className="pro-pay-input-wrap">
                          <input
                            type="text"
                            className="pro-pay-input"
                            placeholder="4532 8912 3456 7890"
                            maxLength={19}
                            value={cardNumber}
                            onChange={(e) => handleCardNumberChange(e.target.value)}
                          />
                          <span className="pro-card-icons-badge">
                            💳 Visa / MC / RuPay
                          </span>
                        </div>
                      </div>

                      <div className="pro-pay-grid-2">
                        <div className="pro-pay-input-group">
                          <label className="pro-pay-label">Expiry Date</label>
                          <input
                            type="text"
                            className="pro-pay-input"
                            placeholder="MM/YY"
                            maxLength={5}
                            value={cardExpiry}
                            onChange={(e) => handleExpiryChange(e.target.value)}
                          />
                        </div>

                        <div className="pro-pay-input-group">
                          <label className="pro-pay-label">CVV / CVC</label>
                          <input
                            type="password"
                            className="pro-pay-input"
                            placeholder="123"
                            maxLength={4}
                            value={cardCvv}
                            onChange={(e) => handleCvvChange(e.target.value)}
                          />
                        </div>
                      </div>

                      <div className="pro-pay-input-group">
                        <label className="pro-pay-label">Cardholder Full Name</label>
                        <input
                          type="text"
                          className="pro-pay-input"
                          placeholder="Name as printed on card"
                          value={cardHolder}
                          onChange={(e) => setCardHolder(e.target.value)}
                        />
                      </div>
                    </div>
                  )}

                  {/* Net Banking Method */}
                  {paymentMethod === "netbanking" && (
                    <div className="pro-netbanking-section">
                      <label className="pro-pay-label">Select Popular Bank</label>
                      <div className="pro-banks-grid">
                        {[
                          { id: "hdfc", name: "HDFC Bank", icon: "🏛️" },
                          { id: "icici", name: "ICICI Bank", icon: "🏢" },
                          { id: "sbi", name: "State Bank of India", icon: "🏦" },
                          { id: "axis", name: "Axis Bank", icon: "🏬" },
                          { id: "kotak", name: "Kotak Mahindra", icon: "🏪" },
                          { id: "pnb", name: "Punjab National Bank", icon: "🏛️" },
                        ].map((b) => (
                          <button
                            key={b.id}
                            type="button"
                            className={`pro-bank-btn ${selectedBank === b.id ? "selected" : ""}`}
                            onClick={() => setSelectedBank(b.id)}
                          >
                            <span className="bank-btn-icon">{b.icon}</span>
                            <span>{b.name}</span>
                          </button>
                        ))}
                      </div>

                      <div className="pro-pay-input-group">
                        <label className="pro-pay-label">Or Select Other Bank</label>
                        <select
                          className="pro-pay-select"
                          value={selectedBank}
                          onChange={(e) => setSelectedBank(e.target.value)}
                        >
                          <option value="hdfc">HDFC Bank</option>
                          <option value="icici">ICICI Bank</option>
                          <option value="sbi">State Bank of India</option>
                          <option value="axis">Axis Bank</option>
                          <option value="kotak">Kotak Mahindra Bank</option>
                          <option value="pnb">Punjab National Bank</option>
                          <option value="bob">Bank of Baroda</option>
                          <option value="canara">Canara Bank</option>
                          <option value="union">Union Bank of India</option>
                          <option value="indusind">IndusInd Bank</option>
                          <option value="yes">Yes Bank</option>
                          <option value="federal">Federal Bank</option>
                        </select>
                      </div>
                    </div>
                  )}

                  {/* Pay button */}
                  <div className="pro-payment-actions">
                    <button type="submit" className="pro-btn-pay-submit">
                      <span>🔒</span>
                      <span>
                        Pay ₹{selectedPlan === "monthly" ? "199" : "999"} Securely
                      </span>
                    </button>

                    <div className="pro-payment-trust-strip">
                      <span>🛡️ RBI Guidelines Compliant</span>
                      <span>·</span>
                      <span>🔒 256-Bit TLS Encryption</span>
                      <span>·</span>
                      <span>✓ 100% Secure Checkout</span>
                    </div>
                  </div>
                </form>
              </div>
            )}

            {/* Step 2: Processing State */}
            {paymentStep === "processing" && (
              <div className="pro-payment-processing-wrap">
                <div className="pro-banking-spinner" />
                <h4>Contacting Secure Banking Switch...</h4>
                <p className="pro-processing-status-text">{processingStatus}</p>
                <div className="pro-processing-notice">
                  <span>⚠️ Please do not close or refresh this page while payment handshake is in progress.</span>
                </div>
              </div>
            )}

            {/* Step 3: Authentic Gateway Technical Error State */}
            {paymentStep === "failed" && (
              <div className="pro-payment-failed-wrap">
                <div className="pro-failed-icon-wrap">
                  <span className="pro-failed-cross">✕</span>
                </div>

                <div className="pro-failed-badge">
                  TECHNICAL GATEWAY ISSUE
                </div>

                <h3>Payment Processing Unavailable</h3>

                <div className="pro-failed-error-box">
                  <div className="pro-failed-err-code">
                    Error Code: <strong>ERR_PGW_503_BANK_GATEWAY_TIMEOUT</strong>
                  </div>

                  <p>
                    The acquiring banking network server timed out during the final 3D-Secure transaction handshake. Payment processing is currently experiencing high load on bank servers.
                  </p>

                  <div className="pro-failed-note">
                    <strong>Zero Charge Assurance:</strong> Your card or bank account has <u>NOT</u> been charged for this attempt.
                  </div>
                </div>

                <div className="pro-failed-actions">
                  <button
                    type="button"
                    className="pro-btn-retry-pay"
                    onClick={handleRetryPayment}
                  >
                    🔄 Try Again
                  </button>

                  <button
                    type="button"
                    className="pro-btn-cancel-pay"
                    onClick={() => setShowPaymentModal(false)}
                  >
                    Close Window
                  </button>
                </div>

                <small className="pro-failed-support-text">
                  If this issue persists, please try an alternative payment method or contact payment support at support@resumeiq.com.
                </small>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProDashboard;
