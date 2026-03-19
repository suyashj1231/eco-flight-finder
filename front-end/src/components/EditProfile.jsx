import { useState } from 'react';
import './Modal.css';

export default function EditProfile({ user, token, onClose, onUpdate, onLogout }) {
    const [firstName, setFirstName] = useState(user.first_name || '');
    const [lastName, setLastName] = useState(user.last_name || '');
    const [age, setAge] = useState(user.age || '');
    const [resultsPerPage, setResultsPerPage] = useState(user.results_per_page || 8);
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        const payload = {};
        if (firstName !== user.first_name) payload.first_name = firstName;
        if (lastName !== user.last_name) payload.last_name = lastName;

        const numericAge = parseInt(age);
        if (numericAge !== (user.age || 0)) payload.age = numericAge;

        const numericRPP = parseInt(resultsPerPage);
        if (numericRPP !== (user.results_per_page || 8)) payload.results_per_page = numericRPP;

        if (newPassword) {
            if (!oldPassword) {
                setError("Old password required to set new password");
                return;
            }
            payload.old_password = oldPassword;
            payload.new_password = newPassword;
        }

        if (Object.keys(payload).length === 0) {
            setError("No changes to save");
            return;
        }

        try {
            const response = await fetch('/users/me', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Update failed');
            }

            const updatedUser = await response.json();
            onUpdate(updatedUser);
            setSuccess("Profile updated successfully!");
            // clear passwords
            setOldPassword('');
            setNewPassword('');
        } catch (err) {
            setError(err.message);
        }
    };

    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const handleDeleteAccount = async () => {
        try {
            const response = await fetch('/users/me', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                alert("Account deleted successfully.");
                if (onLogout) onLogout();
                onClose();
            } else {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Delete failed');
            }
        } catch (err) {
            setError(err.message);
            setShowDeleteConfirm(false);
        }
    };

    if (showDeleteConfirm) {
        return (
            <div className="modal-overlay">
                <div className="modal-content" style={{ maxWidth: '400px', textAlign: 'center' }}>
                    <div className="modal-header" style={{ justifyContent: 'center' }}>
                        <h3 style={{ color: '#e74c3c' }}>Delete Account?</h3>
                    </div>
                    <div className="modal-body">
                        <p style={{ marginBottom: '20px', color: '#34495e' }}>
                            Are you sure you want to delete your account? <br />
                            <strong>This action cannot be undone.</strong>
                        </p>
                        <div className="modal-footer" style={{ justifyContent: 'center', gap: '15px' }}>
                            <button
                                onClick={handleDeleteAccount}
                                className="btn-danger"
                            >
                                Yes, Delete
                            </button>
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className="btn-secondary"
                            >
                                No, Keep Account
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h3>Edit Profile</h3>
                    <button onClick={onClose} className="close-btn">&times;</button>
                </div>

                <div className="modal-body">
                    <p style={{ marginBottom: '15px', color: '#7f8c8d' }}>
                        User ID: <strong>{user.username}</strong>
                    </p>

                    {error && <p style={{ color: '#e74c3c', marginBottom: '10px' }}>{error}</p>}
                    {success && <p style={{ color: '#27ae60', marginBottom: '10px' }}>{success}</p>}

                    <form onSubmit={handleSubmit} className="modal-form">
                        <div>
                            <label>First Name:</label>
                            <input
                                type="text"
                                style={{ width: '100%' }}
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                            />
                        </div>

                        <div>
                            <label>Last Name:</label>
                            <input
                                type="text"
                                style={{ width: '100%' }}
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                            />
                        </div>

                        <div>
                            <label>Age:</label>
                            <input
                                type="number"
                                style={{ width: '100%' }}
                                value={age}
                                onChange={(e) => setAge(e.target.value)}
                                min="0"
                            />
                        </div>

                        <div>
                            <label>Results Per Page:</label>
                            <select
                                style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ddd' }}
                                value={resultsPerPage}
                                onChange={(e) => setResultsPerPage(e.target.value)}
                            >
                                <option value="8">8</option>
                                <option value="16">16</option>
                                <option value="24">24</option>
                                <option value="32">32</option>
                            </select>
                        </div>

                        <hr style={{ width: '100%', margin: '15px 0', border: 'none', borderTop: '1px solid #eee' }} />

                        <div>
                            <label>Change Password (Optional):</label>
                            <input
                                type="password"
                                placeholder="Old Password"
                                style={{ width: '100%', marginBottom: '10px' }}
                                value={oldPassword}
                                onChange={(e) => setOldPassword(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="New Password"
                                style={{ width: '100%' }}
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                            />
                        </div>

                        <div className="modal-footer">
                            <button type="button" onClick={() => setShowDeleteConfirm(true)} className="btn-danger" style={{ marginRight: 'auto' }}>Delete Account</button>
                            <button type="button" onClick={onClose} className="btn-secondary">Close</button>
                            <button type="submit" className="btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
