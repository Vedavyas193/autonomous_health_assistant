import { useState, useEffect } from 'react'

const STEPS = [
  { label: 'Normalising symptoms',         duration: 600,  tag: 'NLP',       ms: '~0.6s'  },
  { label: 'Running ML ensemble',          duration: 1200, tag: 'RF+GB+NB',  ms: '~1.2s'  },
  { label: 'Retrieving medical context',   duration: 900,  tag: 'FAISS RAG', ms: '~0.9s'  },
  { label: 'Assessing complexity',         duration: 700,  tag: 'AGENT',     ms: '~0.7s'  },
  { label: 'Running collaborative agents', duration: 1000, tag: 'AGENT',     ms: '~1.0s'  },
  { label: 'Synthesising with TinyLlama',  duration: 8000, tag: 'LLM',       ms: '~8–15s' },
]

const TAG_COLORS = {
  'NLP':      { bg: 'rgba(167,139,250,0.1)', color: 'var(--purple)',  border: 'rgba(167,139,250,0.2)' },
  'RF+GB+NB': { bg: 'rgba(0,212,170,0.08)', color: 'var(--teal)',    border: 'rgba(0,212,170,0.15)'  },
  'FAISS RAG':{ bg: 'rgba(77,159,255,0.1)', color: 'var(--blue)',    border: 'rgba(77,159,255,0.2)'  },
  'AGENT':    { bg: 'rgba(255,179,64,0.1)', color: 'var(--amber)',   border: 'rgba(255,179,64,0.2)'  },
  'LLM':      { bg: 'rgba(255,87,87,0.08)', color: 'var(--red)',     border: 'rgba(255,87,87,0.15)'  },
}

