import { useState } from 'react'

const TABS = [
  { id: 'overview',  label: 'Overview'  },
  { id: 'testing',   label: 'Testing'   },
  { id: 'treatment', label: 'Treatment' },
  { id: 'referral',  label: 'Referral'  },
  { id: 'details',   label: 'Details'   },
]

function Badge({ label, color = 'teal', size = 'sm' }) {
  const c = {
    teal:   { bg: 'rgba(0,212,170,0.12)',   border: 'rgba(0,212,170,0.3)',   text: 'var(--teal)'   },
    red:    { bg: 'rgba(255,87,87,0.12)',   border: 'rgba(255,87,87,0.3)',   text: 'var(--red)'    },
    amber:  { bg: 'rgba(255,179,64,0.12)',  border: 'rgba(255,179,64,0.3)', text: 'var(--amber)'  },
    blue:   { bg: 'rgba(77,159,255,0.12)',  border: 'rgba(77,159,255,0.3)', text: 'var(--blue)'   },
    purple: { bg: 'rgba(167,139,250,0.12)', border: 'rgba(167,139,250,0.3)',text: 'var(--purple)' },
    gray:   { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)',text: 'var(--text2)'  },
  }[color] || {}
  return (
    <span style={{
      padding: size === 'lg' ? '4px 14px' : '2px 10px',
      borderRadius: '20px',
      fontSize: size === 'lg' ? '12px' : '11px',
      fontFamily: 'var(--mono)', fontWeight: 500,
      background: c.bg, border: `1px solid ${c.border}`, color: c.text,
      letterSpacing: '0.04em',
    }}>
      {label}
    </span>
  )
}

function Card({ children, style = {}, delay = 0 }) {
  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)', padding: '20px',
      animation: `fadeUp 0.4s ease ${delay}s both`,
      ...style,
    }}>
      {children}
    </div>
  )
}

function SectionLabel({ children }) {
  return (
    <div style={{
      fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)',
      letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '14px',
      display: 'flex', alignItems: 'center', gap: '8px',
    }}>
      <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}/>
      {children}
      <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}/>
    </div>
  )
}

