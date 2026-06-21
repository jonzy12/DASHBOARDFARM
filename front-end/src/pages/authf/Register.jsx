import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [companyName, setCompanyName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const registerClick = async () => {setError('');

    if (!companyName || !email || !username || !password || !confirmPassword) {
      setError('fill all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: companyName,
          username: username,
          email: email,
          password: password
        }),
      });

      if (response.ok) {
        alert("account created");
        navigate('/');
        
      } else {
        setError( "Error creating account");
      }
    } catch (error) {
      console.error("Server connection error:", error);
      
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div style={{ padding: '40px', maxWidth: '360px', margin: '60px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ marginBottom: '6px', fontSize: '20px' }}>Create Account</h2>
      <p style={{ color: '#666', marginBottom: '24px', fontSize: '14px' }}>Sign up to get started</p>

      {error && <p style={{ color: 'red', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        
        <input 
          type="text" 
          placeholder="Farm Name"  
          value={companyName}     
          onChange={(e) => setCompanyName(e.target.value)} 
          style={{ padding: '10px', border: '1px solid ', borderRadius: '4px', fontSize: '14px' }} 
        />
        <input 
          type="email"     
          placeholder="Email"      
          value={email}           
          onChange={(e) => setEmail(e.target.value)} 
          style={{ padding: '10px', border: '1px solid ',   fontSize: '14px' }} 
        />
        <input 
          type="text"      
          placeholder="Username"           
          value={username}        
          onChange={(e) => setUsername(e.target.value)} 
          style={{ padding: '10px', border: '1px solid ' , fontSize: '14px' }} 
        />
        <input 
          type="text"  
          placeholder="Password"           
          value={password}        
          onChange={(e) => setPassword(e.target.value)} 
          style={{ padding: '10px', border: '1px solid ', fontSize: '14px' }} 
        />
        <input 
          type="text"  
          placeholder="Confirm Password"   
          value={confirmPassword} 
          onChange={(e) => setConfirmPassword(e.target.value)} 
          style={{ padding: '10px', border: '1px solid ', fontSize: '14px' }} 
        />

        <button
          onClick={registerClick}
          disabled={isLoading}
          style={{ 
            padding: '10px', 
            backgroundColor: 'blue', 
            color: 'white', 
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '14px' 
          }}
        >
          sign up
        </button>
      </div>

      <div style={{ marginTop: '18px', fontSize: '13px', color: 'grey', textAlign: 'center' }}>
        already have an account? <Link to="/" style={{ color: '#4a7fcb' }}>sign in</Link>
      </div>
    </div>
  );
}