import { useState } from 'react';

export default function EditProfile({ user, token, onClose, onUpdate }) {
    const [firstName, setFirstName] = useState(user.first_name || '');
    const [lastName, setLastName] = useState(user.last_name || '');
    const [age, setAge] = useState(user.age || '');
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        console.log("Submit clicked. Current user prop:", user);
        console.log("Current state:", { firstName, lastName, age });

        const payload = {};
        if (firstName !== user.first_name) payload.first_name = firstName;
        if (lastName !== user.last_name) payload.last_name = lastName;

        const numericAge = parseInt(age);
        if (numericAge !== (user.age || 0)) payload.age = numericAge;

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
            console.log("Sending PUT request to /users/me with payload:", payload);
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

    return (
        <div style={styles.overlay}>
            <div style={styles.modal}>
                <h3>Edit Profile</h3>
                <p>User ID: <strong>{user.username}</strong> (Cannot be changed)</p>

                {error && <p style={{ color: 'red' }}>{error}</p>}
                {success && <p style={{ color: 'green' }}>{success}</p>}

                <form onSubmit={handleSubmit} style={styles.form}>
                    <label>First Name:</label>
                    <input
                        style={styles.input}
                        type="text"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                    />

                    <label>Last Name:</label>
                    <input
                        style={styles.input}
                        type="text"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                    />

                    <label>Age:</label>
                    <input
                        style={styles.input}
                        type="number"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                    />

                    <hr style={{ width: '100%', margin: '10px 0' }} />

                    <label>Change Password (Optional):</label>
                    <input
                        style={styles.input}
                        type="password"
                        placeholder="Old Password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                    />
                    <input
                        style={styles.input}
                        type="password"
                        placeholder="New Password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                    />

                    <div style={styles.buttons}>
                        <button type="button" onClick={onClose} style={styles.cancelButton}>Close</button>
                        <button type="submit" style={styles.saveButton}>Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

const styles = {
    overlay: {
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },
    modal: {
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        width: '400px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
    },
    input: {
        padding: '8px',
        borderRadius: '4px',
        border: '1px solid #ccc',
    },
    buttons: {
        display: 'flex',
        justifyContent: 'flex-end',
        gap: '10px',
        marginTop: '10px',
    },
    saveButton: {
        padding: '8px 16px',
        backgroundColor: '#1F9E78',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
    },
    cancelButton: {
        padding: '8px 16px',
        backgroundColor: '#ccc',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
    }
};
