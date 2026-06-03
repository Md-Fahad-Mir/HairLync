import React from 'react';

export default function AdminDashboard() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#0d1117',
      color: '#c9d1d9',
      padding: '2rem'
    }}>
      <header style={{
        display: 'flex',
        justifyContent: 'between',
        alignItems: 'center',
        borderBottom: '1px solid #21262d',
        paddingBottom: '1rem',
        marginBottom: '2rem'
      }}>
        <h1 style={{
          fontSize: '1.8rem',
          margin: 0,
          background: 'linear-gradient(90deg, #58a6ff, #1f6feb)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: '700'
        }}>
          HairIQ Admin Console
        </h1>
        <div style={{
          display: 'flex',
          gap: '10px',
          alignItems: 'center',
          marginLeft: 'auto'
        }}>
          <span style={{
            display: 'inline-block',
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: '#3fb950'
          }}></span>
          <span>System Online</span>
        </div>
      </header>

      <main style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.5rem',
        alignContent: 'start'
      }}>
        <div style={{
          background: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h2 style={{ fontSize: '1rem', color: '#8b949e', margin: '0 0 0.5rem 0' }}>Total Analyzed Profiles</h2>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#58a6ff' }}>1,248</div>
          <span style={{ fontSize: '0.85rem', color: '#3fb950' }}>+12% from last week</span>
        </div>

        <div style={{
          background: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h2 style={{ fontSize: '1rem', color: '#8b949e', margin: '0 0 0.5rem 0' }}>AI Model Efficiency</h2>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#58a6ff' }}>98.2%</div>
          <span style={{ fontSize: '0.85rem', color: '#3fb950' }}>Active (GPT-4o / Claude 3.5)</span>
        </div>

        <div style={{
          background: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '1.5rem'
        }}>
          <h2 style={{ fontSize: '1rem', color: '#8b949e', margin: '0 0 0.5rem 0' }}>API Status</h2>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#3fb950' }}>Healthy</div>
          <span style={{ fontSize: '0.85rem', color: '#8b949e' }}>Average Latency: 124ms</span>
        </div>
      </main>

      <footer style={{
        marginTop: 'auto',
        paddingTop: '2rem',
        borderTop: '1px solid #21262d',
        fontSize: '0.85rem',
        color: '#8b949e',
        textAlign: 'center'
      }}>
        HairIQ Internal Admin Dashboard • Secure Operations
      </footer>
    </div>
  );
}
