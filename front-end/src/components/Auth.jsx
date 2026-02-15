import { useState } from 'react';
import './Auth.css';

export default function Auth({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [error, setError] = useState(null);

    // Login State
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // Register State
    const [regUsername, setRegUsername] = useState('');
    const [regPassword, setRegPassword] = useState('');
    const [regRetypePassword, setRegRetypePassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [age, setAge] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(null);

        // Convert to form data for OAuth2
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch('/token', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Invalid credentials');

            let data = {};
            try {
                data = await response.json();
            } catch (e) {
                console.error("Login response parse error:", e);
                // default to empty or handle gracefully
            }

            if (data.access_token) {
                onLogin(data.access_token);
            } else {
                throw new Error("No access token received");
            }
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError(null);

        if (regPassword !== regRetypePassword) {
            setError("Passwords do not match");
            return;
        }

        const payload = {
            username: regUsername,
            password: regPassword,
            first_name: firstName,
            last_name: lastName,
            age: parseInt(age)
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                let errData = {};
                try {
                    errData = await response.json();
                } catch (e) {
                    // Response was not JSON
                }
                throw new Error(errData.detail || `Registration failed: ${response.statusText}`);
            }

            // Auto Login Mechanism
            const formData = new FormData();
            formData.append('username', regUsername);
            formData.append('password', regPassword);

            const loginResp = await fetch('/token', {
                method: 'POST',
                body: formData,
            });

            if (loginResp.ok) {
                const data = await loginResp.json();
                onLogin(data.access_token);
            } else {
                setIsLogin(true);
                alert("Registration successful! Please log in manually.");
            }

        } catch (err) {
            console.error(err);
            setError(err.message || 'Connection failed');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>

                {error && <div className="auth-error">{error}</div>}

                {isLogin ? (
                    <form onSubmit={handleLogin} className="auth-form">
                        <input
                            className="auth-input"
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                        <input
                            className="auth-input"
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        <button type="submit" className="auth-button">Login</button>

                        <div className="auth-footer">
                            Don't have an account?
                            <span
                                className="auth-link"
                                onClick={() => { setIsLogin(false); setError(null); }}
                            > Register</span>
                        </div>
                    </form>
                ) : (
                    <form onSubmit={handleRegister} className="auth-form">
                        <input
                            className="auth-input"
                            type="text"
                            placeholder="Username"
                            value={regUsername}
                            onChange={(e) => setRegUsername(e.target.value)}
                            required
                        />
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            <input
                                className="auth-input"
                                type="text"
                                placeholder="First Name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                required
                            />
                            <input
                                className="auth-input"
                                type="text"
                                placeholder="Last Name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                required
                            />
                        </div>
                        <input
                            className="auth-input"
                            type="number"
                            placeholder="Age"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            required
                        />
                        <input
                            className="auth-input"
                            type="password"
                            placeholder="Password"
                            value={regPassword}
                            onChange={(e) => setRegPassword(e.target.value)}
                            required
                        />
                        <input
                            className="auth-input"
                            type="password"
                            placeholder="Retype Password"
                            value={regRetypePassword}
                            onChange={(e) => setRegRetypePassword(e.target.value)}
                            required
                        />

                        <button type="submit" className="auth-button">Register</button>

                        <div className="auth-footer">
                            Already have an account?
                            <span
                                className="auth-link"
                                onClick={() => { setIsLogin(true); setError(null); }}
                            > Login</span>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