export default function LoadingState() {
  const [currentStep, setCurrentStep] = useState(0)
  const [elapsed,     setElapsed]     = useState(0)

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

  const pct     = Math.round((currentStep / STEPS.length) * 100)
  const isLLM   = currentStep === 5
  const isDone  = currentStep === STEPS.length

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>

      {/* Header card */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '14px',
        marginBottom: '16px', padding: '16px 20px',
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
      }}>
        <div style={{
          width: '38px', height: '38px', borderRadius: '50%', flexShrink: 0,
          border: `2.5px solid ${isDone ? 'var(--teal)' : 'var(--teal)'}`,
          borderTopColor: isDone ? 'var(--teal)' : 'transparent',
          animation: isDone ? 'none' : 'spin 0.9s linear infinite',
          transition: 'all 0.3s',
        }}/>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: '15px', marginBottom: '3px' }}>
            {isDone ? 'Analysis complete' : 'Analysing patient data'}
          </div>
          <div style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>
            {(elapsed / 1000).toFixed(1)}s elapsed
            &nbsp;·&nbsp;
            {isDone
              ? 'all agents completed'
              : 'multi-agent pipeline active'
            }
          </div>
        </div>
        <div style={{
          fontSize: '18px', fontWeight: 700, fontFamily: 'var(--mono)',
          color: 'var(--teal)', minWidth: '44px', textAlign: 'right',
        }}>
          {pct}%
        </div>
      </div>

      {/* LLM warning banner */}
      {isLLM && (
        <div style={{
          display: 'flex', alignItems: 'flex-start', gap: '10px',
          padding: '10px 14px', marginBottom: '12px',
          background: 'rgba(255,179,64,0.06)',
          border: '1px solid rgba(255,179,64,0.2)',
          borderRadius: 'var(--radius)',
          animation: 'fadeIn 0.3s ease',
        }}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{ flexShrink: 0, marginTop: '1px' }}>
            <path d="M7 2L13 12H1L7 2Z" stroke="var(--amber)" strokeWidth="1.2" strokeLinejoin="round"/>
            <path d="M7 6v3M7 10.5v.5" stroke="var(--amber)" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
          <span style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--amber)', lineHeight: 1.6 }}>
            TinyLlama synthesis in progress — this step takes 8–15s on CPU. Please wait.
          </span>
        </div>
      )}

      {/* Steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
        {STEPS.map((step, i) => {
          const isDoneStep    = i < currentStep
          const isActiveStep  = i === currentStep
          const isPending     = i > currentStep
          const tagStyle      = TAG_COLORS[step.tag]

          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '11px 16px', borderRadius: 'var(--radius)',
              background: isDoneStep
                ? 'var(--teal-glow)'
                : isActiveStep
                  ? 'var(--surface2)'
                  : 'var(--surface)',
              border: `1px solid ${
                isDoneStep
                  ? 'rgba(0,212,170,0.2)'
                  : isActiveStep
                    ? 'var(--border2)'
                    : 'var(--border)'
              }`,
              transition: 'all 0.4s ease',
              animation: `fadeUp 0.3s ease ${i * 0.07}s both`,
              opacity: isPending ? 0.35 : 1,
            }}>

              {/* Status dot */}
              <div style={{
                width: '20px', height: '20px', borderRadius: '50%',
                flexShrink: 0, display: 'flex', alignItems: 'center',
                justifyContent: 'center',
                background: isDoneStep ? 'var(--teal)' : 'transparent',
                border: isDoneStep
                  ? 'none'
                  : isActiveStep
                    ? '2px solid var(--teal)'
                    : '1px solid var(--border2)',
                transition: 'all 0.3s',
              }}>
                {isDoneStep ? (
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5l2.5 2.5L8 2.5" stroke="var(--bg)" strokeWidth="1.8"
                      strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : isActiveStep ? (
                  <div style={{
                    width: '8px', height: '8px', borderRadius: '50%',
                    background: 'var(--teal)',
                    animation: 'pulse 1s ease-in-out infinite',
                  }}/>
                ) : (
                  <div style={{
                    width: '6px', height: '6px', borderRadius: '50%',
                    background: 'var(--border2)',
                  }}/>
                )}
              </div>

              {/* Label */}
              <span style={{
                fontSize: '12px', fontFamily: 'var(--mono)', flex: 1,
                color: isDoneStep
                  ? 'var(--teal)'
                  : isActiveStep
                    ? 'var(--text)'
                    : 'var(--text3)',
                transition: 'color 0.3s',
              }}>
                {step.label}
              </span>

              {/* Tag pill */}
              <span style={{
                fontSize: '9px', fontFamily: 'var(--mono)',
                padding: '2px 7px', borderRadius: '8px',
                background: tagStyle.bg,
                color: tagStyle.color,
                border: `1px solid ${tagStyle.border}`,
                letterSpacing: '0.06em',
              }}>
                {step.tag}
              </span>

              {/* Time estimate or spinner */}
              {isPending && (
                <span style={{
                  fontSize: '10px', fontFamily: 'var(--mono)',
                  color: 'var(--text3)', minWidth: '36px', textAlign: 'right',
                }}>
                  {step.ms}
                </span>
              )}
              {isDoneStep && (
                <span style={{
                  fontSize: '10px', fontFamily: 'var(--mono)',
                  color: 'var(--teal)', opacity: 0.6, minWidth: '36px', textAlign: 'right',
                }}>
                  done
                </span>
              )}
              {isActiveStep && (
                <div style={{
                  width: '13px', height: '13px', borderRadius: '50%', flexShrink: 0,
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
        marginTop: '16px', height: '3px',
        background: 'var(--border)', borderRadius: '2px', overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', background: 'var(--teal)',
          width: `${pct}%`,
          transition: 'width 0.6s ease',
          boxShadow: '0 0 8px var(--teal)',
        }}/>
      </div>

      {/* Step counter */}
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        marginTop: '8px',
        fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)',
      }}>
        <span>STEP {Math.min(currentStep + 1, STEPS.length)} OF {STEPS.length}</span>
        <span>{pct}% COMPLETE</span>
      </div>
    </div>
  )
}