import { useState, useEffect } from 'react';
import Autocomplete from './Autocomplete.jsx';
import '../InputField.css';

export default function SearchForm({ onSearch, lastSearch }) {
  const [formData, setFormData] = useState({
    departure: '',
    arrival: '',
    departure_date: '',
    return_date: '',
    eco_mode: true
  });

  useEffect(() => {
    if (lastSearch) {
      setFormData(prev => ({
        ...prev,
        departure: lastSearch.departure_iata || '',
        arrival: lastSearch.arrival_iata || '',
        departure_date: lastSearch.departure_date || '',
        return_date: lastSearch.return_date || '',
      }));
    }
  }, [lastSearch]);

  const handleChange = (e) => {
    // If Autocomplete sends a custom event, it might not have type/checked
    // So we handle it safely
    const target = e.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(formData);
  };

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <div className="top-row">
        <Autocomplete
          name="departure"
          placeholder="From (City or Airport)"
          value={formData.departure}
          onChange={handleChange}
          required
        />
        <Autocomplete
          name="arrival"
          placeholder="To (City or Airport)"
          value={formData.arrival}
          onChange={handleChange}
          required
        />
      </div>

      <div className="bottom-row">
        <input
          type="date"
          name="departure_date"
          value={formData.departure_date}
          onChange={handleChange}
          required
        />
        <input
          type="date"
          name="return_date"
          value={formData.return_date}
          onChange={handleChange}
          placeholder="Return Date (Optional)"
        />
      </div>

      <div className="options-row">
        <label className="checkbox-label">
          <input
            type="checkbox"
            name="eco_mode"
            checked={formData.eco_mode}
            onChange={handleChange}
          />
          Eco Mode (Prioritize Low CO₂)
        </label>

        <label className="checkbox-label disabled-label" title="Only direct flights are currently supported">
          <input
            type="checkbox"
            checked={true}
            disabled
          />
          Direct Flights Only
        </label>
      </div>

      <button type="submit">
        Find Flights
      </button>
    </form>
  );
}
