import { useState } from 'react'
import axios from 'axios'
import Header from './components/Header'
import SymptomSelector from './components/SymptomSelector'
import DiagnosisResult from './components/DiagnosisResult'
import LoadingState from './components/LoadingState'

const API = 'http://localhost:8000'

export default function App() {
  const [patientId, setPatientId]   = useState('')
  const [symptoms, setSymptoms]     = useState([])
  const [loading, setLoading]       = useState(false)
  const [result, setResult]         = useState(null)
  const [error, setError]           = useState(null)

  const handleDiagnose = async () => {
    if (symptoms.length === 0) {
      setError('Please select at least one symptom.')
      return
    }
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const { data } = await axios.post(`${API}/diagnose`, {
        patient_id: patientId || `pt-${Date.now()}`,
        symptoms,
      })
      setResult(data)
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Could not reach the backend. Make sure uvicorn is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setSymptoms([])
    setPatientId('')
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Header />

      <main style={{
        maxWidth: '1100px', margin: '0 auto',
        padding: '2rem 1.5rem',
        display: 'grid',
        gridTemplateColumns: result ? '1fr 1fr' : '640px',
        justifyContent: 'center',
        gap: '24px',
        alignItems: 'start',
      }}>

        {/* Left panel — intake form */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeUp 0.4s ease' }}>
          {/* Title */}
          <div>
            <h1 style={{
              fontFamily: 'var(--font-head)', fontSize: '32px', fontWeight: 800,
              letterSpacing: '-0.03em', lineHeight: 1.1, marginBottom: '8px',
            }}>
              Patient<br/>
              <span style={{ color: 'var(--teal)' }}>Triage</span> Assessment
            </h1>
            <p style={{ fontSize: '14px', color: 'var(--text2)', lineHeight: 1.6 }}>
              Select symptoms, run the multi-agent diagnostic pipeline,
              and receive a grounded clinical assessment — fully offline.
            </p>
          </div>

          {/* Patient ID */}
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: '12px', padding: '20px',
          }}>
            <label style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', letterSpacing: '0.08em', display: 'block', marginBottom: '8px' }}>
              PATIENT ID (optional)
            </label>
            <input
              value={patientId}
              onChange={e => setPatientId(e.target.value)}
              placeholder="e.g. PT-2024-001"
              style={{
                width: '100%', padding: '10px 12px',
                background: 'var(--bg2)', border: '1px solid var(--border)',
                borderRadius: '6px', color: 'var(--text)', fontSize: '14px', outline: 'none',
              }}
              onFocus={e => e.target.style.borderColor = 'var(--teal)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
          </div>

          {/* Symptom selector */}
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: '12px', padding: '20px',
          }}>
            <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text3)', letterSpacing: '0.08em', marginBottom: '16px' }}>
              SYMPTOMS — {symptoms.length} SELECTED
            </div>
            <SymptomSelector selected={symptoms} onChange={setSymptoms}/>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              padding: '12px 16px', background: 'var(--red-dim)',
              border: '1px solid var(--red)', borderRadius: '8px',
              fontSize: '13px', color: 'var(--red)',
            }}>
              {error}
            </div>
          )}

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={handleDiagnose} disabled={loading || symptoms.length === 0} style={{
              flex: 1, padding: '14px', background: symptoms.length > 0 && !loading ? 'var(--teal)' : 'var(--surface2)',
              color: symptoms.length > 0 && !loading ? 'var(--bg)' : 'var(--text3)',
              borderRadius: '8px', fontSize: '14px', fontWeight: 600,
              fontFamily: 'var(--font-head)', letterSpacing: '0.01em',
              transition: 'all 0.15s', cursor: symptoms.length > 0 && !loading ? 'pointer' : 'not-allowed',
            }}>
              {loading ? 'Analysing...' : `Run Diagnosis (${symptoms.length} symptoms)`}
            </button>
            {(result || symptoms.length > 0) && (
              <button onClick={handleReset} style={{
                padding: '14px 20px', background: 'transparent',
                border: '1px solid var(--border)', borderRadius: '8px',
                color: 'var(--text2)', fontSize: '14px', transition: 'all 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border2)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Right panel — results */}
        {(loading || result) && (
          <div style={{ animation: 'fadeUp 0.4s ease' }}>
            {loading ? <LoadingState /> : <DiagnosisResult data={result}/>}
          </div>
        )}
      </main>
    </div>
  )
}