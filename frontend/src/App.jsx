import { useState } from 'react'
import axios from 'axios'
import Header from './components/Header'
import SymptomSelector from './components/SymptomSelector'
import DiagnosisResult from './components/DiagnosisResult'
import LoadingState from './components/LoadingState'

const API = 'http://localhost:8000'

export default function App() {
  const [patientId, setPatientId] = useState('')
  const [symptoms,  setSymptoms]  = useState([])
  const [loading,   setLoading]   = useState(false)
  const [result,    setResult]    = useState(null)
  const [error,     setError]     = useState(null)
  const [idFocused, setIdFocused] = useState(false)

  const handleDiagnose = async () => {
    if (!symptoms.length) { setError('Select at least one symptom.'); return }
    setError(null); setResult(null); setLoading(true)
    try {
      const { data } = await axios.post(`${API}/diagnose`, {
        patient_id: patientId || `pt-${Date.now()}`,
        symptoms,
      })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Backend unreachable. Make sure uvicorn is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => { setResult(null); setError(null); setSymptoms([]); setPatientId('') }

  const showResult = loading || result

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Header/>

      <main style={{
        maxWidth: showResult ? '1200px' : '700px',
        margin: '0 auto',
        padding: '2rem 1.5rem',
        display: 'grid',
        gridTemplateColumns: showResult ? '1fr 1fr' : '1fr',
        gap: '28px',
        alignItems: 'start',
        transition: 'max-width 0.4s ease',
      }}>

        {/* Left — intake */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeUp 0.5s ease' }}>

          {/* Hero title */}
          <div style={{ paddingBottom: '4px' }}>
            <div style={{
              fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--teal)',
              letterSpacing: '0.12em', marginBottom: '10px',
            }}>
              MULTI-AGENT DIAGNOSTIC SYSTEM
            </div>
            <h1 style={{
              fontFamily: 'var(--font)', fontSize: '36px', fontWeight: 700,
              letterSpacing: '-0.03em', lineHeight: 1.05, marginBottom: '10px',
            }}>
              Patient<br/>
              <span style={{
                color: 'var(--teal)',
                background: 'linear-gradient(90deg, var(--teal), #00ffcc)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                Triage
              </span>{' '}
              Assessment
            </h1>
            <p style={{ fontSize: '14px', color: 'var(--text2)', lineHeight: 1.65, maxWidth: '420px' }}>
              Select symptoms and run the full diagnostic pipeline — ML ensemble,
              semantic retrieval, collaborative agents, and LLM synthesis. Fully offline.
            </p>
          </div>

          {/* Patient ID */}
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', padding: '18px 20px',
          }}>
            <label style={{
              fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)',
              letterSpacing: '0.1em', display: 'block', marginBottom: '10px',
            }}>
              PATIENT ID (OPTIONAL)
            </label>
            <input
              value={patientId}
              onChange={e => setPatientId(e.target.value)}
              onFocus={() => setIdFocused(true)}
              onBlur={() => setIdFocused(false)}
              placeholder="e.g. PT-2024-001"
              style={{
                width: '100%', padding: '10px 14px',
                background: 'var(--bg2)',
                border: `1px solid ${idFocused ? 'var(--teal2)' : 'var(--border)'}`,
                borderRadius: 'var(--radius)', color: 'var(--text)',
                fontSize: '14px', outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s',
                boxShadow: idFocused ? '0 0 0 3px var(--teal-glow)' : 'none',
              }}
            />
          </div>

          {/* Symptom selector */}
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', padding: '18px 20px',
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginBottom: '16px',
            }}>
              <label style={{
                fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)',
                letterSpacing: '0.1em',
              }}>
                SYMPTOMS
              </label>
              {symptoms.length > 0 && (
                <span style={{
                  fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--teal)',
                  background: 'var(--teal-glow)', padding: '2px 10px',
                  borderRadius: '20px', border: '1px solid rgba(0,212,170,0.2)',
                }}>
                  {symptoms.length} selected
                </span>
              )}
            </div>
            <SymptomSelector selected={symptoms} onChange={setSymptoms}/>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              padding: '12px 16px', background: 'var(--red-dim)',
              border: '1px solid rgba(255,87,87,0.3)', borderRadius: 'var(--radius)',
              fontSize: '13px', color: 'var(--red)',
              animation: 'fadeIn 0.2s ease',
            }}>
              {error}
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleDiagnose}
              disabled={loading || !symptoms.length}
              style={{
                flex: 1, padding: '14px 20px', borderRadius: 'var(--radius)',
                fontSize: '14px', fontWeight: 600, letterSpacing: '0.01em',
                background: !symptoms.length || loading
                  ? 'var(--surface2)'
                  : 'var(--teal)',
                color: !symptoms.length || loading ? 'var(--text3)' : 'var(--bg)',
                cursor: !symptoms.length || loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: symptoms.length && !loading
                  ? '0 0 20px rgba(0,212,170,0.2)'
                  : 'none',
              }}
              onMouseEnter={e => { if (symptoms.length && !loading) e.currentTarget.style.boxShadow = '0 0 30px rgba(0,212,170,0.35)' }}
              onMouseLeave={e => { if (symptoms.length && !loading) e.currentTarget.style.boxShadow = '0 0 20px rgba(0,212,170,0.2)' }}
            >
              {loading ? 'Analysing...' : `Run Diagnosis — ${symptoms.length} symptom${symptoms.length !== 1 ? 's' : ''}`}
            </button>

            {(result || symptoms.length > 0) && (
              <button onClick={handleReset} style={{
                padding: '14px 20px', background: 'transparent',
                border: '1px solid var(--border)', borderRadius: 'var(--radius)',
                color: 'var(--text2)', fontSize: '14px', transition: 'all 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--text)' }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}
              >
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Right — results */}
        {showResult && (
          <div style={{ animation: 'fadeUp 0.4s ease 0.1s both' }}>
            {loading ? <LoadingState/> : <DiagnosisResult data={result}/>}
          </div>
        )}
      </main>
    </div>
  )
}