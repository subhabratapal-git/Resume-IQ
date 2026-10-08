import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Brand from "../components/Brand";
import ThemeToggle from "../components/ThemeToggle";
import ResumeArtwork from "../components/ResumeArtwork";
import ModeCard from "../components/ModeCard";
import ResumeAnalyzer from "../components/ResumeAnalyzer";
import ProfileMenu from "../components/ProfileMenu";

import { logoutUser } from "../services/authApi";
import { getAnalysisHistory } from "../services/resumeApi";

import "../styles/theme.css";
import "../styles/dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("resumeiq-theme");

    return savedTheme === "light"
      ? "light"
      : "color";
  });

  const [analysisCount, setAnalysisCount] = useState(0);

  const [analysisActive, setAnalysisActive] = useState(false);

  const [user] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem("resumeiq-user") || "null"
      );
    } catch {
      return null;
    }
  });

  const firstName =
    user?.full_name?.split(" ")[0] || "User";

  const proUsesRemaining =
    user?.pro_uses_remaining ?? 5;

  const fetchAnalysisStats = async () => {
    try {
      const data = await getAnalysisHistory(0);
      if (data && typeof data.total === "number") {
        setAnalysisCount(data.total);
      }
    } catch (err) {
      // Ignore network errors on unauthenticated or offline state
    }
  };

  useEffect(() => {
    fetchAnalysisStats();
  }, []);

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

  const handleLogout = () => {
    logoutUser();

    navigate("/", {
      replace: true,
    });
  };

  const handleAnalysisSuccess = () => {
    fetchAnalysisStats();
  };

  const handleAnalysisStateChange = (active) => {
    setAnalysisActive(active);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();

    if (hour < 12) {
      return "Good morning";
    }

    if (hour < 17) {
      return "Good afternoon";
    }

    return "Good evening";
  };

  return (
    <div
      className={`app-theme dashboard-page ${
        analysisActive
          ? "dashboard-result-active"
          : ""
      }`}
      data-theme={theme}
    >
      <div className="dashboard-background">
        <div className="dashboard-grid-background" />

        <div className="dashboard-glow dashboard-glow-left" />
        <div className="dashboard-glow dashboard-glow-right" />

        <div className="dashboard-wave dashboard-wave-one" />
        <div className="dashboard-wave dashboard-wave-two" />
      </div>

      <header className="main-header dashboard-header">
        <div className="header-container">
          <Brand />

          <div className="dashboard-header-actions">
            <ThemeToggle
              theme={theme}
              setTheme={setTheme}
            />

            <div className="dashboard-header-separator" />

            <ProfileMenu
              user={user}
              analysisCount={analysisCount}
              proUsesRemaining={proUsesRemaining}
              onLogout={handleLogout}
            />
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-top">
          <div className="dashboard-top-left">
            <div className="dashboard-greeting">
              <h1>
                {getGreeting()},{" "}
                <span className="gradient-text">
                  {firstName}
                </span>
              </h1>

              <p>
                Optimize your resume for the role you want
              </p>
            </div>

            <div className="dashboard-mode-row">
              <ModeCard
                type="normal"
                title="Normal Mode"
                subtitle="ATS + Job Matching"
                active
              />

              <div onClick={() => navigate('/pro-dashboard')} style={{ cursor: 'pointer' }}>
                <ModeCard
                  type="pro"
                  title="Pro Mode"
                  subtitle="ML-powered insights"
                />
              </div>
            </div>
          </div>

          <div className="dashboard-top-art">
            <div className="dashboard-art-copy">
              <span>BETTER</span>
              <span>RESUMES</span>
              <span>BRIGHTER</span>
              <span>FUTURES</span>
            </div>

            <ResumeArtwork variant="dashboard" />
          </div>
        </section>

        <ResumeAnalyzer
          onAnalysisSuccess={handleAnalysisSuccess}
          onAnalysisStateChange={handleAnalysisStateChange}
        />

        <footer className="dashboard-footer">
          <span>ResumeIQ</span>

          <span>
            Smarter Resumes · Brighter Opportunities
          </span>
        </footer>
      </main>
    </div>
  );
}

export default Dashboard;

