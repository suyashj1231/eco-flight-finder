import { useState } from "react";

export default function SearchForm({ onSearch }) {
  const [form, setForm] = useState({
    departure: "SFO",
    arrival: "JFK",
    departure_date: "2026-02-10",
    return_date: null,
    eco_mode: true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(form);
  };

  return (
    <div style={{ padding: "20px", maxWidth: "500px" }}>
      <h2>Search Flights</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "15px" }}>
          <input
            type="text"
            name="departure"
            placeholder="Departure (IATA)"
            value={form.departure}
            onChange={handleChange}
            style={{ padding: "8px" }}
          />
          <input
            type="text"
            name="arrival"
            placeholder="Arrival (IATA)"
            value={form.arrival}
            onChange={handleChange}
            style={{ padding: "8px" }}
          />
        </div>
        <div style={{ marginBottom: "15px" }}>
          <input
            type="date"
            name="departure_date"
            value={form.departure_date}
            onChange={handleChange}
            style={{ padding: "8px", width: "100%", boxSizing: "border-box" }}
          />
        </div>
        <label style={{ display: "flex", alignItems: "center", marginBottom: "15px" }}>
          <input
            type="checkbox"
            name="eco_mode"
            checked={form.eco_mode}
            onChange={handleChange}
            style={{ marginRight: "10px" }}
          />
          Eco Mode (Prioritize CO2 emissions)
        </label>
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            backgroundColor: "#1F9E78",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%",
            fontSize: "16px",
          }}
        >
          Search Flights
        </button>
      </form>
    </div>
  );
}
