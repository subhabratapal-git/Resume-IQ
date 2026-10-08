function ScoreCard({
  type = "ats",
  score = 0,
  title,
  description,
}) {
  const numericScore = Number(score) || 0;

  const normalizedScore = Math.max(
    0,
    Math.min(100, numericScore)
  );

  return (
    <article
      className={`dashboard-score-card score-${type}`}
    >
      <div
        className="dashboard-score-ring"
        style={{
          "--score-angle": `${normalizedScore * 3.6}deg`,
        }}
      >
        <div className="dashboard-score-ring-inner">
          <strong>
            {type === "ats"
              ? Math.round(normalizedScore)
              : `${Math.round(normalizedScore)}%`}
          </strong>
        </div>
      </div>

      <div className="dashboard-score-copy">
        <h3>{title}</h3>

        <p>{description}</p>
      </div>
    </article>
  );
}

export default ScoreCard;


