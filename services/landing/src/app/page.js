import React from 'react';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem',
      background: 'radial-gradient(circle at top, #1f2833 0%, #0b0c10 100%)',
      textAlign: 'center'
    }}>
      <main style={{
        maxWidth: '800px',
        padding: '3rem',
        borderRadius: '16px',
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)'
      }}>
        <h1 style={{
          fontSize: '3rem',
          margin: '0 0 1rem 0',
          background: 'linear-gradient(90deg, #66fcf1, #45a29e)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: '800',
          letterSpacing: '1px'
        }}>
          HairIQ
        </h1>
        <p style={{
          fontSize: '1.25rem',
          color: '#c5c6c7',
          lineHeight: '1.6',
          margin: '0 0 2rem 0'
        }}>
          Premium AI-powered Hair Analysis & Styling Platform. Discover custom cuts, styling insights, and customized routines tailored specifically to your unique profile.
        </p>
        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <a href="/analyze" style={{
            padding: '0.8rem 2rem',
            borderRadius: '50px',
            backgroundColor: '#66fcf1',
            color: '#0b0c10',
            textDecoration: 'none',
            fontWeight: '600',
            transition: 'transform 0.2s, box-shadow 0.2s',
            boxShadow: '0 4px 15px rgba(102, 252, 241, 0.3)'
          }}>
            Try AI Analyzer
          </a>
          <a href="/admin" style={{
            padding: '0.8rem 2rem',
            borderRadius: '50px',
            border: '2px solid #45a29e',
            color: '#66fcf1',
            textDecoration: 'none',
            fontWeight: '600',
            transition: 'background 0.2s'
          }}>
            Admin Panel
          </a>
        </div>
      </main>
      <footer style={{
        marginTop: '3rem',
        fontSize: '0.85rem',
        color: '#45a29e'
      }}>
        © {new Date().getFullYear()} HairIQ. All rights reserved.
      </footer>
    </div>
  );
}
