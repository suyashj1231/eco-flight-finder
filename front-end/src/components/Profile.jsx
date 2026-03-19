import React, { useState } from 'react';


const Profile = ({ user, onUpdateUser, onLogout }) => {
    const [formData, setFormData] = useState({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        age: user.age || '',
        height_cm: user.height_cm || '',
        weight_kg: user.weight_kg || '',
        dob: user.dob || '',
        title: user.title || ''
    });

    const [passwordData, setPasswordData] = useState({
        old_password: '',
        new_password: '',
        confirm_password: ''
    });

    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleProfileUpdate = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        try {
            const response = await fetch('http://127.0.0.1:8000/user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...user, ...formData, user_id: user.google_id })
            });

            if (!response.ok) throw new Error('Failed to update profile');

            const updatedUser = await response.json();
            onUpdateUser(updatedUser);
            setMessage('Profile updated successfully!');
        } catch (err) {
            setError(err.message);
        }
    };

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        if (passwordData.new_password !== passwordData.confirm_password) {
            setError("New passwords do not match");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.google_id,
                    old_password: passwordData.old_password,
                    new_password: passwordData.new_password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to change password');
            }

            setMessage('Password changed successfully!');
            setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="profile-container">
            <h2>My Profile</h2>
            <div className="user-info">
                <p><strong>User ID:</strong> {user.google_id}</p>
                <button onClick={onLogout} className="logout-btn">Logout</button>
            </div>

            {message && <p className="success-message">{message}</p>}
            {error && <p className="error-message">{error}</p>}

            <section className="profile-section">
                <h3>Edit Personal Details</h3>
                <form onSubmit={handleProfileUpdate}>
                    <div className="form-row">
                        <div className="form-group">
                            <label>Title:</label>
                            <select value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })}>
                                <option value="">Select</option>
                                <option value="Mr">Mr.</option>
                                <option value="Miss">Miss</option>
                                <option value="Mrs">Mrs.</option>
                                <option value="Ms">Ms.</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>DOB:</label>
                            <input type="date" value={formData.dob} onChange={(e) => setFormData({ ...formData, dob: e.target.value })} />
                        </div>
                    </div>
                    <div className="form-row">
                        <div className="form-group">
                            <label>First Name:</label>
                            <input type="text" value={formData.first_name} onChange={(e) => setFormData({ ...formData, first_name: e.target.value })} />
                        </div>
                        <div className="form-group">
                            <label>Last Name:</label>
                            <input type="text" value={formData.last_name} onChange={(e) => setFormData({ ...formData, last_name: e.target.value })} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>Email:</label>
                        <input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                    </div>
                    <button type="submit">Update Profile</button>
                </form>
            </section>

            <section className="profile-section">
                <h3>Change Password</h3>
                <form onSubmit={handlePasswordChange}>
                    <div className="form-group">
                        <label>Old Password:</label>
                        <input type="password" value={passwordData.old_password} onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>New Password:</label>
                        <input type="password" value={passwordData.new_password} onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>Confirm New Password:</label>
                        <input type="password" value={passwordData.confirm_password} onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })} required />
                    </div>
                    <button type="submit">Change Password</button>
                </form>
            </section>

            <section className="profile-section">
                <h3>Search History</h3>
                {user.search_history && user.search_history.length > 0 ? (
                    <ul className="history-list">
                        {user.search_history.slice().reverse().map((search, index) => (
                            <li key={index} className="history-item">
                                <span className="search-route">{search.departure} &rarr; {search.arrival}</span>
                                <span className="search-date">{search.date}</span>
                                <span className="search-meta">({search.results_count} results)</span>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No search history found.</p>
                )}
            </section>
        </div>
    );
};

export default Profile;