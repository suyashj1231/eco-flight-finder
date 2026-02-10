export default function Results({ results }) {
  if (!results || results.length === 0) {
    return <div style={{ padding: "20px" }}>No results yet. Try searching!</div>;
  }

  return (
    <div style={{ padding: "20px", maxWidth: "800px" }}>
      <h2>Recommended Flights</h2>
      <div>
        {results.map((item, idx) => (
          <div
            key={idx}
            style={{
              border: "1px solid #ddd",
              borderRadius: "4px",
              padding: "15px",
              marginBottom: "10px",
              backgroundColor: item.filtered_out ? "#fee" : "#efe",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div>
                <h3>{item.flight?.flight_number || "N/A"}</h3>
                <p style={{ margin: "5px 0" }}>
                  <strong>Airline:</strong> {item.flight?.airline || "Unknown"}
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Distance:</strong> {item.flight?.distance_km?.toFixed(0) || 0} km
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Duration:</strong> {item.flight?.duration_hours?.toFixed(1) || 0}h
                </p>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "24px", fontWeight: "bold", color: item.flight?.emissions_kg < 300 ? "green" : "red" }}>
                  {item.flight?.emissions_kg?.toFixed(0) || 0} kg CO₂
                </div>
                {item.filtered_out && (
                  <p style={{ color: "red", marginTop: "10px" }}>
                    <strong>Filtered:</strong> {item.filter_reason}
                  </p>
                )}
                {!item.filtered_out && (
                  <p style={{ color: "green", marginTop: "10px" }}>
                    Score: {item.rank_score?.toFixed(3) || 0} (lower is better)
                  </p>
                )}
              </div>
            </div>
            {item.explanation && item.explanation.length > 0 && (
              <p style={{ fontSize: "12px", color: "#666", marginTop: "10px" }}>
                {item.explanation.join(" • ")}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
