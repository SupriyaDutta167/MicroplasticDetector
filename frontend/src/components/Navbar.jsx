const Navbar = () => {
  return (
    <nav style={{
      background: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
      padding: '1rem 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span style={{ fontSize: '1.5rem' }}>🌊</span>
          <h1 style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#1890ff',
            margin: 0,
            letterSpacing: '-0.01em'
          }}>
            Microplastic Detector
          </h1>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          fontSize: '0.9rem',
          color: '#666',
          fontWeight: '500'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: 'linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%)',
            borderRadius: '20px',
            border: '1px solid #bae7ff'
          }}>
            <span>🔬</span>
            <span>Advanced Analysis</span>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.5rem 1rem',
            background: 'linear-gradient(135deg, #f6ffed 0%, #f0fff0 100%)',
            borderRadius: '20px',
            border: '1px solid #b7eb8f'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: '#52c41a',
              borderRadius: '50%',
              animation: 'pulse 2s infinite'
            }}></div>
            <span>System Active</span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;