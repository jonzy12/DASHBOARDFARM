
import React, { useState } from 'react';
import { MapContainer, TileLayer, FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';

export default function AddFieldMap({ onCancel, onSave }) {
  const [plotName, setPlotName] = useState('');
  const [cropType, setCropType] = useState('');
  const [area, setArea] = useState(0);
  const [centerLat, setCenterLat] = useState(0);
  const [centerLon, setCenterLon] = useState(0);

  const createdmap = (e) => {
    let lat = e.layer.getLatLng().lat;
    let lng = e.layer.getLatLng().lng;
    let radius = e.layer.getRadius();

    let calc = (Math.PI * radius * radius) / 10000;

    setArea(calc);
    setCenterLat(lat);
    setCenterLon(lng);
  };

  const saveClick = () => {

    if (area == 0 || plotName.trim() === '' || cropType.trim() === '')
    {
      alert("fill the missing things");
      return;
    }



    onSave({
      plot_name: plotName,
      crop_type: cropType,
      area_size_hectares: area,
      latitude: centerLat,
      longitude: centerLon
    });
  };

  return (
    <div style={{ display: 'flex', height: '100vh'}}>


      <div style={{ width: '60%' }}>
        <MapContainer center={[32.084226, 34.865809]} zoom={20} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" />
          <FeatureGroup>
            <EditControl
              position="topright"
              onCreated={createdmap}
              draw={{
                rectangle: false,
                polygon: false,
                polyline: false,
                circlemarker: false,
                marker: false,
                circle: true
              }}
            />
          </FeatureGroup>
        </MapContainer>
      </div>

      <div style={{padding: '20px', width: '40%' }}><strong>add field</strong>
        <p>field name:</p>
        <input value={plotName} onChange={(e) => setPlotName(e.target.value)} />

        <p>crop type:</p>
        <input value={cropType} onChange={(e) => setCropType(e.target.value)} />

       <p>area: {area.toFixed(2)} ha</p>
        <p>Lat: {centerLat.toFixed(5)}</p>
        <p>lon: {centerLon.toFixed(5)}</p>

        <br />
        <button onClick={onCancel} style={{ marginRight: '10px' }}>cancel</button>
        <button onClick={saveClick}>save</button>
      </div>

    </div>
  );
}