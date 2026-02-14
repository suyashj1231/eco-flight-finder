import { useState, useEffect } from 'react';

export default function SearchHistory({ token, onClose }) {
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
        <div style={styles.overlay}>
            <div style={styles.modal}>
                <div style={styles.header}>
                    <h3>Your Search History</h3>
                    <button onClick={onClose} style={styles.closeButton}>&times;</button>
                </div>

                {loading && <p>Loading history...</p>}
                {error && <p style={{ color: 'red' }}>{error}</p>}

                {!loading && !error && history.length === 0 && (
                    <p>No search history found.</p>
                )}

                <div style={styles.list}>
                    {history.map((item) => (
                        <div key={item.id} style={styles.item}>
                            <div style={styles.itemHeader}>
                                <strong>{item.departure_iata} ➔ {item.arrival_iata}</strong>
                                <span style={styles.timestamp}>{formatDate(item.search_timestamp)}</span>
                            </div>
                            <div style={styles.itemDetails}>
                                Departure: {item.departure_date}
                                {item.return_date && ` | Return: ${item.return_date}`}
                            </div>
                        </div>
                    ))}
                </div>

                <div style={styles.footer}>
                    <button onClick={onClose} style={styles.button}>Close</button>
                </div>
            </div>
        </div>
    );
}

const styles = {
    overlay: {
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.6)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)',
    },
    modal: {
        backgroundColor: 'white',
        padding: '24px',
        borderRadius: '12px',
        width: '500px',
        maxHeight: '80vh',
        boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
        display: 'flex',
        flexDirection: 'column',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        borderBottom: '1px solid #eee',
        paddingBottom: '10px',
    },
    closeButton: {
        background: 'none',
        border: 'none',
        fontSize: '24px',
        cursor: 'pointer',
        color: '#888',
    },
    list: {
        overflowY: 'auto',
        flex: 1,
        paddingRight: '5px',
    },
    item: {
        padding: '12px',
        borderBottom: '1px solid #f0f0f0',
        transition: 'background-color 0.2s',
    },
    itemHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: '4px',
    },
    timestamp: {
        fontSize: '12px',
        color: '#888',
    },
    itemDetails: {
        fontSize: '14px',
        color: '#555',
    },
    footer: {
        marginTop: '20px',
        display: 'flex',
        justifyContent: 'flex-end',
    },
    button: {
        padding: '10px 20px',
        backgroundColor: '#1F9E78',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        cursor: 'pointer',
        fontWeight: 'bold',
    }
};
