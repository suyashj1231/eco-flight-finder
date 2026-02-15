import { useState, useEffect } from 'react';
import './Modal.css';

export default function SearchHistory({ token, onClose, onClear }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const response = await fetch('/users/history', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (!response.ok) throw new Error("Failed to fetch history");
            const data = await response.json();
            // Sort by timestamp descending
            const sortedData = data.sort((a, b) => new Date(b.search_timestamp) - new Date(a.search_timestamp));
            setHistory(sortedData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleString();
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>Your Search History</h3>
                    <button onClick={onClose} className="close-btn">&times;</button>
                </div>

                <div className="modal-body">
                    {loading && <p>Loading history...</p>}
                    {error && <p style={{ color: '#e74c3c' }}>{error}</p>}

                    {!loading && !error && history.length === 0 && (
                        <p style={{ color: '#7f8c8d' }}>No search history found.</p>
                    )}

                    {!loading && !error && history.map((item) => (
                        <div key={item.id} className="history-item">
                            <div className="history-header">
                                <strong>{item.departure_iata} ➔ {item.arrival_iata}</strong>
                                <span className="history-timestamp">{formatDate(item.search_timestamp)}</span>
                            </div>
                            <div className="history-details">
                                Departure: {item.departure_date}
                                {item.return_date && ` | Return: ${item.return_date}`}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="modal-footer">
                    {history.length > 0 && (
                        <button
                            onClick={async () => {
                                if (window.confirm("Clear all search history?")) {
                                    try {
                                        const res = await fetch('/users/history', {
                                            method: 'DELETE',
                                            headers: { 'Authorization': `Bearer ${token}` }
                                        });
                                        if (res.ok) {
                                            setHistory([]);
                                            if (onClear) onClear();
                                        }
                                    } catch (e) { console.error(e); }
                                }
                            }}
                            className="btn-danger"
                            style={{ marginRight: 'auto' }}
                        >
                            Clear History
                        </button>
                    )}
                    <button onClick={onClose} className="btn-secondary">Close</button>
                    <button className="btn-primary" onClick={fetchHistory}>Refresh</button>
                </div>
            </div>
        </div>
    );
}
