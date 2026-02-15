import { useState, useEffect } from 'react';
import './Results.css';

export default function Results({ results, resultsPerPage = 8, onBack }) {
  const outboundList = results.outbound || [];
  const inboundList = results.inbound || [];

  const [outboundPage, setOutboundPage] = useState(1);
  const [inboundPage, setInboundPage] = useState(1);

  useEffect(() => {
    setOutboundPage(1);
    setInboundPage(1);
  }, [results]);

  if (outboundList.length === 0 && inboundList.length === 0) {
    return (
      <div className="results-container">
        <div style={{ marginBottom: '20px' }}>
          <button onClick={onBack} className="btn-back">← Back to Search</button>
        </div>
        <div style={{ textAlign: "center", fontStyle: "italic", marginTop: "20px" }}>No results found.</div>
      </div>
    );
  }

  const formatTime = (isoString) => {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderFlightList = (list, page, setPage, title) => {
    const indexOfLastResult = page * resultsPerPage;
    const indexOfFirstResult = indexOfLastResult - resultsPerPage;
    const currentResults = list.slice(indexOfFirstResult, indexOfLastResult);
    const totalPages = Math.ceil(list.length / resultsPerPage);

    const paginate = (pageNumber) => setPage(pageNumber);

    return (
      <div className="flight-section" style={{ marginBottom: '40px' }}>
        <h3 className="section-title" style={{ color: '#2c3e50', borderBottom: '2px solid #ecf0f1', paddingBottom: '10px', marginBottom: '20px' }}>
          {title} ({list.length})
        </h3>

        <div>
          {currentResults.map((item, idx) => {
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

        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => paginate(page - 1)}
              disabled={page === 1}
              className="page-btn"
            >
              Prev
            </button>
            <span className="page-info">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => paginate(page + 1)}
              disabled={page === totalPages}
              className="page-btn"
            >
              Next
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="results-container">
      <div style={{ marginBottom: '20px' }}>
        <button onClick={onBack} className="btn-back">← Back to Search</button>
      </div>

      {outboundList.length > 0 && renderFlightList(outboundList, outboundPage, setOutboundPage, "Outbound Flights")}
      {inboundList.length > 0 && renderFlightList(inboundList, inboundPage, setInboundPage, "Return Flights")}
    </div>
  );
}
