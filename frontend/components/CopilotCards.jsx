export default function CopilotCards({ recommendation = {} }) {
  return (
    <div className="copilot">
      <div className="recommendation">
        <small>PRIMARY ACTION</small>
        <h2>{recommendation.primary_action || "No recommendation"}</h2>
        <div className="confidence">
          <div className="confidence-bar">
            <div style={{ width: `${recommendation.survival_prob || 0}%` }} />
          </div>
          <span>{recommendation.survival_prob || 0}% survival confidence</span>
        </div>
      </div>
      <div className="explanation">
        <small>DIAGNOSTIC CONTEXT</small>
        <p>{recommendation.explanation || "Awaiting diagnostic context."}</p>
      </div>
    </div>
  );
}
