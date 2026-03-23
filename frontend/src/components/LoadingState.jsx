export default function LoadingState() {
  const steps = [
    { label: 'Normalizing symptoms', done: true },
    { label: 'Running ML ensemble (SVM + NB + RF)', done: true },
    { label: 'Retrieving medical context (FAISS)', done: true },
    { label: 'Assessing complexity', done: false },
    { label: 'Running collaborative agents', done: false },
    { label: 'Synthesizing with TinyLlama', done: false },
  ]

  return (
    <div style={{ padding: '2rem', animation: 'fadeUp 0.4s ease' }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '2rem',
      }}>
        <div style={{
          width: '20px', height: '20px', border: '2px solid var(--teal)',
          borderTopColor: 'transparent', borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }}/>
        <span style={{ fontFamily: 'var(--font-head)', fontSize: '18px', fontWeight: 600 }}>
          Analysing patient data...
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {steps.map((step, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: '12px',
            padding: '12px 16px', borderRadius: '8px',
            background: 'var(--surface)',
            border: `1px solid ${step.done ? 'var(--teal-dim)' : 'var(--border)'}`,
            animation: `fadeUp 0.3s ease ${i * 0.1}s both`,
          }}>
            <div style={{
              width: '18px', height: '18px', borderRadius: '50%', flexShrink: 0,
              background: step.done ? 'var(--teal)' : 'var(--surface2)',
              border: `1px solid ${step.done ? 'var(--teal)' : 'var(--border2)'}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {step.done
                ? <svg width="10" height="10" viewBox="0 0 10 10"><path d="M2 5l2.5 2.5L8 3" stroke="var(--bg)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>
                : <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--border2)' }}/>
              }
            </div>
            <span style={{ fontSize: '13px', color: step.done ? 'var(--teal)' : 'var(--text3)', fontFamily: 'var(--font-mono)' }}>
              {step.label}
            </span>
            {!step.done && i === steps.findIndex(s => !s.done) && (
              <div style={{
                marginLeft: 'auto', width: '14px', height: '14px',
                border: '1.5px solid var(--teal)', borderTopColor: 'transparent',
                borderRadius: '50%', animation: 'spin 0.8s linear infinite',
              }}/>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}