// ── Tab: Overview ─────────────────────────────────────────────────────────────
function OverviewTab({ data }) {
  const confidenceColor = { high: 'teal', medium: 'amber', low: 'red' }[data.confidence_level] || 'gray'
  const riskColor       = { LOW: 'teal', MEDIUM: 'amber', HIGH: 'amber', EMERGENCY: 'red' }[data.risk_level] || 'gray'
  const complexityColor = { LOW: 'teal', MEDIUM: 'amber', HIGH: 'red' }[data.complexity?.level] || 'gray'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* Primary diagnosis hero */}
      <Card delay={0} style={{
        borderColor: data.is_emergency ? 'rgba(255,87,87,0.5)' : 'var(--border)',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: '-40px', right: '-40px',
          width: '180px', height: '180px', borderRadius: '50%',
          background: data.is_emergency
            ? 'rgba(255,87,87,0.04)'
            : 'rgba(0,212,170,0.04)',
          pointerEvents: 'none',
        }}/>

        {data.is_emergency && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            padding: '8px 12px', background: 'var(--red-dim)',
            border: '1px solid rgba(255,87,87,0.3)', borderRadius: '8px',
            marginBottom: '16px',
          }}>
            <div style={{
              width: '8px', height: '8px', borderRadius: '50%',
              background: 'var(--red)',
              animation: 'pulse 1s ease-in-out infinite', flexShrink: 0,
            }}/>
            <span style={{ fontSize: '12px', color: 'var(--red)', fontWeight: 600 }}>
              EMERGENCY — Seek immediate medical attention
            </span>
          </div>
        )}

        <div style={{
          fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)',
          marginBottom: '6px', letterSpacing: '0.08em',
        }}>
          PRIMARY DIAGNOSIS
        </div>
        <div style={{
          fontFamily: 'var(--font)', fontSize: '30px', fontWeight: 700,
          letterSpacing: '-0.03em',
          color: data.is_emergency ? 'var(--red)' : 'var(--teal)',
          marginBottom: '12px', lineHeight: 1.1,
        }}>
          {data.primary_disease}
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '18px' }}>
          <Badge label={`${data.confidence_level?.toUpperCase()} CONFIDENCE`} color={confidenceColor} size="lg"/>
          <Badge label={`${data.model_agreement}/3 MODELS`}
            color={data.model_agreement === 3 ? 'teal' : data.model_agreement === 2 ? 'amber' : 'red'} size="lg"/>
          <Badge label={data.risk_level} color={riskColor} size="lg"/>
          {data.complexity?.level && <Badge label={data.complexity.level} color={complexityColor} size="lg"/>}
        </div>

        <div style={{
          padding: '16px', background: 'var(--bg2)',
          borderRadius: '10px', borderLeft: '3px solid var(--teal)',
          fontSize: '13.5px', color: 'var(--text2)', lineHeight: 1.75,
          marginBottom: '16px',
        }}>
          {data.diagnosis_summary || 'Generating summary...'}
        </div>

        {/* Meta row */}
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          {[
            ['Latency',  data.total_ms ? `${data.total_ms}ms` : '—'],
            ['HMAC',     data.hmac_valid ? 'Verified ✓' : 'Failed ✗'],
            ['Pipeline', data.pipeline_version],
            ['Patient',  data.patient_id?.slice(0, 10)],
          ].map(([k, v]) => (
            <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <span style={{
                fontSize: '10px', fontFamily: 'var(--mono)',
                color: 'var(--text3)', letterSpacing: '0.06em',
              }}>
                {k.toUpperCase()}
              </span>
              <span style={{
                fontSize: '12px', fontFamily: 'var(--mono)',
                color: k === 'HMAC'
                  ? data.hmac_valid ? 'var(--teal)' : 'var(--red)'
                  : 'var(--text2)',
              }}>
                {v}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Model breakdown */}
      {data.model_breakdown && (
        <Card delay={0.04}>
          <SectionLabel>Ensemble model breakdown</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '8px' }}>
            {[
              { label: 'Random Forest',  value: data.model_breakdown.rf_model_prediction,    color: 'var(--teal)'   },
              { label: 'Gradient Boost', value: data.model_breakdown.svm_model_prediction,   color: 'var(--blue)'   },
              { label: 'Naive Bayes',    value: data.model_breakdown.naive_bayes_prediction,  color: 'var(--purple)' },
              { label: 'Final vote',     value: data.model_breakdown.final_prediction,        color: 'var(--teal)', highlight: true },
            ].map((m, i) => (
              <div key={i} style={{
                padding: '12px', borderRadius: '10px',
                background: m.highlight ? 'var(--teal-glow)' : 'var(--bg2)',
                border: `1px solid ${m.highlight ? 'rgba(0,212,170,0.25)' : 'var(--border)'}`,
                animation: `fadeUp 0.3s ease ${i * 0.06}s both`,
              }}>
                <div style={{
                  fontSize: '10px', fontFamily: 'var(--mono)',
                  color: 'var(--text3)', marginBottom: '6px',
                  letterSpacing: '0.06em',
                }}>
                  {m.label.toUpperCase()}
                </div>
                <div style={{
                  fontSize: '12px', fontWeight: m.highlight ? 600 : 400,
                  color: m.highlight ? 'var(--teal)' : 'var(--text)',
                  lineHeight: 1.35,
                }}>
                  {m.value || '—'}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Top-K probabilities */}
      <Card delay={0.08}>
        <SectionLabel>Disease probability distribution</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {(data.top_k_diseases || []).map((d, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              animation: `slideIn 0.3s ease ${i * 0.07}s both`,
            }}>
              <span style={{
                fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)',
                width: '14px', textAlign: 'right', flexShrink: 0,
              }}>
                {d.rank}
              </span>
              <div style={{
                flex: 1, position: 'relative', height: '32px',
                background: 'var(--bg2)', borderRadius: '6px', overflow: 'hidden',
              }}>
                <div style={{
                  position: 'absolute', left: 0, top: 0, bottom: 0,
                  width: `${(d.probability * 100).toFixed(1)}%`,
                  background: i === 0
                    ? 'linear-gradient(90deg, rgba(0,212,170,0.2), rgba(0,212,170,0.06))'
                    : 'rgba(255,255,255,0.03)',
                  borderRight: i === 0 ? '2px solid var(--teal)' : '1px solid var(--border2)',
                  transition: 'width 1s ease',
                  '--w': `${(d.probability * 100).toFixed(1)}%`,
                }}/>
                <span style={{
                  position: 'absolute', left: '12px', top: '50%',
                  transform: 'translateY(-50%)', fontSize: '12px',
                  color: i === 0 ? 'var(--teal)' : 'var(--text2)',
                  fontWeight: i === 0 ? 500 : 400,
                }}>
                  {d.disease}
                </span>
              </div>
              <span style={{
                fontSize: '12px', fontFamily: 'var(--mono)', color: 'var(--text2)',
                width: '44px', textAlign: 'right', flexShrink: 0,
              }}>
                {(d.probability * 100).toFixed(1)}%
              </span>
              <div style={{ display: 'flex', gap: '3px', flexShrink: 0 }}>
                {[0, 1, 2].map(j => (
                  <div key={j} style={{
                    width: '6px', height: '6px', borderRadius: '50%',
                    background: j < (d.votes || 0) ? 'var(--teal)' : 'var(--border2)',
                  }}/>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Complexity */}
      {data.complexity && (
        <Card delay={0.12}>
          <SectionLabel>Case complexity</SectionLabel>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div style={{
              padding: '12px 16px', background: 'var(--bg2)', borderRadius: '10px',
              border: `1px solid ${
                data.complexity.level === 'HIGH'   ? 'rgba(255,87,87,0.3)'   :
                data.complexity.level === 'MEDIUM' ? 'rgba(255,179,64,0.3)' :
                'rgba(0,212,170,0.3)'
              }`, flexShrink: 0,
            }}>
              <div style={{
                fontSize: '10px', fontFamily: 'var(--mono)',
                color: 'var(--text3)', marginBottom: '4px',
              }}>
                COMPLEXITY
              </div>
              <div style={{
                fontSize: '22px', fontWeight: 700,
                color: data.complexity.level === 'HIGH'   ? 'var(--red)'   :
                       data.complexity.level === 'MEDIUM' ? 'var(--amber)' : 'var(--teal)',
              }}>
                {data.complexity.level}
              </div>
              <div style={{
                fontSize: '11px', fontFamily: 'var(--mono)',
                color: 'var(--text3)', marginTop: '2px',
              }}>
                score {data.complexity.score}/100
              </div>
            </div>
            <div style={{ flex: 1 }}>
              {data.complexity.systems_involved?.length > 0 && (
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
                  {data.complexity.systems_involved.map(s => (
                    <Badge key={s} label={s} color="blue"/>
                  ))}
                </div>
              )}
              <div style={{ fontSize: '13px', color: 'var(--text2)', lineHeight: 1.6 }}>
                {data.complexity.reasoning}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Red flags */}
      {data.red_flags?.length > 0 && (
        <Card delay={0.16} style={{ borderColor: 'rgba(255,87,87,0.4)' }}>
          <SectionLabel>Red flags</SectionLabel>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {data.red_flags.map((f, i) => (
              <Badge key={i} label={f.replace(/_/g, ' ')} color="red"/>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}

// ── Tab: Testing ──────────────────────────────────────────────────────────────
function TestingTab({ data }) {
  if (!data.testing?.requires_testing) {
    return (
      <Card delay={0}>
        <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text2)' }}>
          <div style={{
            width: '48px', height: '48px', borderRadius: '50%',
            background: 'var(--teal-glow)', border: '1px solid rgba(0,212,170,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 14px',
          }}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <path d="M4 11l5 5L18 6" stroke="var(--teal)" strokeWidth="2"
                strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 500, color: 'var(--teal)', marginBottom: '6px' }}>
            No further testing required
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text3)' }}>
            The diagnostic ensemble has sufficient confidence for a clinical assessment.
          </div>
        </div>
      </Card>
    )
  }

  const URGENCY_CONFIG = {
    IMMEDIATE:   { color: 'var(--red)',   bg: 'rgba(255,87,87,0.1)',   label: 'Immediate'   },
    WITHIN_24H:  { color: 'var(--amber)', bg: 'rgba(255,179,64,0.1)', label: 'Within 24h'  },
    WITHIN_WEEK: { color: 'var(--teal)',  bg: 'rgba(0,212,170,0.1)',  label: 'Within week' },
    ROUTINE:     { color: 'var(--text2)', bg: 'rgba(255,255,255,0.05)',label: 'Routine'     },
  }

  const TYPE_COLOR = {
    BLOOD: '#ff5757', IMAGING: '#4d9fff', URINE: '#ffb340',
    STOOL: '#a78bfa', SWAB:    '#00d4aa', ECG:   '#f472b6',
    OTHER: '#7a8fa8',
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card delay={0} style={{ borderColor: 'rgba(255,179,64,0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px', flexShrink: 0,
            background: 'var(--amber-dim)', border: '1px solid rgba(255,179,64,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="9" cy="9" r="7.5" stroke="var(--amber)" strokeWidth="1.2"/>
              <path d="M9 5v5M9 12.5v.5" stroke="var(--amber)" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '15px', color: 'var(--amber)', marginBottom: '4px' }}>
              Further Testing Required
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text2)', lineHeight: 1.6 }}>
              {data.testing.testing_rationale}
            </div>
          </div>
        </div>
      </Card>

      <Card delay={0.05}>
        <SectionLabel>Recommended tests for {data.testing.primary_disease}</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {data.testing.tests.map((t, i) => {
            const urg = URGENCY_CONFIG[t.urgency] || URGENCY_CONFIG.ROUTINE
            const tc  = TYPE_COLOR[t.test_type] || '#7a8fa8'
            return (
              <div key={i} style={{
                display: 'flex', gap: '12px', alignItems: 'flex-start',
                padding: '14px', background: 'var(--bg2)', borderRadius: '10px',
                border: '1px solid var(--border)',
                animation: `fadeUp 0.3s ease ${i * 0.05}s both`,
                transition: 'border-color 0.2s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border2)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                <div style={{
                  width: '36px', height: '36px', borderRadius: '8px', flexShrink: 0,
                  background: tc + '18', border: `1px solid ${tc}33`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '10px', fontFamily: 'var(--mono)', fontWeight: 600,
                  color: tc,
                }}>
                  {t.test_type.slice(0, 2)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: 500, fontSize: '13px',
                    color: 'var(--text)', marginBottom: '3px',
                  }}>
                    {t.test_name}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text2)', lineHeight: 1.5 }}>
                    {t.reason}
                  </div>
                </div>
                <span style={{
                  padding: '3px 10px', borderRadius: '20px', fontSize: '10px',
                  fontFamily: 'var(--mono)', fontWeight: 500, flexShrink: 0,
                  background: urg.bg, color: urg.color,
                  border: `1px solid ${urg.color}33`,
                }}>
                  {urg.label}
                </span>
              </div>
            )
          })}
        </div>
      </Card>

      {data.testing.differential_tests?.length > 0 && (
        <Card delay={0.1}>
          <SectionLabel>Differential — also rule out</SectionLabel>
          {data.testing.differential_tests.map((d, i) => (
            <div key={i} style={{
              padding: '12px', background: 'var(--bg2)', borderRadius: '10px',
              border: '1px solid var(--border)', marginBottom: '8px',
              animation: `fadeUp 0.3s ease ${0.1 + i * 0.05}s both`,
            }}>
              <div style={{
                display: 'flex', alignItems: 'center',
                gap: '10px', marginBottom: '10px',
              }}>
                <span style={{ fontWeight: 500, fontSize: '13px', color: 'var(--text)' }}>
                  {d.disease}
                </span>
                <span style={{
                  fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)',
                }}>
                  {(d.probability * 100).toFixed(1)}%
                </span>
              </div>
              {d.tests.map((t, j) => (
                <div key={j} style={{
                  display: 'flex', gap: '8px', padding: '6px 0',
                  borderTop: j > 0 ? '1px solid var(--border)' : 'none',
                  fontSize: '12px', color: 'var(--text2)',
                }}>
                  <span style={{ color: 'var(--teal)', flexShrink: 0 }}>▸</span>
                  <span style={{ fontWeight: 500, color: 'var(--text)' }}>{t.test_name}</span>
                  <span style={{ color: 'var(--text3)' }}>— {t.reason}</span>
                </div>
              ))}
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}

// ── Tab: Treatment ────────────────────────────────────────────────────────────
function TreatmentTab({ data }) {
  const plan = data.treatment_plan

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {data.suggested_precautions?.length > 0 && (
        <Card delay={0}>
          <SectionLabel>Suggested precautions</SectionLabel>
          {data.suggested_precautions.map((p, i) => (
            <div key={i} style={{
              display: 'flex', gap: '12px', padding: '12px 0',
              borderBottom: i < data.suggested_precautions.length - 1
                ? '1px solid var(--border)' : 'none',
              animation: `slideIn 0.3s ease ${i * 0.07}s both`,
            }}>
              <div style={{
                width: '22px', height: '22px', borderRadius: '50%', flexShrink: 0,
                background: 'var(--teal-glow)', border: '1px solid rgba(0,212,170,0.3)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--teal)',
                marginTop: '1px',
              }}>
                {i + 1}
              </div>
              <span style={{ fontSize: '13px', color: 'var(--text2)', lineHeight: 1.6 }}>{p}</span>
            </div>
          ))}
        </Card>
      )}

      {plan ? (
        <>
          {plan.immediate_actions?.length > 0 && (
            <Card delay={0.05} style={{ borderColor: 'rgba(255,87,87,0.3)' }}>
              <SectionLabel>Immediate actions</SectionLabel>
              {plan.immediate_actions.map((a, i) => (
                <div key={i} style={{
                  display: 'flex', gap: '12px', padding: '10px 0',
                  borderBottom: i < plan.immediate_actions.length - 1
                    ? '1px solid var(--border)' : 'none',
                  animation: `slideIn 0.3s ease ${i * 0.07}s both`,
                }}>
                  <span style={{
                    fontFamily: 'var(--mono)', fontSize: '11px',
                    color: 'var(--red)', flexShrink: 0, marginTop: '2px',
                  }}>
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span style={{ fontSize: '13px', color: 'var(--text)', lineHeight: 1.6 }}>{a}</span>
                </div>
              ))}
            </Card>
          )}

          {plan.lifestyle_advice?.length > 0 && (
            <Card delay={0.1}>
              <SectionLabel>Lifestyle advice</SectionLabel>
              {plan.lifestyle_advice.map((a, i) => (
                <div key={i} style={{
                  display: 'flex', gap: '10px', padding: '8px 0',
                  borderBottom: i < plan.lifestyle_advice.length - 1
                    ? '1px solid var(--border)' : 'none',
                  fontSize: '13px', color: 'var(--text2)',
                  animation: `slideIn 0.3s ease ${i * 0.07}s both`,
                }}>
                  <span style={{ color: 'var(--teal)', flexShrink: 0 }}>→</span>
                  {a}
                </div>
              ))}
            </Card>
          )}

          <Card delay={0.15}>
            <SectionLabel>Follow-up</SectionLabel>
            <div style={{
              padding: '14px', background: 'var(--bg2)', borderRadius: '8px',
              fontSize: '14px', color: 'var(--text)',
              borderLeft: '3px solid var(--teal)',
            }}>
              {plan.follow_up}
            </div>
          </Card>
        </>
      ) : (
        !data.suggested_precautions?.length && (
          <Card delay={0}>
            <div style={{
              textAlign: 'center', padding: '32px',
              color: 'var(--text3)', fontSize: '13px',
            }}>
              Treatment plan not available for this case.
            </div>
          </Card>
        )
      )}
    </div>
  )
}

// ── Tab: Referral ─────────────────────────────────────────────────────────────
function ReferralTab({ data }) {
  const ref = data.referral
  if (!ref) return (
    <Card delay={0}>
      <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text3)', fontSize: '13px' }}>
        No referral data available.
      </div>
    </Card>
  )

  const urgencyConfig = {
    IMMEDIATE: {
      color: 'var(--red)',   bg: 'var(--red-dim)',
      icon: <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="var(--red)" strokeWidth="1.5"/><path d="M10 6v5M10 13.5v.5" stroke="var(--red)" strokeWidth="1.8" strokeLinecap="round"/></svg>,
    },
    URGENT: {
      color: 'var(--amber)', bg: 'var(--amber-dim)',
      icon: <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 3L18 17H2L10 3Z" stroke="var(--amber)" strokeWidth="1.5" strokeLinejoin="round"/><path d="M10 9v4M10 14.5v.5" stroke="var(--amber)" strokeWidth="1.5" strokeLinecap="round"/></svg>,
    },
    ROUTINE: {
      color: 'var(--teal)',  bg: 'var(--teal-glow)',
      icon: <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="4" width="14" height="14" rx="3" stroke="var(--teal)" strokeWidth="1.5"/><path d="M7 9h6M7 12h4" stroke="var(--teal)" strokeWidth="1.5" strokeLinecap="round"/><path d="M7 2v4M13 2v4" stroke="var(--teal)" strokeWidth="1.5" strokeLinecap="round"/></svg>,
    },
  }[ref.urgency] || {
    color: 'var(--teal)', bg: 'var(--teal-glow)',
    icon: null,
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card delay={0} style={{ borderColor: urgencyConfig.color + '44' }}>
        <div style={{
          padding: '16px', background: urgencyConfig.bg,
          borderRadius: '10px', marginBottom: '16px',
          display: 'flex', alignItems: 'center', gap: '14px',
        }}>
          <div style={{
            width: '44px', height: '44px', borderRadius: '12px', flexShrink: 0,
            background: urgencyConfig.color + '15',
            border: `1px solid ${urgencyConfig.color}33`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {urgencyConfig.icon}
          </div>
          <div>
            <div style={{
              fontWeight: 700, fontSize: '18px',
              color: urgencyConfig.color, marginBottom: '2px',
            }}>
              {ref.urgency}
            </div>
            <div style={{
              fontSize: '11px', fontFamily: 'var(--mono)',
              color: 'var(--text3)', letterSpacing: '0.06em',
            }}>
              URGENCY LEVEL
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '14px' }}>
          <div style={{
            fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)',
            marginBottom: '6px', letterSpacing: '0.08em',
          }}>
            REFER TO
          </div>
          <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text)' }}>
            {ref.specialist}
          </div>
        </div>

        <div style={{
          padding: '14px', background: 'var(--bg2)', borderRadius: '10px',
          fontSize: '13px', color: 'var(--text2)', lineHeight: 1.7, marginBottom: '12px',
        }}>
          {ref.referral_note}
        </div>

        <div style={{
          padding: '12px 16px', background: 'var(--teal-glow)',
          border: '1px solid rgba(0,212,170,0.2)', borderRadius: '8px',
          fontSize: '13px', color: 'var(--teal)', fontWeight: 500,
          display: 'flex', alignItems: 'center', gap: '8px',
        }}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M7 4.5v3l2 1.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
          {ref.contact_advice}
        </div>
      </Card>

      {data.treatment_plan?.refer_to_specialist && (
        <Card delay={0.05}>
          <SectionLabel>Specialist type</SectionLabel>
          <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--teal)' }}>
            {data.treatment_plan.specialist_type}
          </div>
        </Card>
      )}
    </div>
  )
}

// ── Tab: Details ──────────────────────────────────────────────────────────────
function DetailsTab({ data }) {
  const [showRaw, setShowRaw] = useState(false)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {data.symptom_analysis && (
        <Card delay={0}>
          <SectionLabel>Symptom analysis</SectionLabel>
          <div style={{
            display: 'grid', gridTemplateColumns: '1fr 1fr',
            gap: '10px', marginBottom: '14px',
          }}>
            {[
              ['Dominant system', data.symptom_analysis.dominant_system?.replace(/_/g, ' ')],
              ['Severity score',  `${data.symptom_analysis.total_severity_score} pts`],
            ].map(([k, v]) => (
              <div key={k} style={{
                padding: '12px', background: 'var(--bg2)', borderRadius: '8px',
              }}>
                <div style={{
                  fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)',
                  marginBottom: '4px', letterSpacing: '0.08em', textTransform: 'uppercase',
                }}>
                  {k}
                </div>
                <div style={{
                  fontSize: '14px', fontWeight: 500,
                  color: 'var(--teal)', textTransform: 'capitalize',
                }}>
                  {v}
                </div>
              </div>
            ))}
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text2)', lineHeight: 1.6 }}>
            {data.symptom_analysis.pattern_notes}
          </div>
        </Card>
      )}

      {data.unknown_symptoms?.length > 0 && (
        <Card delay={0.05}>
          <SectionLabel>Unrecognised symptoms</SectionLabel>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
            {data.unknown_symptoms.map((s, i) => <Badge key={i} label={s} color="gray"/>)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text3)' }}>
            These symptoms were not found in the canonical symptom vocabulary and were excluded from analysis.
          </div>
        </Card>
      )}

      <button
        onClick={() => setShowRaw(v => !v)}
        style={{
          padding: '10px 16px', background: 'transparent',
          border: '1px solid var(--border)', borderRadius: '8px',
          color: 'var(--text3)', fontSize: '12px', fontFamily: 'var(--mono)',
          alignSelf: 'flex-start', transition: 'all 0.15s', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: '6px',
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--text2)' }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)';  e.currentTarget.style.color = 'var(--text3)' }}
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.5"
            strokeLinecap="round" strokeLinejoin="round"
            style={{ transform: showRaw ? 'rotate(180deg)' : 'none', transformOrigin: 'center' }}
          />
        </svg>
        {showRaw ? 'Hide' : 'Show'} raw JSON
      </button>

      {showRaw && (
        <pre style={{
          padding: '16px', background: 'var(--bg2)', border: '1px solid var(--border)',
          borderRadius: '10px', fontSize: '11px', fontFamily: 'var(--mono)',
          color: 'var(--text2)', overflowX: 'auto', lineHeight: 1.7,
          animation: 'fadeIn 0.2s ease',
        }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────
export default function DiagnosisResult({ data }) {
  const [activeTab, setActiveTab] = useState('overview')

  const availableTabs = TABS.filter(t => {
    if (t.id === 'testing'   && !data.testing?.requires_testing)                               return false
    if (t.id === 'treatment' && !data.suggested_precautions?.length && !data.treatment_plan)   return false
    return true
  })

  return (
    <div style={{ animation: 'fadeUp 0.4s ease' }}>

      {/* Tab bar */}
      <div style={{
        display: 'flex', gap: '2px', marginBottom: '20px',
        background: 'var(--surface)', borderRadius: '12px', padding: '4px',
        border: '1px solid var(--border)',
      }}>
        {availableTabs.map(tab => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: '8px 4px', borderRadius: '9px',
                fontSize: '13px', fontWeight: isActive ? 600 : 400,
                background: isActive ? 'var(--surface2)' : 'transparent',
                color: isActive ? 'var(--teal)' : 'var(--text2)',
                border: isActive ? '1px solid var(--border2)' : '1px solid transparent',
                transition: 'all 0.2s', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
              }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.color = 'var(--text)' }}
              onMouseLeave={e => { if (!isActive) e.currentTarget.style.color = 'var(--text2)' }}
            >
              {tab.label}
              {tab.id === 'testing' && data.testing?.requires_testing && (
                <span style={{
                  width: '6px', height: '6px', borderRadius: '50%',
                  background: 'var(--amber)', display: 'inline-block',
                  animation: 'pulse 2s ease-in-out infinite', flexShrink: 0,
                }}/>
              )}
              {tab.id === 'overview' && data.is_emergency && (
                <span style={{
                  width: '6px', height: '6px', borderRadius: '50%',
                  background: 'var(--red)', display: 'inline-block',
                  animation: 'pulse 1s ease-in-out infinite', flexShrink: 0,
                }}/>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <div key={activeTab} style={{ animation: 'fadeUp 0.25s ease' }}>
        {activeTab === 'overview'  && <OverviewTab  data={data}/>}
        {activeTab === 'testing'   && <TestingTab   data={data}/>}
        {activeTab === 'treatment' && <TreatmentTab data={data}/>}
        {activeTab === 'referral'  && <ReferralTab  data={data}/>}
        {activeTab === 'details'   && <DetailsTab   data={data}/>}
      </div>
    </div>
  )
}