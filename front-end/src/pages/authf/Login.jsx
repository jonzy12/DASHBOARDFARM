import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Login({ setUser }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [isLoading, setIsLoading] = useState(false); 
  const navigate = useNavigate();

  const loginClick = async () => {

    if (username.trim() === '' || password.trim() === '') {
      alert("fill the fields");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setUser({ token: data.access_token }); 
        navigate('/farm-dashboard');
      } else {
        alert("שגיאה בהתחברות: שם משתמש או סיסמה לא נכונים");
      }
    } catch (error) {
      console.error("שגיאת תקשורת עם השרת:", error);

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '360px', margin: '80px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ marginBottom: '6px', fontSize: '20px' }}>Login</h2>
      <p style={{ color: '#666', marginBottom: '24px', fontSize: '14px' }}>Enter your username and password</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '4px', fontSize: '14px' }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: '10px', border: '1px solid #ccc', borderRadius: '4px', fontSize: '14px' }}
        />

        <button
          onClick={loginClick}
          disabled={isLoading}
          style={{ 
            padding: '10px', 
            backgroundColor: 'blue', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: isLoading ? 'not-allowed' : 'pointer', 
            fontSize: '14px', 
            marginTop: '10px' 
          }}
        >
          Sign In
        </button>
      </div>

      <div style={{ marginTop: '18px', fontSize: '13px', color: '#666', display: 'flex', justifyContent: 'space-between' }}>
        <Link to="/forgot-password" style={{ color: '#4a7fcb' }}>Forgot Password?</Link>
        <span>New here? <Link to="/register" style={{ color: '#4a7fcb' }}>Create Account</Link></span>
      </div>
    </div>
  );
}