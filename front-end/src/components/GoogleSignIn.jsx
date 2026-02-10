export default function GoogleSignIn({ onSignIn }) {
  const handleSimulateSignIn = () => {
    // Simulate Google Sign-In for demo
    onSignIn({
      id: "guest_" + Math.random().toString(36).substr(2, 9),
      email: "demo@example.com",
      name: "Demo User",
    });
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h1>Eco Flight Finder</h1>
      <p>Find the most environmentally friendly flights</p>
      <button 
        onClick={handleSimulateSignIn}
        style={{
          padding: "12px 24px",
          fontSize: "16px",
          backgroundColor: "#4285F4",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Simulate Sign-In
      </button>
      <p style={{ marginTop: "20px", fontSize: "12px", color: "#666" }}>
        TODO: Replace with real Google OAuth when credentials are available
      </p>
    </div>
  );
}
