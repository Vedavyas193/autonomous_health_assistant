import { useState, useEffect } from 'react'

export default function Header() {
  const [status, setStatus] = useState({ online: false, version: '2.0.0' })

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(r => r.json())
      .then(d => setStatus({
        online: d.models_loaded,
        version: d.pipeline_version || '2.0.0',
      }))
      .catch(() => setStatus({ online: false, version: '2.0.0' }))
  }, [])

  return (
    <header style={{
      padding: '0 2.5rem',
      height: '62px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid var(--border)',
      background: 'rgba(7,11,16,0.88)',
      backdropFilter: 'blur(14px)',
      WebkitBackdropFilter: 'blur(14px)',
      position: 'sticky',
      top: 0,
      zIndex: 200,
    }}>

      {/* ── Left — logo ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '9px',
          background: 'var(--teal)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
          animation: 'glow 3s ease-in-out infinite',
        }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 2v12M2 8h12" stroke="var(--bg)" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
        </div>

        <div>
          <div style={{
            fontFamily: 'var(--font)', fontSize: '16px', fontWeight: 700,
            letterSpacing: '-0.02em', lineHeight: 1.1,
            display: 'flex', alignItems: 'center', gap: '6px',
          }}>
            MedTriage<span style={{ color: 'var(--teal)' }}>.ai</span>
            <span style={{
              fontSize: '9px', fontFamily: 'var(--mono)',
              color: 'var(--text3)', background: 'var(--surface)',
              border: '1px solid var(--border)',
              padding: '1px 6px', borderRadius: '6px',
              letterSpacing: '0.06em',
            }}>
              v{status.version}
            </span>
          </div>
          <div style={{
            fontSize: '10px', color: 'var(--text3)',
            fontFamily: 'var(--mono)', letterSpacing: '0.06em',
            marginTop: '1px',
          }}>
            AUTONOMOUS TRIAGE SYSTEM
          </div>
        </div>
      </div>

      {/* ── Right — status ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>

        {/* Backend status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <div style={{ position: 'relative', width: '8px', height: '8px' }}>
            <div style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: status.online ? 'var(--teal)' : 'var(--red)',
            }}/>
            {status.online && (
              <div style={{
                position: 'absolute', inset: 0, borderRadius: '50%',
                background: 'var(--teal)',
                animation: 'ping 1.5s ease-out infinite',
              }}/>
            )}
          </div>
          <span style={{
            fontSize: '11px', fontFamily: 'var(--mono)',
            color: status.online ? 'var(--text2)' : 'var(--red)',
          }}>
            {status.online ? 'BACKEND READY' : 'BACKEND OFFLINE'}
          </span>
        </div>

        {/* Divider */}
        <div style={{ width: '1px', height: '20px', background: 'var(--border)' }}/>

        {/* Offline capable badge */}
        <div style={{
          padding: '4px 12px', borderRadius: '20px',
          fontSize: '11px', fontFamily: 'var(--mono)',
          background: 'var(--teal-glow)',
          border: '1px solid rgba(0,212,170,0.2)',
          color: 'var(--teal)',
          display: 'flex', alignItems: 'center', gap: '6px',
        }}>
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M5 1v4l2.5 2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
            <circle cx="5" cy="5" r="4" stroke="currentColor" strokeWidth="1"/>
          </svg>
          OFFLINE CAPABLE
        </div>

        {/* Pipeline info — only when online */}
        {status.online && (
          <div style={{
            padding: '4px 12px', borderRadius: '20px',
            fontSize: '11px', fontFamily: 'var(--mono)',
            background: 'rgba(77,159,255,0.08)',
            border: '1px solid rgba(77,159,255,0.15)',
            color: 'var(--blue)',
            display: 'flex', alignItems: 'center', gap: '5px',
          }}>
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
              <rect x="1" y="1" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1"/>
              <path d="M3 5h4M3 3.5h2M3 6.5h3" stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
            </svg>
            73 DISEASES · 180 SYMPTOMS
          </div>
        )}
      </div>
    </header>
  )
}