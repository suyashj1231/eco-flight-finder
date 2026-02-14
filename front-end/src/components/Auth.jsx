import { useState } from 'react';

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

            const data = await response.json();
            onLogin(data.access_token);
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
                const errData = await response.json();
                throw new Error(errData.detail || 'Registration failed');
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
        <div style={styles.container}>
            <div style={styles.card}>
                <h2>{isLogin ? 'Login' : 'Register'}</h2>

                {error && <p style={{ color: 'red' }}>{error}</p>}

                {isLogin ? (
                    <form onSubmit={handleLogin} style={styles.form}>
                        <input
                            style={styles.input}
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button type="submit" style={styles.button}>Login</button>
                        <p>
                            Don't have an account?
                            <span
                                style={styles.link}
                                onClick={() => setIsLogin(false)}
                            > Register</span>
                        </p>
                    </form>
                ) : (
                    <form onSubmit={handleRegister} style={styles.form}>
                        <input
                            style={styles.input}
                            type="text"
                            placeholder="Username"
                            value={regUsername}
                            onChange={(e) => setRegUsername(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="text"
                            placeholder="First Name"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="text"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="number"
                            placeholder="Age"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="password"
                            placeholder="Password"
                            value={regPassword}
                            onChange={(e) => setRegPassword(e.target.value)}
                            required
                        />
                        <input
                            style={styles.input}
                            type="password"
                            placeholder="Retype Password"
                            value={regRetypePassword}
                            onChange={(e) => setRegRetypePassword(e.target.value)}
                            required
                        />
                        <button type="submit" style={styles.button}>Register</button>
                        <p>
                            Already have an account?
                            <span
                                style={styles.link}
                                onClick={() => setIsLogin(true)}
                            > Login</span>
                        </p>
                    </form>
                )}
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f0f2f5',
    },
    card: {
        padding: '2rem',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
    },
    input: {
        padding: '0.8rem',
        borderRadius: '4px',
        border: '1px solid #ddd',
        fontSize: '1rem',
    },
    button: {
        padding: '0.8rem',
        backgroundColor: '#1F9E78',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        fontSize: '1rem',
        cursor: 'pointer',
    },
    link: {
        color: '#1F9E78',
        cursor: 'pointer',
        fontWeight: 'bold',
        marginLeft: '5px'
    }
};
