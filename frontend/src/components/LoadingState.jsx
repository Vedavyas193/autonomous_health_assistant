import { useState, useEffect } from 'react'

const STEPS = [
  { label: 'Normalising symptoms',             duration: 600  },
  { label: 'Running ML ensemble',              duration: 1200 },
  { label: 'Retrieving medical context',       duration: 900  },
  { label: 'Assessing complexity',             duration: 700  },
  { label: 'Running collaborative agents',     duration: 1000 },
  { label: 'Synthesising with TinyLlama',      duration: 8000 },
]

export default function LoadingState() {
  const [currentStep, setCurrentStep] = useState(0)
  const [elapsed, setElapsed]         = useState(0)

  useEffect(() => {
    const timer = setInterval(() => setElapsed(e => e + 100), 100)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    let acc = 0
    const timeouts = STEPS.map((step, i) => {
      acc += step.duration
      return setTimeout(() => setCurrentStep(s => Math.max(s, i + 1)), acc)
    })
    return () => timeouts.forEach(clearTimeout)
  }, [])

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '14px',
        marginBottom: '24px', padding: '16px 20px',
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
      }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '50%', flexShrink: 0,
          border: '2.5px solid var(--teal)', borderTopColor: 'transparent',
          animation: 'spin 0.9s linear infinite',
        }}/>
        <div>
          <div style={{ fontWeight: 600, fontSize: '16px', marginBottom: '2px' }}>
            Analysing patient data
          </div>
          <div style={{ fontSize: '12px', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>
            {(elapsed / 1000).toFixed(1)}s elapsed · multi-agent pipeline active
          </div>
        </div>
      </div>

      {/* Steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {STEPS.map((step, i) => {
          const isDone    = i < currentStep
          const isActive  = i === currentStep
          const isPending = i > currentStep

          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '12px 16px', borderRadius: 'var(--radius)',
              background: isDone ? 'var(--teal-glow)' : isActive ? 'var(--surface2)' : 'var(--surface)',
              border: `1px solid ${isDone ? 'rgba(0,212,170,0.25)' : isActive ? 'var(--border2)' : 'var(--border)'}`,
              transition: 'all 0.4s ease',
              animation: `fadeUp 0.3s ease ${i * 0.08}s both`,
              opacity: isPending ? 0.4 : 1,
            }}>
              {/* Status indicator */}
              <div style={{
                width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: isDone ? 'var(--teal)' : 'transparent',
                border: isDone ? 'none' : isActive ? '2px solid var(--teal)' : '1px solid var(--border2)',
                transition: 'all 0.3s',
              }}>
                {isDone ? (
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5l2.5 2.5L8 2.5" stroke="var(--bg)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : isActive ? (
                  <div style={{
                    width: '8px', height: '8px', borderRadius: '50%',
                    background: 'var(--teal)', animation: 'pulse 1s ease-in-out infinite',
                  }}/>
                ) : (
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--border2)' }}/>
                )}
              </div>

              <span style={{
                fontSize: '13px', fontFamily: 'var(--mono)',
                color: isDone ? 'var(--teal)' : isActive ? 'var(--text)' : 'var(--text3)',
                transition: 'color 0.3s', flex: 1,
              }}>
                {step.label}
              </span>

              {isDone && (
                <span style={{ fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--teal)', opacity: 0.6 }}>
                  done
                </span>
              )}
              {isActive && (
                <div style={{
                  width: '14px', height: '14px', borderRadius: '50%',
                  border: '1.5px solid var(--teal)', borderTopColor: 'transparent',
                  animation: 'spin 0.7s linear infinite',
                }}/>
              )}
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div style={{
        marginTop: '20px', height: '3px',
        background: 'var(--border)', borderRadius: '2px', overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', background: 'var(--teal)',
          width: `${(currentStep / STEPS.length) * 100}%`,
          transition: 'width 0.6s ease',
          boxShadow: '0 0 10px var(--teal)',
        }}/>
      </div>
    </div>
  )
}