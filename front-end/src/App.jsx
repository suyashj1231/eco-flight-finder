import { useState, useEffect } from 'react';
import SearchForm from './components/SearchForm.jsx';
import Results from './components/Results.jsx';
import Auth from './components/Auth.jsx';
import EditProfile from './components/EditProfile.jsx';
import SearchHistory from './components/SearchHistory.jsx';
import './App.css';

function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const [results, setResults] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (accessToken) => {
    setToken(accessToken);
    // Fetch User Details
    try {
      const res = await fetch('/users/me', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      if (res.ok) {
        setUser(await res.json());
        fetchHistory(accessToken);
      }
    } catch (e) {
      console.error("Failed to fetch user:", e);
    }
  };

  const fetchHistory = async (tokenToUse) => {
    try {
      const res = await fetch('/users/history', {
        headers: { 'Authorization': `Bearer ${tokenToUse}` }
      });
      if (res.ok) {
        const data = await res.json();
        // Sort by timestamp desc and take top 5
        const sorted = data.sort((a, b) => new Date(b.search_timestamp) - new Date(a.search_timestamp));
        setHistory(sorted.slice(0, 5));
      }
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setResults([]);
    setUser(null);
    setHistory([]);
    setShowMenu(false);
  };

  const handleSearch = async (formData) => {
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      // Map SearchForm data to backend API expectation
      const payload = {
        departure_iata: formData.departure,
        arrival_iata: formData.arrival,
        departure_date: formData.departure_date,
        return_date: formData.return_date || null, // Ensure null if empty string
        eco_mode: formData.eco_mode,
        sort_by: "emissions" // Default sort
      };

      // Use authenticated endpoint if token exists
      const endpoint = token ? '/search_authenticated' : '/search';
      const headers = {
        'Content-Type': 'application/json',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      // Refresh history if authenticated
      if (token) {
        fetchHistory(token);
      }
    } catch (err) {
      console.error("Search failed:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className='page-container'>
      {showHistory && (
        <SearchHistory
          token={token}
          onClose={() => setShowHistory(false)}
        />
      )}

      {showProfile && user && (
        <EditProfile
          user={user}
          token={token}
          onClose={() => setShowProfile(false)}
          onUpdate={(u) => { setUser(u); }}
        />
      )}

      <div className='my-div'>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', position: 'relative' }}>
          <h1 style={{ margin: 0 }}>Eco Flight Finder</h1>

          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              style={{
                padding: '8px 12px',
                cursor: 'pointer',
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              <strong>{user ? `${user.first_name} ${user.last_name}` : "Menu"}</strong>
              <span>▼</span>
            </button>

            {showMenu && (
              <div style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
                marginTop: '5px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                width: '150px',
                zIndex: 100,
                overflow: 'hidden'
              }}>
                <div
                  onClick={() => { setShowHistory(true); setShowMenu(false); }}
                  style={{ padding: '10px', cursor: 'pointer', borderBottom: '1px solid #eee', color: '#333' }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  Search History
                </div>
                <div
                  onClick={() => { setShowProfile(true); setShowMenu(false); }}
                  style={{ padding: '10px', cursor: 'pointer', borderBottom: '1px solid #eee', color: '#333' }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  Edit Details
                </div>
                <div
                  onClick={handleLogout}
                  style={{ padding: '10px', cursor: 'pointer', color: '#d32f2f' }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  Logout
                </div>
              </div>
            )}
          </div>
        </div>

        <SearchForm onSearch={handleSearch} />

        {user && history.length > 0 && (
          <div style={styles.recentSearches}>
            <h4 style={styles.recentTitle}>Recent Searches</h4>
            <div style={styles.historyGrid}>
              {history.map(item => (
                <div
                  key={item.id}
                  style={styles.historyCard}
                  onClick={() => handleSearch({
                    departure: item.departure_iata,
                    arrival: item.arrival_iata,
                    departure_date: item.departure_date,
                    return_date: item.return_date,
                    eco_mode: true // Default for re-search
                  })}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
                  }}
                >
                  <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                    {item.departure_iata} ➔ {item.arrival_iata}
                  </div>
                  <div style={{ fontSize: '11px', color: '#666' }}>
                    {item.departure_date}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && <p>Searching flights... This might take a moment.</p>}
        {error && <p style={{ color: 'red', marginTop: '10px' }}><strong>Error:</strong> {error}</p>}
        {!loading && !error && results.length > 0 && <Results results={results} />}
      </div>
    </div>
  )
}

const styles = {
  recentSearches: {
    marginTop: '25px',
    textAlign: 'left',
    width: '100%',
    padding: '0 10px'
  },
  recentTitle: {
    fontSize: '14px',
    color: '#333',
    marginBottom: '10px',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    borderBottom: '1px solid #eee',
    paddingBottom: '5px'
  },
  historyGrid: {
    display: 'flex',
    gap: '12px',
    overflowX: 'auto',
    paddingBottom: '10px',
    scrollbarWidth: 'thin'
  },
  historyCard: {
    backgroundColor: '#fff',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '10px 15px',
    minWidth: '130px',
    flexShrink: 0,
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  }
}

export default App
