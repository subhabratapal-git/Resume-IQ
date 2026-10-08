import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { changePassword } from "../services/authApi";
import { getAnalysisHistory } from "../services/resumeApi";

function ChangePasswordModal({ isOpen, onClose }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!currentPassword) {
      setError("Please enter your current password.");
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      setError("New password must be at least 6 characters long.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return;
    }

    try {
      setLoading(true);
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setSuccess("Password changed successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => {
        setSuccess("");
        onClose();
      }, 1400);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to change password. Please check your current password."
      );
    } finally {
      setLoading(false);
    }
  };

  return createPortal(
    <div className="resumeiq-modal-backdrop" onClick={onClose}>
      <div
        className="resumeiq-modal-window"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="resumeiq-modal-header">
          <div className="modal-title-with-icon">
            <span className="modal-icon">⚿</span>
            <div>
              <h3>Change Password</h3>
              <p>Update your account security password</p>
            </div>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        {error && <div className="modal-alert-error">{error}</div>}
        {success && <div className="modal-alert-success">✓ {success}</div>}

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="modal-form-group">
            <label>Current Password</label>
            <div className="modal-input-wrapper">
              <input
                type={showCurrentPassword ? "text" : "password"}
                placeholder="Enter current password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="pwd-toggle-btn"
                onClick={() => setShowCurrentPassword((prev) => !prev)}
                title={showCurrentPassword ? "Hide password" : "Show password"}
              >
                {showCurrentPassword ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          <div className="modal-form-group">
            <label>New Password (min 6 characters)</label>
            <div className="modal-input-wrapper">
              <input
                type={showNewPassword ? "text" : "password"}
                placeholder="Enter new password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="pwd-toggle-btn"
                onClick={() => setShowNewPassword((prev) => !prev)}
                title={showNewPassword ? "Hide password" : "Show password"}
              >
                {showNewPassword ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          <div className="modal-form-group">
            <label>Confirm New Password</label>
            <div className="modal-input-wrapper">
              <input
                type={showNewPassword ? "text" : "password"}
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="modal-btn-cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="modal-btn-submit"
              disabled={loading}
            >
              {loading ? "Updating..." : "Update Password"}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}

function AnalysisHistoryModal({ isOpen, onClose }) {
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);
  const [bestScore, setBestScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await getAnalysisHistory(0);
      setHistory(data.items || []);
      setTotal(data.total || 0);
      setBestScore(data.best_score ?? null);
    } catch (err) {
      setError("Failed to load analysis history.");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const formatDate = (isoString) => {
    if (!isoString) return "";
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  return createPortal(
    <div className="resumeiq-modal-backdrop" onClick={onClose}>
      <div
        className="resumeiq-modal-window history-modal-window"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="resumeiq-modal-header">
          <div className="modal-title-with-icon">
            <span className="modal-icon">📜</span>
            <div>
              <h3>Resume Analysis History</h3>
              <p>Your previous resume optimization analyses</p>
            </div>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="history-summary-pills">
          <div className="history-pill">
            <span>Total Analyses:</span>
            <strong>{total}</strong>
          </div>
          {bestScore !== null && (
            <div className="history-pill highlight">
              <span>Best ATS Score:</span>
              <strong>{Math.round(bestScore)}%</strong>
            </div>
          )}
        </div>

        {error && <div className="modal-alert-error">{error}</div>}

        {loading ? (
          <div className="history-loading-state">
            <div className="history-spinner" />
            <span>Loading your analysis history...</span>
          </div>
        ) : history.length === 0 ? (
          <div className="history-empty-state">
            <span className="empty-icon">📁</span>
            <h4>No Resume Analyses Yet</h4>
            <p>Upload a resume and job description to perform your first analysis!</p>
          </div>
        ) : (
          <div className="history-list-container">
            {history.map((item) => {
              const score = Math.round(item.ats_score);
              const scoreBadgeClass =
                score >= 75
                  ? "score-badge-high"
                  : score >= 50
                  ? "score-badge-med"
                  : "score-badge-low";

              return (
                <div key={item.id} className="history-item-card">
                  <div className="history-item-icon">📄</div>
                  <div className="history-item-body">
                    <div className="history-item-header">
                      <strong className="history-item-filename">
                        {item.filename || "Resume"}
                      </strong>
                      <span className={`history-score-badge ${scoreBadgeClass}`}>
                        {score}% ATS
                      </span>
                    </div>
                    <div className="history-item-footer">
                      <span className="history-item-role">
                        🎯 {item.target_role || "General Analysis"}
                      </span>
                      <span className="history-item-date">
                        🕒 {formatDate(item.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="modal-actions" style={{ justifyContent: "flex-end" }}>
          <button
            type="button"
            className="modal-btn-cancel"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}

function ProfileMenu({
  user,
  analysisCount = 0,
  proUsesRemaining = 5,
  onLogout,
}) {
  const [open, setOpen] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const menuRef = useRef(null);

  const fullName = user?.full_name || "User";
  const email = user?.email || "No email available";
  const firstLetter = fullName.charAt(0).toUpperCase();
  const firstName = fullName.split(" ")[0];

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  return (
    <>
      <div className="profile-menu-wrapper" ref={menuRef}>
        <button
          type="button"
          className="profile-menu-trigger"
          onClick={() => setOpen((current) => !current)}
          aria-expanded={open}
          aria-label="Open profile menu"
        >
          <div className="profile-menu-avatar">{firstLetter}</div>

          <span className="profile-menu-name">{firstName}</span>

          <span className={`profile-menu-chevron ${open ? "open" : ""}`}>
            ⌄
          </span>
        </button>

        {open && (
          <div className="profile-dropdown">
            <div className="profile-dropdown-header">
              <div className="profile-dropdown-avatar">{firstLetter}</div>

              <div className="profile-dropdown-user-info">
                <strong>{fullName}</strong>
                <span>{email}</span>
              </div>
            </div>

            <div className="profile-dropdown-stats">
              <div
                className="profile-stat clickable"
                onClick={() => {
                  setOpen(false);
                  setShowHistoryModal(true);
                }}
                title="Click to view full analysis history"
              >
                <span>Resume Analyses ↗</span>
                <strong>{analysisCount}</strong>
              </div>

              <div className="profile-stat">
                <span>Pro Uses Left</span>
                <strong>{proUsesRemaining}</strong>
              </div>
            </div>

            <div className="profile-dropdown-menu">
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  setShowHistoryModal(true);
                }}
              >
                <span className="profile-menu-item-icon">📜</span>
                <div>
                  <strong>Analysis History</strong>
                  <small>View past resume analysis records</small>
                </div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  setShowPasswordModal(true);
                }}
              >
                <span className="profile-menu-item-icon">⚿</span>
                <div>
                  <strong>Change Password</strong>
                  <small>Update your account password</small>
                </div>
              </button>
            </div>

            <div className="profile-dropdown-footer">
              <button
                type="button"
                className="profile-logout-button"
                onClick={() => {
                  setOpen(false);
                  if (onLogout) {
                    onLogout();
                  }
                }}
              >
                <span>↪</span>
                Logout
              </button>
            </div>
          </div>
        )}
      </div>

      <ChangePasswordModal
        isOpen={showPasswordModal}
        onClose={() => setShowPasswordModal(false)}
      />

      <AnalysisHistoryModal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
      />
    </>
  );
}

export default ProfileMenu;
