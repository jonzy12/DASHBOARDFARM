import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';

export default function FarmDashboard({ setUser }) {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState({ fields: [], stress: null, ndvi: [], et0: [], growth: [], farmScore: null ,totalHectares: 0});

  useEffect(() => {
    const loadAllData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/');
        return;
      }

      setIsLoading(true);
      try {
        const headers = { 'Authorization': `Bearer ${token}` };

        const [fieldsRes, stressChartRes, ndviRes, et0Res, stressDaysRes, effectedHectaresRes, growthRes, scoreRes,totalHectares ] = await Promise.all([
          fetch('http://localhost:8000/fields', { headers }),
          fetch('http://localhost:8000/farm/stress-graph', { headers }),
          fetch('http://localhost:8000/farm/ndvi-summary', { headers }),
          fetch('http://localhost:8000/farm/et0-summary', { headers }),
          fetch('http://localhost:8000/farm/amount-of-stressdays', { headers }),
          fetch('http://localhost:8000/farm/effected-hectares', { headers }),
          fetch('http://localhost:8000/farm/growth-stage-summary', { headers }),
          fetch('http://localhost:8000/farm/score', { headers }),
          fetch('http://localhost:8000/farm/sum-of-area-hactares', { headers })

        ]);

        const fieldsData = fieldsRes.ok ? await fieldsRes.json() : [];
        const stressChartData = stressChartRes.ok ? await stressChartRes.json() : { chartData: [] };
        const ndviData = ndviRes.ok ? await ndviRes.json() : [];
        const et0Data = et0Res.ok ? await et0Res.json() : [];
        const stressDaysData = stressDaysRes.ok ? await stressDaysRes.json() : { stressdays: 0 };
        const effectedHectaresData = effectedHectaresRes.ok ? await effectedHectaresRes.json() : { effected_hectares: 0, effected_percentage: 0 };
        const growthData = growthRes.ok ? await growthRes.json() : [];
        const scoreData = scoreRes.ok ? await scoreRes.json() : { score: 0, out_of_number: 0 };
        const totalHectaresData = totalHectares.ok ? await totalHectares.json() : { totalAreaHectares: 0 };

        setData({
          fields: fieldsData,
          stress: {
            chartData: stressChartData.chartData || [],
            stressSummary: {
              days: stressDaysData.stressdays || 0,
              effectedHectares: effectedHectaresData.effected_hectares || 0,
              effectedPercentage: effectedHectaresData.effected_percentage || 0
            }
          },
          ndvi: ndviData,
          et0: et0Data,
          growth: growthData,
          farmScore: scoreData,
          totalHectares: (totalHectaresData.totalAreaHectares || 0).toFixed(2)
        });

      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
      setIsLoading(false);
    };

    loadAllData();}, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/');
  };


  return (
    <div style={{ padding: '20px', backgroundColor: 'lightgray', minHeight: '100vh' }}>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid black', paddingBottom: '10px' }}>
        <div>
          <h1 style={{ margin: 0 }}>Farm Dashboard</h1>
          
          {data.farmScore && data.farmScore.score && (
            <h3 style={{ color: 'blue' }}>
               farm score: {Number(data.farmScore.score).toFixed(2)} / {data.farmScore.out_of_number}
            </h3>
          )}
        </div>  
        <div>
          <button style={{ marginRight: '10px', padding: '10px' }} onClick={() => navigate('/fieldlist-dashboard')}>manage fields</button>
          <button style={{ backgroundColor: 'red', color: 'white', padding: '10px' }} onClick={handleLogout}>log out</button>
        </div>
      </div>

      {isLoading ? (<p>loading</p>) : (
        <div>

          
          <div style={{ display: 'flex', gap: '10px', marginTop: '20px', marginBottom: '20px' }}>
            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '10px' }}>
              <p>total fields</p>
              <h3>{data.fields.length}</h3>
            </div>
            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '10px' }}>
              <p>total area</p>
              <h3>{data.totalHectares} ha</h3>
            </div>
            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '10px', color: 'red' }}>
              <p>stress days</p>
              <h3>{data.stress?.stressSummary?.days || 0}</h3>
            </div>
            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '10px', color: 'red' }}>
              <p>effected area %</p>
              <h3>{data.stress?.stressSummary?.effectedPercentage || 0}%</h3>
            </div>
            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '10px', color: 'red' }}>
              <p>effected area ha</p>
              <h3>{data.stress?.stressSummary?.effectedHectares || 0} ha</h3>
            </div>
          </div>

          <div style={{ backgroundColor: 'white', border: '1px solid black', padding: '15px', marginBottom: '20px' }}>
            <h3>temperature stress</h3>
            <div style={{ height: '300px',}}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.stress?.chartData.map(d => ({...d,total_stress: d.high_stress || d.low_stress ? 1 : 0 })) || []}>

                  <XAxis dataKey="date_str" />
                  <Tooltip />
                  <Legend />
                  
                  <Bar dataKey="total_stress" name="Stress" fill="blue" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
            
            <div style={{ backgroundColor: 'white' }}>
              <h3>crop health trends</h3>
                
                <PieChart width={300} height={300}>
                  <Pie data={data.ndvi} dataKey="value">
                    {data.ndvi.map((item, i) => ( <Cell key={i} fill={item.color} />))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>

            </div>

            <div style={{ flex: 1, backgroundColor: 'white', border: '1px solid black', padding: '15px' }}>
              <h3>precipitation against evaportion</h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.et0}>
                    <XAxis dataKey="date_str" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="et0" name="ET0" fill="red" />
                    <Bar dataKey="precip" name="Precipitation" fill="blue" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          <div style={{ backgroundColor: 'white', border: '1px solid black', padding: '15px' }}>
            <h3>all fields growth stages</h3>
            <div style={{ height: '300px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.growth}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="hectares" name="Hectares" fill="lightgreen" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}