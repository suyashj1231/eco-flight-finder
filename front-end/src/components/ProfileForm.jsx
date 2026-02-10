import { useState } from "react";

export default function ProfileForm({ onSave }) {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    age: "",
    height_cm: "",
    weight_kg: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      first_name: form.first_name,
      last_name: form.last_name,
      age: parseInt(form.age),
      height_cm: parseFloat(form.height_cm),
      weight_kg: parseFloat(form.weight_kg),
    });
  };

  return (
    <div style={{ padding: "20px", maxWidth: "400px" }}>
      <h2>Create Your Profile</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="first_name"
          placeholder="First Name"
          value={form.first_name}
          onChange={handleChange}
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name"
          value={form.last_name}
          onChange={handleChange}
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <input
          type="number"
          name="age"
          placeholder="Age"
          value={form.age}
          onChange={handleChange}
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <input
          type="number"
          name="height_cm"
          placeholder="Height (cm)"
          value={form.height_cm}
          onChange={handleChange}
          step="0.1"
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <input
          type="number"
          name="weight_kg"
          placeholder="Weight (kg)"
          value={form.weight_kg}
          onChange={handleChange}
          step="0.1"
          required
          style={{ display: "block", marginBottom: "10px", padding: "8px", width: "100%" }}
        />
        <button
          type="submit"
          style={{
            padding: "10px 20px",
            backgroundColor: "#34A853",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            width: "100%",
          }}
        >
          Save Profile
        </button>
      </form>
    </div>
  );
}
