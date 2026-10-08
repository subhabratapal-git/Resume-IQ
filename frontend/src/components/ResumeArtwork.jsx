function ResumeArtwork({ variant = "login" }) {
  const isDashboard = variant === "dashboard";

  return (
    <div
      className={
        isDashboard
          ? "riq-artwork riq-artwork-dashboard"
          : "riq-artwork riq-artwork-login"
      }
      aria-hidden="true"
    >
      <div className="riq-art-glow" />

      <div className="riq-art-orbit riq-orbit-one" />
      <div className="riq-art-orbit riq-orbit-two" />

      <div className="riq-resume-sheet">
        <div className="riq-resume-profile">
          <div className="riq-profile-icon">
            <span className="riq-profile-head" />
            <span className="riq-profile-body" />
          </div>

          <div className="riq-profile-lines">
            <span />
            <span />
          </div>
        </div>

        <div className="riq-resume-lines">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
      </div>

      <div className="riq-opportunity-card">
        <span className="riq-opportunity-star">✦</span>

        <p>
          Your
          <br />
          Next Opportunity
          <strong>Starts Here</strong>
        </p>
      </div>
    </div>
  );
}

export default ResumeArtwork;


