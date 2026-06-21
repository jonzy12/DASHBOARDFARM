import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, Circle } from 'react-leaflet';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

import { cropStressLegend } from '/home/jonzy/python/תיקייה לפרוייקט גמר/dashfarmboardtrue/front-end/src/cropStressLegend';

export default function FieldDashboard() {
  const [fields, setFields] = useState([]);
  const [selectedField, setSelectedField] = useState(null);
  const [weatherData, setWeatherData] = useState([]);



  const [fieldScore, setFieldScore] = useState(null);

  const [mlHealth, setMlHealth] = useState(null);

  const navigate = useNavigate();

  const loadFields = async () => {
    try {
      const token = localStorage.getItem('token');
      const fieldsget = await fetch('http://localhost:8000/fields', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (fieldsget.ok) {
        const data = await fieldsget.json();
        setFields(data);
        
        if (data.length > 0) {
          selectField(data[0]); 
        }
      }
    } 
    catch (e)
    {
      console.error(e);
    }
  };

  useEffect(() => {loadFields();}, []);


  const selectField = async (field) => {setSelectedField(field); setWeatherData([]);  setFieldScore(null);    setMlHealth(null); 

    const token = localStorage.getItem('token');

    try {
      const weatherget = await fetch(`http://localhost:8000/field/${field._id}/weather`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (weatherget.ok) {
        const data = await weatherget.json();
        setWeatherData(data.weather);
      }

      const scoreget = await fetch(`http://localhost:8000/field/${field._id}/score`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (scoreget.ok) {
        const scoreData = await scoreget.json();
        setFieldScore(scoreData);
      }

      const healthget = await fetch(`http://localhost:8000/field/${field._id}/health`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (healthget.ok) {
        const healthData = await healthget.json();
        setMlHealth(healthData);
      }

    } catch (e) {
      console.error(e);
    }
  };


  const cropLimits = cropStressLegend[selectedField?.crop_type?.toLowerCase() || ''];

  const moredatatoknow = weatherData.map(day => ({...day,
    
    isstressed: cropLimits && (day.temperatureAVG < cropLimits.minTemp || day.temperatureAVG > cropLimits.maxTemp),
    high_stress: cropLimits && day.temperatureAVG > cropLimits.maxTemp ? 1 : null,
    low_stress: cropLimits && day.temperatureAVG < cropLimits.minTemp ? 1 : null
  }));

  return (
    <div style={{ padding: '30px', backgroundColor:  'lightgrey', minHeight: '100vh' }}>

      {/* Header Container */}
      <div style={{  display: 'flex', justifyContent:   'space-between', alignItems: 'center', borderBottom: '2px solid ', paddingBottom: '15px', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: 'black' }}>Field Dashboard</h2>
        <div>
          <button onClick={() => navigate('/fieldlist-dashboard')} style={{ padding: '8px ', marginRight: '10px', backgroundColor: 'lightgreen' }}>back to the fields list</button>
          <button onClick={() => { localStorage.removeItem('token'); navigate('/'); }} style={{ padding: '8px ', backgroundColor: 'red', color: 'white' }}>logout</button>
        </div>
      </div>

      {/* Field Selector Buttons */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px'}}>
        {fields.map(f => {
          const isSelected = selectedField?._id === f._id;
          return (
            <button 
              key={f._id} 
              onClick={() => selectField(f)}
              style={{
                padding: '10px',
                backgroundColor: isSelected ? 'green' : 'white',
                border: '1px solid ',
              }}
            >
              {f.plot_name}
            </button>
          );
        })} 
      </div>

      {selectedField && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* Top Row: Map and Details */}
          <div style={{ display: 'flex', gap: '20px' }}>
            
            {/* Map Card */}
            <div style={{ flex: 2, backgroundColor: 'white', padding: '20px', border: '1px solid ' }}>
              <h3 >map of field</h3>
              <div style={{ height: '500px', borderRadius: '5px', border: '1px solid ' }}>
                <MapContainer key={selectedField._id} center={[selectedField.latitude, selectedField.longitude]} zoom={15} style={{ height: '100%', width: '100%' }}>
                  <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" />
                  <Circle
                    center={[selectedField.latitude, selectedField.longitude]}
                    radius={Math.sqrt((selectedField.area_size_hectares * 10000) / Math.PI)}
                  />
                </MapContainer>
              </div>
            </div>

            {/* עמודת פרטים + כרטיסיית הערות AI */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* Details Card */}
              <div style={{ backgroundColor: 'white', border: '1px solid ',    padding: '15px'}}>
                <h3 style={{ marginTop: 0 }}> stuff about the farm</h3>
                <p><strong>crop:</strong> {selectedField.crop_type}</p>
                <p><strong>area:</strong> {selectedField.area_size_hectares.toFixed(2)} ha</p>
                <p><strong>coordinates:</strong> <br/> {selectedField.latitude.toFixed(5)}, {selectedField.longitude.toFixed(5)}</p>
                
                {fieldScore && (
                  <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'white',  border: '1px solid ' }}>
                    <p style={{ margin: 0, fontWeight: 'bold' }}> health score for the field</p>
                    <h2 style={{ margin: '5px ', color: 'black' }}>
                      {Number(fieldScore.score).toFixed(2)} / {fieldScore.out_of_number}
                    </h2>
                  </div>
                )}
              </div>

              {/* AI Alerts Card (התראות המערכת) */}
              {mlHealth && (
                <div  style={{ 
                  borderRadius: '8px', 
                  padding: '15px',
                  border: '1px solid  ',
                  backgroundColor: 'white'
                }}>
                  <h3 >
                    {mlHealth.message}
                  </h3>
                  
            
                  {/* לולאה שעוברת על כל ההערות/ההתראות שהשרת שלח ומדפיסה אותן */}
                  {mlHealth.alerts && mlHealth.alerts.length > 0 && (
                    <ul style={{color: 'red' }}>
                      {mlHealth.alerts.map((alert, index) => (<p key={index}>{alert}</p>))}
                    </ul>
                  )}
                  
                </div>
              )}

            </div>
          </div>

          {/* Charts Row */}
          <div style={{ display: 'flex', gap: '20px' ,}}>
            
            {/* NDVI Chart */}
            <div style={{ flex: 1, border: '1px solid ',backgroundColor: 'white' }}>
              <h3 style={{ textAlign: 'center' }}>ndvi prediction based on temperature for next 7 days</h3>
              
              <ResponsiveContainer width="100%" height={250}>
                 <LineChart data={weatherData}>
                  <XAxis dataKey="temperatureAVG" label={{ value: 'temperature', dy: 11 }} />  
                  <YAxis label={{ value: 'ndvi', dy: -22 ,dx: -15}} />
                  <Tooltip />
                  <Line  dataKey="ndvi"  />
                </LineChart>
              </ResponsiveContainer>
              
            </div>

            {/* Stress Chart */}
            <div style={{ flex: 1,  border: '1px solid',backgroundColor: 'white' }}>
              <h3  style={{ textAlign: 'center' }}>temperature stress for the next 7 days</h3>
              
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={moredatatoknow}>
                    <XAxis dataKey="date_str" tickFormatter={(val) => `${val}, ${new Date().getFullYear()}`}/>
                    <Bar dataKey="high_stress"  fill="red" name="above optimal"   />
                    <Bar dataKey="low_stress"   fill="blue" name="below optimal" />
                    <Legend  />
                  </BarChart>
                </ResponsiveContainer>
              
            </div>

          </div>

          {/* Weather Row */}
            <h3 style={{ marginTop: 0, }}> weather for the next 7 days</h3>

              <div style={{ display: 'flex', gap: '12px' }}>

                {moredatatoknow.map((d, i) => (
                  <div key={i} style={{ 
                    minWidth: '120px', 
                    textAlign: 'center', 
                    backgroundColor: 'white',
                    border: '1px solid ', 
                  }}>
                    <p >{d.date_str} </p>
                    <h2 >{Math.round(d.temperatureAVG)} C</h2>
                    {d.isstressed && <p style={{ color: 'red', fontWeight: 'bold' }}>stress</p>}
                  </div>
                ))}
              </div>  
            
          </div>

      )}

    </div>
  );
}