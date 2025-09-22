import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#1890ff", "#52c41a"];

const StatsPanel = ({ stats, isLive }) => {
  if (!stats) {
    return (
      <div className="stats-panel">
        <div className="no-image">
          <div className="no-image-icon">📊</div>
          <span>
            {isLive 
              ? 'Waiting for live data...' 
              : 'No analysis data available'
            }
          </span>
          <small style={{ opacity: 0.7, marginTop: '0.5rem' }}>
            {isLive 
              ? 'Live statistics will appear here' 
              : 'Upload an image to see analysis results'
            }
          </small>
        </div>
      </div>
    );
  }

  const particleCount = stats.objects || stats.count || 0;
  const waterPercent = stats.percent_water || 100 - (stats.percent_plastic || 0);
  const plasticPercent = stats.percent_plastic || (stats.count && stats.water_ml ? (stats.count / (stats.count + stats.water_ml) * 100) : 0);

  const data = [
    { name: "Water", value: waterPercent },
    { name: "Microplastics", value: plasticPercent },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          border: '1px solid #e8e8e8',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(10px)'
        }}>
          <p style={{ color: payload[0].color, fontWeight: 600, margin: 0 }}>
            {`${payload[0].name}: ${payload[0].value.toFixed(1)}%`}
          </p>
        </div>
      );
    }
    return null;
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 5) return null; // Don't show labels for very small slices
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight={600}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="stats-panel">
      {/* Chart */}
      <div className="stats-chart-container">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={90}
              fill="#8884d8"
              dataKey="value"
              animationBegin={0}
              animationDuration={800}
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[index % COLORS.length]}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              wrapperStyle={{
                paddingTop: '20px',
                fontSize: '14px',
                fontWeight: '600'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Stats */}
      <div className="stats-text">
        <div className="stat-item">
          <span>🔍 Particles Detected</span>
          <span className="stat-value">{particleCount}</span>
        </div>
        
        <div className="stat-item">
          <span>💧 Water Content</span>
          <span className="stat-value">{waterPercent.toFixed(1)}%</span>
        </div>
        
        <div className="stat-item">
          <span>🧪 Microplastic Content</span>
          <span className="stat-value" style={{ color: plasticPercent > 50 ? '#ff4d4f' : '#52c41a' }}>
            {plasticPercent.toFixed(1)}%
          </span>
        </div>

        <div className="stat-item">
          <span>📏 Particle Density</span>
          <span className="stat-value">
            {stats.density ? `${stats.density.toFixed(2)} particles/mL` : 
             particleCount > 0 ? `${(particleCount / 100).toFixed(2)} particles/mL` : 'N/A'}
          </span>
        </div>
        {/* Quality Assessment */}
        <div className="stat-item" style={{ 
          background: plasticPercent > 10 ? 
            'linear-gradient(135deg, #fff2f0 0%, #ffebe6 100%)' : 
            'linear-gradient(135deg, #f6ffed 0%, #f0fff0 100%)',
          border: `1px solid ${plasticPercent > 10 ? '#ffccc7' : '#b7eb8f'}`,
          color: plasticPercent > 10 ? '#cf1322' : '#389e0d'
        }}>
          <span>🎯 Water Quality</span>
          <span className="stat-value" style={{ 
            color: plasticPercent > 10 ? '#cf1322' : '#389e0d',
            fontWeight: 700
          }}>
            {plasticPercent > 10 ? 'Poor' : 'Good'}
          </span>
        </div>


        {/* Live indicator for live mode */}
        {isLive && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            marginTop: '1rem' 
          }}>
            <div className="live-indicator" style={{ fontSize: '0.85rem' }}>
              <div className="live-dot"></div>
              Real-time Analysis
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsPanel;