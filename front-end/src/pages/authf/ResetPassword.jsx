import React, { useState } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const { token } = useParams();

  const resetClick = async () => {
    setError('');

    if (!password || !confirmPassword) {
      setError(' fill all  fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/reset-password-confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token, new_password: password })
      });
      
      if (response.ok) {
        alert("password updated ");
        navigate('/');
      } else {
        const errorData = await response.json();
        setError("Failed to reset password. Token might be expired");
      }
    } catch (err) {
      console.error(err);
      setError("error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '360px', margin: '80px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ marginBottom: '6px', fontSize: '20px' }}>Reset Password</h2>
      <p style={{ color: 'grey', marginBottom: '24px', fontSize: '14px' }}>Create a new password</p>

      {error && <p style={{ color: 'red', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <input
          type="password"
          placeholder="New Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: '10px', border: '1px solid ',  fontSize: '14px' }}
        />
        <input
          type="password"
          placeholder="Confirm New Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          style={{ padding: '10px', border: '1px solid ', fontSize: '14px' }}
        />
        
        <button
          onClick={resetClick}
          disabled={isLoading}
          style={{ padding: '10px', backgroundColor:'blue', color: 'white', cursor: isLoading ? 'not-allowed' : 'pointer', fontSize: '14px' }}
        >
          set  password
        </button>
      </div>

      <div style={{ marginTop: '18px', fontSize: '13px', color: 'grey', textAlign: 'center' }}>
        remember your password? <Link to="/" style={{ color: 'blue' }}>sign in</Link>
      </div>
    </div>
  );
}