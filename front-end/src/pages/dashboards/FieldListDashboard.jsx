import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AddFieldMap from './AddFieldMap';

export default function FieldListDashboard() {
  const [fields, setFields] = useState([]);
  const [isAddingMode, setIsAddingMode] = useState(false);
  const navigate = useNavigate();



  const loadFields = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return ;

      const resultts = await fetch('http://localhost:8000/fields', {headers: { Authorization: `Bearer ${token}` }});

      if (resultts.ok) setFields(await resultts.json());
    } 
    catch (e) {
      console.error(e);
    }
  };


  
  useEffect(() => { loadFields();}, []);

  

  const handleSaveField = async (fieldData) => {
    try {
      const token = localStorage.getItem('token');
      const ress = await fetch('http://localhost:8000/add-field', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(fieldData)
      });

      if (ress.ok) {
        alert("Saved");
        setIsAddingMode(false);
        loadFields();
      } else {
        alert("Error saving");
      }
    } catch (e) {
      console.error(e);
      alert("Server error");
    }
  };

  const openField = (field) => navigate("/field-dashboard", { state: { field } });

  if (isAddingMode) return <AddFieldMap onCancel={() => setIsAddingMode(false)} onSave={handleSaveField} />;

  return (
    <div style={{ padding: '20px' }}>
      <h2>fields</h2>
      <button onClick={() => navigate('/farm-dashboard')} style={{ marginRight: '10px' }}>back</button>
      <button onClick={() => setIsAddingMode(true)}>add field</button>


      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '20px' ,cursor: 'pointer'}}>
        {fields.map((field, i) => (
          <div
            key={i}
            onClick={() => openField(field)}
            style={{ border: '1px solid', padding: '15px', width: '200px', backgroundColor: 'white' }}
          >
            <p style={{  fontWeight: 'bold' }}>{field.plot_name}</p>
            <p >crop: {field.crop_type}</p>
            <p >size: {field.area_size_hectares.toFixed(2)} ha</p>
            <p >coord: {Number(field.latitude).toFixed(4)}, {Number(field.longitude).toFixed(4)}</p>
          </div>
        ))}
      </div>

      {fields.length === 0 && <p>add field</p>}
    </div>
  );
}