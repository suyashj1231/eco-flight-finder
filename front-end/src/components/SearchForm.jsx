import { useState } from 'react';
import Autocomplete from './Autocomplete.jsx';
import '../InputField.css';

export default function SearchForm({ onSearch }) {
  const [formData, setFormData] = useState({
    departure: '',
    arrival: '',
    departure_date: '',
    return_date: '',
    eco_mode: true
  });

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

      <label style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        color: 'var(--text-dark)',
        cursor: 'pointer',
        alignSelf: 'flex-start',
        marginLeft: '5px'
      }}>
        <input
          type="checkbox"
          name="eco_mode"
          checked={formData.eco_mode}
          onChange={handleChange}
          style={{ width: 'auto', margin: 0 }}
        />
        <span>Eco Mode (Prioritize Low CO₂)</span>
      </label>

      <button type="submit">
        Find Flights
      </button>
    </form>
  );
}
