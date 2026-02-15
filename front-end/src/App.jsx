import { useState } from 'react';
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
          onClear={() => setHistory([])}
        />
      )}

      {showProfile && user && (
        <EditProfile
          user={user}
          token={token}
          onClose={() => setShowProfile(false)}
          onUpdate={(u) => { setUser(u); }}
          onLogout={handleLogout}
        />
      )}

      <div className='my-div'>
        <div className="app-header">
          <h1 className="app-title">Eco Flight Finder</h1>

          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="menu-btn"
            >
              <strong>{user ? `${user.first_name} ${user.last_name}` : "Menu"}</strong>
              <span style={{ fontSize: '0.8rem' }}>▼</span>
            </button>

            {showMenu && (
              <div className="dropdown-menu">
                <div
                  onClick={() => { setShowHistory(true); setShowMenu(false); }}
                  className="dropdown-item"
                >
                  Search History
                </div>
                <div
                  onClick={() => { setShowProfile(true); setShowMenu(false); }}
                  className="dropdown-item"
                >
                  Edit Details
                </div>
                <div
                  onClick={handleLogout}
                  className="dropdown-item logout"
                >
                  Logout
                </div>
              </div>
            )}
          </div>
        </div>

        <SearchForm
          onSearch={handleSearch}
          lastSearch={history.length > 0 ? history[0] : null}
        />

        {user && history.length > 0 && (
          <div className="recent-searches">
            <h4 className="recent-title">Recent Searches</h4>
            <div className="history-grid">
              {history.map(item => (
                <div
                  key={item.id}
                  className="history-card"
                  onClick={() => handleSearch({
                    departure: item.departure_iata,
                    arrival: item.arrival_iata,
                    departure_date: item.departure_date,
                    return_date: item.return_date,
                    eco_mode: true // Default for re-search
                  })}
                >
                  <div className="history-route">
                    {item.departure_iata} ➔ {item.arrival_iata}
                  </div>
                  <div className="history-date">
                    {item.departure_date}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loading && <p className="loading-msg">Searching flights... This might take a moment.</p>}
        {error && <div className="error-msg"><strong>Error:</strong> {error}</div>}
        {!loading && !error && results.length > 0 &&
          <Results
            results={results}
            resultsPerPage={user?.results_per_page || 8}
            onBack={() => setResults([])}
          />
        }
      </div>
    </div>
  )
}

export default App
