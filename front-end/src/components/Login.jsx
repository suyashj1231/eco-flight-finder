import { useState } from 'react';


const Login = ({ onLoginSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        user_id: '',
        password: '',
        email: '',
        first_name: '',
        last_name: '',
        age: 25,
        height_cm: 175,
        weight_kg: 70,
        dob: '',
        title: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const endpoint = isLogin ? 'http://127.0.0.1:8000/auth/login' : 'http://127.0.0.1:8000/auth/signup';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Authentication failed');
            }

            const user = await response.json();
            onLoginSuccess(user);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="login-container">
            <h2>{isLogin ? 'Sign In' : 'Create Account'}</h2>
            {error && <p className="error-message">{error}</p>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>User ID / Username:</label>
                    <input
                        type="text"
                        name="user_id"
                        value={formData.user_id}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Password:</label>
                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                {!isLogin && (
                    <>
                        <div className="form-group">
                            <label>Email:</label>
                            <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label>Title:</label>
                                <select name="title" value={formData.title} onChange={handleChange}>
                                    <option value="">Select</option>
                                    <option value="Mr">Mr.</option>
                                    <option value="Miss">Miss</option>
                                    <option value="Mrs">Mrs.</option>
                                    <option value="Ms">Ms.</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>DOB:</label>
                                <input type="date" name="dob" value={formData.dob} onChange={handleChange} />
                            </div>
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label>First Name:</label>
                                <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>Last Name:</label>
                                <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
                            </div>
                        </div>
                        {/* Optional fields can be hidden or shown */}
                        <div className="form-row">
                            <div className="form-group">
                                <label>Age:</label>
                                <input type="number" name="age" value={formData.age} onChange={handleChange} min="0" />
                            </div>
                            <div className="form-group">
                                <label>Height (cm):</label>
                                <input type="number" name="height_cm" value={formData.height_cm} onChange={handleChange} />
                            </div>
                            <div className="form-group">
                                <label>Weight (kg):</label>
                                <input type="number" name="weight_kg" value={formData.weight_kg} onChange={handleChange} />
                            </div>
                        </div>
                    </>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
                </button>
            </form>

            <p className="toggle-auth">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button type="button" onClick={() => setIsLogin(!isLogin)} className="link-button">
                    {isLogin ? 'Sign Up' : 'Sign In'}
                </button>
            </p>
        </div>
    );
};

export default Login;
