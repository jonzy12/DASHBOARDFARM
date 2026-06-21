import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const navigate = useNavigate();

  const sendClick = async () => {
    
    if (email.trim() === '') {
      alert("enter yor mail");
      return;
    }

    setIsLoading(true);
    
    
    try {
      const response = await fetch('http://127.0.0.1:8000/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      });
      if (response.ok) {
        setMessage('sent a link');
        setTimeout(() => { window.location.replace("http://127.0.0.1:5173/");}, 3000);
      } 

    } catch (error) {
      console.error("Server connection error:", error);
      
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '360px', margin: '80px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ marginBottom: '6px', fontSize: '20px' }}>Forgot Password</h2>
      <p style={{ color: '#666', marginBottom: '24px', fontSize: '14px' }}>We  will send instructions to your email</p>

      {message && <p style={{ color: '#2a7a2a', fontSize: '13px', marginBottom: '12px' }}>{message}</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: '10px', border: '1px solid ', borderRadius: '4px', fontSize: '14px' }}
        />
        <div style={{ display: 'flex', gap: '10px' }}>
          
          <button
            onClick={sendClick}
            disabled={isLoading}
            style={{ flex: 1, padding: '10px', backgroundColor:'blue', color: 'white',   cursor: isLoading ? 'not-allowed' : 'pointer', fontSize: '14px' }}
          >
            Submit
          </button>
          
          <button
            type="button"
            onClick={() => navigate('/')}
            style={{ flex: 1, padding: '10px', backgroundColor: 'white', color: '#444', border: '1px solid ', cursor: isLoading ? 'not-allowed' : 'pointer', fontSize: '14px' }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}