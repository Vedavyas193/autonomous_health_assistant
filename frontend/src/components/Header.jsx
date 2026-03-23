import { useState, useEffect } from 'react'

export default function Header() {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(r => r.json())
      .then(d => setOnline(d.models_loaded))
      .catch(() => setOnline(false))
  }, [])

  return (
    <header style={{
      padding: '0 2.5rem', height: '60px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      borderBottom: '1px solid var(--border)',
      background: 'rgba(7,11,16,0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky', top: 0, zIndex: 200,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '30px', height: '30px', borderRadius: '8px',
          background: 'var(--teal)', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          animation: 'glow 3s ease-in-out infinite',
        }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 2v12M2 8h12" stroke="var(--bg)" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
        </div>
        <div>
          <div style={{
            fontFamily: 'var(--font)', fontSize: '16px', fontWeight: 700,
            letterSpacing: '-0.02em', lineHeight: 1,
          }}>
            MedTriage<span style={{ color: 'var(--teal)' }}>.ai</span>
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text3)', fontFamily: 'var(--mono)', letterSpacing: '0.05em' }}>
            AUTONOMOUS TRIAGE SYSTEM
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <div style={{ position: 'relative', width: '8px', height: '8px' }}>
            <div style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: online ? 'var(--teal)' : 'var(--red)',
            }}/>
            {online && <div style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: 'var(--teal)', animation: 'ping 1.5s ease-out infinite',
            }}/>}
          </div>
          <span style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text2)' }}>
            {online ? 'BACKEND READY' : 'BACKEND OFFLINE'}
          </span>
        </div>
        <div style={{
          padding: '4px 12px', borderRadius: '20px', fontSize: '11px',
          fontFamily: 'var(--mono)', background: 'var(--teal-glow)',
          border: '1px solid var(--teal2)', color: 'var(--teal)',
        }}>
          OFFLINE CAPABLE
        </div>
      </div>
    </header>
  )
}