function ModeCard({
  type = "normal",
  title,
  subtitle,
  active = false,
  comingSoon = false,
}) {
  const normal = type === "normal";

  return (
    <article
      className={`mode-card ${
        normal ? "mode-card-normal" : "mode-card-pro"
      }`}
    >
      <div
        className={`mode-card-icon ${
          normal ? "normal" : "pro"
        }`}
      >
        {normal ? "◎" : "♛"}
      </div>

      <div className="mode-card-content">
        <div className="mode-card-main">
          <div>
            <h2>{title}</h2>
            <p>{subtitle}</p>
          </div>

          {active && (
            <span className="mode-status active">
              <i />
              ACTIVE
            </span>
          )}

          {comingSoon && (
            <span className="mode-status coming">
              Coming Soon
            </span>
          )}
        </div>
      </div>
    </article>
  );
}

export default ModeCard;


