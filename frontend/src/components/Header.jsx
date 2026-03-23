export default function Header() {
  return (
    <header style={{
      padding: '0 2rem',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid var(--border)',
      background: 'var(--bg)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '32px', height: '32px', borderRadius: '8px',
          background: 'var(--teal)', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M9 2v14M2 9h14" stroke="var(--bg)" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
        </div>
        <span style={{
          fontFamily: 'var(--font-head)', fontSize: '18px',
          fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text)',
        }}>
          MedTriage
          <span style={{ color: 'var(--teal)', marginLeft: '2px' }}>AI</span>
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          width: '8px', height: '8px', borderRadius: '50%',
          background: 'var(--teal)', position: 'relative',
        }}>
          <div style={{
            position: 'absolute', inset: 0, borderRadius: '50%',
            background: 'var(--teal)',
            animation: 'pulse-ring 2s ease-out infinite',
          }}/>
        </div>
        <span style={{ fontSize: '12px', color: 'var(--text2)', fontFamily: 'var(--font-mono)' }}>
          OFFLINE READY
        </span>
      </div>
    </header>
  )
}