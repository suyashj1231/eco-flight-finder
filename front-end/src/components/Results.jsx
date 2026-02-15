import './Results.css';

export default function Results({ results }) {
  if (!results || results.length === 0) {
    return <div className="results-container" style={{ textAlign: "center", fontStyle: "italic", marginTop: "20px" }}>No results found.</div>;
  }

  const formatTime = (isoString) => {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="results-container">
      <h2 className="results-header">Recommended Flights</h2>
      <div>
        {results.map((item, idx) => {
          const flight = item.flight;
          const isHighEmissions = flight?.emissions_kg >= 300;

          return (
            <div
              key={idx}
              className={`flight-card ${item.filtered_out ? 'filtered-out' : ''}`}
            >
              <div className="flight-info">
                <div className="airline-name">{flight?.airline || "Unknown Airline"}</div>

                <div className="route-details">
                  <div className="flight-number">{flight?.flight_number || "N/A"}</div>

                  <div>
                    <span className="detail-label">Time:</span>
                    {formatTime(flight?.departure)} - {formatTime(flight?.arrival)}
                  </div>

                  <div>
                    <span className="detail-label">Duration:</span>
                    {flight?.duration_hours?.toFixed(1) || 0}h
                  </div>

                  <div>
                    <span className="detail-label">Distance:</span>
                    {flight?.distance_km?.toFixed(0) || 0} km
                  </div>
                </div>

                {item.filtered_out && (
                  <div className="filter-reason">
                    Reason: {item.filter_reason}
                  </div>
                )}
              </div>

              <div className="emissions-info">
                <div className="co2-amount" style={{ color: isHighEmissions ? '#e74c3c' : '#27ae60' }}>
                  {flight?.emissions_kg?.toFixed(0) || 0}
                </div>
                <div className="co2-label">kg CO₂</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
