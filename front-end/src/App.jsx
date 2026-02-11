import { useState } from 'react';
import SearchForm from './components/SearchForm.jsx';
import Results from './components/Results.jsx';
import './App.css';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

      const response = await fetch('http://127.0.0.1:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Search failed:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='page-container'>
      <div className='my-div'>
        <h1>Eco Flight Finder</h1>
        <SearchForm onSearch={handleSearch} />

        {loading && <p>Searching flights... This might take a moment.</p>}
        {error && <p style={{ color: 'red', marginTop: '10px' }}><strong>Error:</strong> {error}</p>}
        {!loading && !error && results.length > 0 && <Results results={results} />}
      </div>
    </div>
  )
}

export default App
