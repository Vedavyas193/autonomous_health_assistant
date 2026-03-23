import { useState } from 'react'

function Badge({ label, color = 'teal' }) {
  const colors = {
    teal:  { bg: 'var(--teal-glow)',  border: 'var(--teal)',     text: 'var(--teal)'  },
    red:   { bg: 'var(--red-dim)',    border: 'var(--red)',      text: 'var(--red)'   },
    amber: { bg: 'var(--amber-dim)',  border: 'var(--amber)',    text: 'var(--amber)' },
    blue:  { bg: 'var(--blue-dim)',   border: 'var(--blue)',     text: 'var(--blue)'  },
  }
  const c = colors[color] || colors.teal
  return (
    <span style={{
      padding: '2px 10px', borderRadius: '20px', fontSize: '11px',
      fontFamily: 'var(--font-mono)', fontWeight: 500,
      background: c.bg, border: `1px solid ${c.border}`, color: c.text,
    }}>
      {label}
    </span>
  )
}

function Card({ children, style = {} }) {
  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: '12px', padding: '20px', ...style,
    }}>
      {children}
    </div>
  )
}

function SectionTitle({ children }) {
  return (
    <div style={{
      fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text3)',
      letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '12px',
    }}>
      {children}
    </div>
  )
}

export default function DiagnosisResult({ data }) {
  const [showRaw, setShowRaw] = useState(false)

  const complexityColor = {
    LOW: 'teal', MEDIUM: 'amber', HIGH: 'red',
  }[data.complexity?.level] || 'teal'

  const riskColor = {
    LOW: 'teal', MEDIUM: 'amber', HIGH: 'amber', EMERGENCY: 'red',
  }[data.risk_level] || 'teal'

  const confidenceColor = {
    high: 'teal', medium: 'amber', low: 'red',
  }[data.confidence_level] || 'teal'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', animation: 'fadeUp 0.4s ease' }}>

      {/* Emergency banner */}
      {data.is_emergency && (
        <div style={{
          padding: '14px 20px', background: 'var(--red-dim)',
          border: '1px solid var(--red)', borderRadius: '10px',
          display: 'flex', alignItems: 'center', gap: '12px',
        }}>
          <div style={{
            width: '10px', height: '10px', borderRadius: '50%',
            background: 'var(--red)', animation: 'pulse-ring 1s ease-out infinite',
            flexShrink: 0,
          }}/>
          <div>
            <div style={{ fontFamily: 'var(--font-head)', fontWeight: 700, color: 'var(--red)', fontSize: '15px' }}>
              EMERGENCY — Immediate Medical Attention Required
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text2)', marginTop: '2px' }}>
              {data.referral?.contact_advice}
            </div>
          </div>
        </div>
      )}

      {/* Primary diagnosis */}
      <Card>
        <SectionTitle>Primary Diagnosis</SectionTitle>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontFamily: 'var(--font-head)', fontSize: '26px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--teal)', marginBottom: '6px' }}>
              {data.primary_disease}
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <Badge label={`${data.confidence_level?.toUpperCase()} CONFIDENCE`} color={confidenceColor}/>
              <Badge label={`${data.model_agreement}/3 MODELS AGREE`} color={data.model_agreement === 3 ? 'teal' : 'amber'}/>
              <Badge label={data.complexity?.level} color={complexityColor}/>
              <Badge label={data.risk_level} color={riskColor}/>
            </div>
          </div>
        </div>
        {data.diagnosis_summary && (
          <div style={{
            marginTop: '16px', padding: '14px', background: 'var(--bg2)',
            borderRadius: '8px', fontSize: '14px', color: 'var(--text2)', lineHeight: '1.7',
            borderLeft: '3px solid var(--teal)',
          }}>
            {data.diagnosis_summary}
          </div>
        )}
      </Card>

      {/* Model breakdown */}
      <Card>
        <SectionTitle>Ensemble model breakdown</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '10px' }}>
          {[
            { label: 'SVM', value: data.model_breakdown?.svm_model_prediction },
            { label: 'Naive Bayes', value: data.model_breakdown?.naive_bayes_prediction },
            { label: 'Random Forest', value: data.model_breakdown?.rf_model_prediction },
            { label: 'Ensemble vote', value: data.model_breakdown?.final_prediction, highlight: true },
          ].map(m => (
            <div key={m.label} style={{
              padding: '12px', borderRadius: '8px',
              background: m.highlight ? 'var(--teal-glow)' : 'var(--bg2)',
              border: `1px solid ${m.highlight ? 'var(--teal-dim)' : 'var(--border)'}`,
            }}>
              <div style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', marginBottom: '4px', textTransform: 'uppercase' }}>
                {m.label}
              </div>
              <div style={{ fontSize: '12px', fontWeight: 500, color: m.highlight ? 'var(--teal)' : 'var(--text)', lineHeight: 1.3 }}>
                {m.value || '—'}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Top-K diseases */}
      <Card>
        <SectionTitle>Top disease probabilities</SectionTitle>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {(data.top_k_diseases || []).map((d, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', width: '16px', textAlign: 'right' }}>
                {d.rank}
              </span>
              <div style={{ flex: 1, position: 'relative', height: '28px', background: 'var(--bg2)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  position: 'absolute', left: 0, top: 0, bottom: 0,
                  width: `${(d.probability * 100).toFixed(1)}%`,
                  background: i === 0 ? 'var(--teal-glow)' : 'var(--surface2)',
                  borderRight: i === 0 ? '2px solid var(--teal)' : '1px solid var(--border2)',
                  transition: 'width 0.8s ease',
                }}/>
                <span style={{
                  position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)',
                  fontSize: '12px', color: i === 0 ? 'var(--teal)' : 'var(--text2)', fontWeight: i === 0 ? 500 : 400,
                }}>
                  {d.disease}
                </span>
              </div>
              <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text2)', width: '44px', textAlign: 'right' }}>
                {(d.probability * 100).toFixed(1)}%
              </span>
              <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', width: '32px' }}>
                {d.votes}/3
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Complexity assessment */}
      {data.complexity && (
        <Card>
          <SectionTitle>Complexity assessment</SectionTitle>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
            <Badge label={data.complexity.level} color={complexityColor}/>
            <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text3)' }}>
              Score: {data.complexity.score}/100
            </span>
          </div>
          {data.complexity.systems_involved?.length > 0 && (
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
              {data.complexity.systems_involved.map(s => (
                <Badge key={s} label={s} color="blue"/>
              ))}
            </div>
          )}
          <div style={{ fontSize: '13px', color: 'var(--text2)' }}>
            {data.complexity.reasoning}
          </div>
        </Card>
      )}

      {/* Symptom analysis (collaborative agents output) */}
      {data.symptom_analysis && (
        <Card>
          <SectionTitle>Symptom analysis</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '12px' }}>
            <div style={{ padding: '10px', background: 'var(--bg2)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', marginBottom: '4px' }}>DOMINANT SYSTEM</div>
              <div style={{ fontSize: '14px', color: 'var(--teal)', fontWeight: 500, textTransform: 'capitalize' }}>
                {data.symptom_analysis.dominant_system?.replace(/_/g, ' ')}
              </div>
            </div>
            <div style={{ padding: '10px', background: 'var(--bg2)', borderRadius: '6px' }}>
              <div style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', marginBottom: '4px' }}>SEVERITY SCORE</div>
              <div style={{ fontSize: '14px', color: 'var(--amber)', fontWeight: 500 }}>
                {data.symptom_analysis.total_severity_score} pts
              </div>
            </div>
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text2)' }}>
            {data.symptom_analysis.pattern_notes}
          </div>
        </Card>
      )}

      {/* Treatment plan */}
      {data.treatment_plan && (
        <Card>
          <SectionTitle>Treatment plan</SectionTitle>
          {data.treatment_plan.immediate_actions?.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', color: 'var(--red)', fontFamily: 'var(--font-mono)', marginBottom: '8px' }}>
                IMMEDIATE ACTIONS
              </div>
              {data.treatment_plan.immediate_actions.map((a, i) => (
                <div key={i} style={{ display: 'flex', gap: '10px', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--red)', fontFamily: 'var(--font-mono)', fontSize: '11px', flexShrink: 0, marginTop: '2px' }}>
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span style={{ fontSize: '13px', color: 'var(--text)' }}>{a}</span>
                </div>
              ))}
            </div>
          )}
          {data.treatment_plan.precautions?.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', color: 'var(--teal)', fontFamily: 'var(--font-mono)', marginBottom: '8px' }}>
                PRECAUTIONS
              </div>
              {data.treatment_plan.precautions.map((p, i) => (
                <div key={i} style={{ display: 'flex', gap: '10px', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--teal)', fontSize: '11px', flexShrink: 0, marginTop: '3px' }}>▸</span>
                  <span style={{ fontSize: '13px', color: 'var(--text2)' }}>{p}</span>
                </div>
              ))}
            </div>
          )}
          <div style={{ padding: '10px 12px', background: 'var(--bg2)', borderRadius: '6px', fontSize: '13px' }}>
            <span style={{ color: 'var(--text3)', fontFamily: 'var(--font-mono)', fontSize: '10px' }}>FOLLOW-UP: </span>
            <span style={{ color: 'var(--text)' }}>{data.treatment_plan.follow_up}</span>
          </div>
        </Card>
      )}

      {/* Precautions (from LLM) */}
      {data.suggested_precautions?.length > 0 && !data.treatment_plan && (
        <Card>
          <SectionTitle>Suggested precautions</SectionTitle>
          {data.suggested_precautions.map((p, i) => (
            <div key={i} style={{ display: 'flex', gap: '10px', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--teal)', fontSize: '11px', flexShrink: 0, marginTop: '3px' }}>▸</span>
              <span style={{ fontSize: '13px', color: 'var(--text2)' }}>{p}</span>
            </div>
          ))}
        </Card>
      )}

      {/* Red flags */}
      {data.red_flags?.length > 0 && (
        <Card style={{ borderColor: 'var(--red)' }}>
          <SectionTitle>Red flags detected</SectionTitle>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {data.red_flags.map((f, i) => (
              <Badge key={i} label={f.replace(/_/g, ' ')} color="red"/>
            ))}
          </div>
        </Card>
      )}

      {/* Referral */}
      {data.referral && (
        <Card style={{ borderColor: data.referral.urgency === 'IMMEDIATE' ? 'var(--red)' : data.referral.urgency === 'URGENT' ? 'var(--amber)' : 'var(--border)' }}>
          <SectionTitle>Referral</SectionTitle>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span style={{ fontFamily: 'var(--font-head)', fontSize: '16px', fontWeight: 600 }}>
                  {data.referral.specialist}
                </span>
                <Badge
                  label={data.referral.urgency}
                  color={data.referral.urgency === 'IMMEDIATE' ? 'red' : data.referral.urgency === 'URGENT' ? 'amber' : 'teal'}
                />
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text2)', marginBottom: '6px' }}>
                {data.referral.referral_note}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--teal)', fontFamily: 'var(--font-mono)' }}>
                {data.referral.contact_advice}
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Pipeline meta */}
      <div style={{
        display: 'flex', gap: '16px', flexWrap: 'wrap',
        padding: '12px 16px', background: 'var(--surface)',
        border: '1px solid var(--border)', borderRadius: '8px',
        fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text3)',
      }}>
        {[
          ['PATIENT', data.patient_id?.slice(0, 8)],
          ['PIPELINE', data.pipeline_version],
          ['HMAC', data.hmac_valid ? 'VERIFIED' : 'FAILED'],
          ['LATENCY', data.total_ms ? `${data.total_ms}ms` : '—'],
        ].map(([k, v]) => (
          <span key={k}>{k}: <span style={{ color: k === 'HMAC' && !data.hmac_valid ? 'var(--red)' : 'var(--text2)' }}>{v}</span></span>
        ))}
      </div>

      {/* Raw JSON toggle */}
      <button onClick={() => setShowRaw(v => !v)} style={{
        padding: '8px 14px', background: 'transparent', border: '1px solid var(--border)',
        borderRadius: '6px', color: 'var(--text3)', fontSize: '12px', fontFamily: 'var(--font-mono)',
        alignSelf: 'flex-start', transition: 'all 0.15s',
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border2)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
      >
        {showRaw ? 'HIDE' : 'SHOW'} RAW JSON
      </button>
      {showRaw && (
        <pre style={{
          padding: '16px', background: 'var(--bg2)', border: '1px solid var(--border)',
          borderRadius: '8px', fontSize: '11px', fontFamily: 'var(--font-mono)',
          color: 'var(--text2)', overflowX: 'auto', lineHeight: 1.6,
        }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  )
}