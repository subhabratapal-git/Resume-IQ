import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Brand from "../components/Brand";
import ThemeToggle from "../components/ThemeToggle";
import ResumeArtwork from "../components/ResumeArtwork";

import {
  loginUser,
  registerUser,
  saveAuth,
} from "../services/authApi";
import { getAnalysisTotal } from "../services/resumeApi";

import "../styles/theme.css";
import "../styles/login.css";

function Login() {
  const navigate = useNavigate();

  const [mode, setMode] = useState("login");

  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("resumeiq-theme");

    return savedTheme === "light" ? "light" : "color";
  });

  const [totalAnalyses, setTotalAnalyses] = useState(null);

  const [fullName, setFullName] = useState("");

  const [email, setEmail] = useState(() => {
    return (
      localStorage.getItem("resumeiq-remembered-email") || ""
    );
  });

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [rememberMe, setRememberMe] = useState(() => {
    return Boolean(
      localStorage.getItem("resumeiq-remembered-email")
    );
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      theme
    );

    localStorage.setItem(
      "resumeiq-theme",
      theme
    );
  }, [theme]);

  useEffect(() => {
    let isMounted = true;

    getAnalysisTotal()
      .then((data) => {
        if (isMounted && data && typeof data.total_analyses === "number") {
          setTotalAnalyses(data.total_analyses);
        }
      })
      .catch(() => {
        // Fallback gracefully
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleModeChange = (nextMode) => {
    setMode(nextMode);
    setError("");
    setPassword("");
    setConfirmPassword("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    if (mode === "register") {
      if (!fullName.trim()) {
        setError("Please enter your full name.");
        return;
      }

      if (password.length < 8) {
        setError(
          "Password must contain at least 8 characters."
        );
        return;
      }

      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    try {
      setLoading(true);

      let response;

      if (mode === "login") {
        response = await loginUser({
          email: email.trim(),
          password,
        });
      } else {
        response = await registerUser({
          full_name: fullName.trim(),
          email: email.trim(),
          password,
        });
      }

      saveAuth(response);

      if (rememberMe) {
        localStorage.setItem(
          "resumeiq-remembered-email",
          email.trim()
        );
      } else {
        localStorage.removeItem(
          "resumeiq-remembered-email"
        );
      }

      navigate("/dashboard", {
        replace: true,
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="app-theme login-page"
      data-theme={theme}
    >
      <div className="login-background">
        <div className="login-bg-glow login-bg-glow-left" />
        <div className="login-bg-glow login-bg-glow-right" />

        <div className="login-orbit login-orbit-left" />
        <div className="login-orbit login-orbit-right" />

        <div className="login-star star-1">✦</div>
        <div className="login-star star-2">✦</div>
        <div className="login-star star-3">✦</div>
      </div>

      <header className="main-header login-header">
        <div className="header-container">
          <Brand />

          <ThemeToggle
            theme={theme}
            setTheme={setTheme}
          />
        </div>
      </header>

      <main className="login-layout">
        {/* LEFT SIDE */}

        <section className="login-left">
          <div className="login-copy">
            <p className="login-eyebrow">
              SMART RESUME ANALYSIS
            </p>

            <h1>
              Better Resumes.
              <br />

              <span className="gradient-text">
                More Matches.
              </span>
            </h1>

            <div className="total-analyses-badge">
              <span className="badge-pulse-dot" />
              <span className="badge-icon">✨</span>
              <span>
                <strong>{totalAnalyses !== null ? totalAnalyses.toLocaleString() : "15"}</strong> resumes analyzed globally across all users
              </span>
            </div>

            <p className="login-description">
              Analyze your resume, improve your profile,
              and match with the right opportunities.
            </p>
          </div>

          <div className="login-feature-grid">
            <article className="login-feature-card">
              <div className="feature-icon-shell blue">
                <span>◔</span>
              </div>

              <div>
                <h3>ATS Score</h3>

                <p>
                  See how well your resume
                  <br />
                  passes ATS checks
                </p>
              </div>
            </article>

            <article className="login-feature-card">
              <div className="feature-icon-shell green">
                <span>♟</span>
              </div>

              <div>
                <h3>Skill Match</h3>

                <p>
                  Compare skills with
                  <br />
                  job requirements
                </p>
              </div>
            </article>

            <article className="login-feature-card">
              <div className="feature-icon-shell purple">
                <span>⌕</span>
              </div>

              <div>
                <h3>Keyword Analysis</h3>

                <p>
                  Find missing keywords
                  <br />
                  and suggestions
                </p>
              </div>
            </article>

            <article className="login-feature-card">
              <div className="feature-icon-shell blue">
                <span>▣</span>
              </div>

              <div>
                <h3>PDF/DOCX Upload</h3>

                <p>
                  Easily upload and analyze
                  <br />
                  your resume
                </p>
              </div>
            </article>

            <article className="login-feature-card">
              <div className="feature-icon-shell green">
                <span>◆</span>
              </div>

              <div>
                <h3>Secure Login</h3>

                <p>
                  Your workspace is private
                  <br />
                  and protected
                </p>
              </div>
            </article>

            <article className="login-feature-card">
              <div className="feature-icon-shell purple">
                <span>▥</span>
              </div>

              <div>
                <h3>Resume Analysis</h3>

                <p>
                  Get detailed insights
                  <br />
                  from your resume
                </p>
              </div>
            </article>
          </div>

          <div className="login-tagline-bottom">
            <span>SAME POTENTIAL.</span>

            <div>
              <span>A BRIGHTER TOMORROW.</span>
              <i />
            </div>
          </div>
        </section>

        {/* CENTER ARTWORK */}

        <section className="login-center-art">
          <ResumeArtwork variant="login" />
        </section>

        {/* RIGHT SIDE */}

        <section className="login-right-panel">
          <div className="login-card">
            <div className="login-card-heading">
              <h2>
                {mode === "login"
                  ? "Welcome to "
                  : "Join "}

                <span>ResumeIQ</span>
              </h2>

              <p>
                {mode === "login"
                  ? "Sign in to analyze your resume and unlock better opportunities."
                  : "Create your account and start improving your resume."}
              </p>

              <div className="login-global-counter-pill">
                <span className="live-dot" />
                <span>Global Analyses: <strong>{totalAnalyses !== null ? totalAnalyses.toLocaleString() : "15"}</strong> resumes optimized</span>
              </div>
            </div>

            <div className="login-tabs">
              <button
                type="button"
                className={
                  mode === "login" ? "active" : ""
                }
                onClick={() =>
                  handleModeChange("login")
                }
              >
                Sign In
              </button>

              <button
                type="button"
                className={
                  mode === "register" ? "active" : ""
                }
                onClick={() =>
                  handleModeChange("register")
                }
              >
                Create Account
              </button>
            </div>

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            <form
              className="login-form"
              onSubmit={handleSubmit}
            >
              {mode === "register" && (
                <div className="login-field">
                  <label>Full Name</label>

                  <div className="login-input">
                    <span className="input-icon">○</span>

                    <input
                      type="text"
                      placeholder="Enter your full name"
                      value={fullName}
                      onChange={(event) =>
                        setFullName(event.target.value)
                      }
                    />
                  </div>
                </div>
              )}

              <div className="login-field">
                <label>Email Address</label>

                <div className="login-input">
                  <span className="input-icon">✉</span>

                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                  />
                </div>
              </div>

              <div className="login-field">
                <label>Password</label>

                <div className="login-input">
                  <span className="input-icon">▣</span>

                  <input
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Enter your password"
                    value={password}
                    autoComplete={
                      mode === "login"
                        ? "current-password"
                        : "new-password"
                    }
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                  />

                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() =>
                      setShowPassword(
                        (current) => !current
                      )
                    }
                  >
                    {showPassword ? "Hide" : "◉"}
                  </button>
                </div>
              </div>

              {mode === "register" && (
                <div className="login-field">
                  <label>
                    Confirm Password
                  </label>

                  <div className="login-input">
                    <span className="input-icon">▣</span>

                    <input
                      type={
                        showPassword
                          ? "text"
                          : "password"
                      }
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      autoComplete="new-password"
                      onChange={(event) =>
                        setConfirmPassword(
                          event.target.value
                        )
                      }
                    />
                  </div>
                </div>
              )}

              <div className="login-options">
                <label className="remember-option">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(event) =>
                      setRememberMe(
                        event.target.checked
                      )
                    }
                  />

                  <span>Remember me</span>
                </label>

                {mode === "login" && (
                  <button
                    type="button"
                    className="forgot-password"
                    onClick={() =>
                      setError(
                        "Password reset is not available yet."
                      )
                    }
                  >
                    Forgot password?
                  </button>
                )}
              </div>

              <button
                type="submit"
                className="login-submit"
                disabled={loading}
              >
                {loading ? (
                  "Please wait..."
                ) : (
                  <>
                    <span>
                      {mode === "login"
                        ? "Enter ResumeIQ"
                        : "Create Account"}
                    </span>

                    <span className="submit-arrow">
                      →
                    </span>
                  </>
                )}
              </button>
            </form>

            <div className="login-divider">
              <span />
              <p>or</p>
              <span />
            </div>

            <div className="login-bottom-link">
              {mode === "login" ? (
                <>
                  <span>
                    Don't have an account?
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      handleModeChange("register")
                    }
                  >
                    Create one
                  </button>
                </>
              ) : (
                <>
                  <span>
                    Already have an account?
                  </span>

                  <button
                    type="button"
                    onClick={() =>
                      handleModeChange("login")
                    }
                  >
                    Sign in
                  </button>
                </>
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="login-footer">
        <span>
          © 2026 ResumeIQ. All rights reserved.
        </span>

        <div className="login-footer-center">
          <i />
          <span>
            SMARTER RESUMES · BRIGHTER OPPORTUNITIES.
          </span>
          <i />
        </div>

        <div className="login-footer-links">
          <span>Privacy</span>
          <span>Terms</span>
          <span>Support</span>
        </div>
      </footer>
    </div>
  );
}

export default Login;


