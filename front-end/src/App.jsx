import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

import Login from './pages/authf/Login';
import Register from './pages/authf/Register';
import ForgotPassword from './pages/authf/ForgotPassword';
import ResetPassword from './pages/authf/ResetPassword';

import FarmDasboard from './pages/dashboards/FarmDashboard';
import FieldDashboard from './pages/dashboards/FieldDashboard';
import FieldListDashBoard from './pages/dashboards/FieldListDashboard';

export default function App() {
  
  const [user, setuser] = useState(null); 

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login setUser={setuser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />


        <Route 
          path="/farm-dashboard" 
          element={user ? <FarmDasboard setUser={setuser} /> : <Navigate to="/" />} 
        />
        <Route 
          path="/field-dashboard" 
          element={user ? <FieldDashboard setUser={setuser} /> : <Navigate to="/" />} 
        />
        <Route 
          path="/fieldlist-dashboard" 
          element={user ? <FieldListDashBoard setUser={setuser} /> : <Navigate to="/" />} 
        />

      </Routes>
    </Router>
  );
}