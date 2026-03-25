import { useState } from 'react'
import axios from 'axios'
import Header from './components/Header'
import SymptomSelector from './components/SymptomSelector'
import DiagnosisResult from './components/DiagnosisResult'
import LoadingState from './components/LoadingState'

const API = 'http://localhost:8000'

export default function App() {
  const [patientId,  setPatientId]  = useState('')
  const [symptoms,   setSymptoms]   = useState([])
  const [freeText,   setFreeText]   = useState('')
  const [loading,    setLoading]    = useState(false)
  const [result,     setResult]     = useState(null)
  const [error,      setError]      = useState(null)
  const [idFocused,  setIdFocused]  = useState(false)
  const [txtFocused, setTxtFocused] = useState(false)

  const hasInput   = symptoms.length > 0 || freeText.trim().length > 0
  const showResult = loading || result

  const handleDiagnose = async () => {
    if (!hasInput) {
      setError('Enter a description or select at least one symptom.')
      return
    }
    setError(null); setResult(null); setLoading(true)
    try {
      const { data } = await axios.post(`${API}/diagnose`, {
        patient_id: patientId || `pt-${Date.now()}`,
        symptoms,
        free_text: freeText.trim() || null,
      })
      setResult(data)
    } catch (e) {
      setError(
        e.response?.data?.detail ||
        'Backend unreachable. Make sure uvicorn is running on port 8000.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null); setError(null)
    setSymptoms([]); setPatientId(''); setFreeText('')
  }

  const card = {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '18px 20px',
  }

  const lbl = {
    fontSize: '10px',
    fontFamily: 'var(--mono)',
    color: 'var(--text3)',
    letterSpacing: '0.1em',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '10px',
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Header />

      <main style={{
        maxWidth: showResult ? '1200px' : '720px',
        margin: '0 auto',
        padding: '2.5rem 1.5rem',
        display: 'grid',
        gridTemplateColumns: showResult ? 'minmax(0,1fr) minmax(0,1fr)' : '1fr',
        gap: '28px',
        alignItems: 'start',
        transition: 'max-width 0.4s ease',
      }}>

        {/* ── Left panel ── */}
        <div style={{
          display: 'flex', flexDirection: 'column', gap: '16px',
          animation: 'fadeUp 0.5s ease',
        }}>

          {/* Hero */}
          <div style={{ paddingBottom: '4px' }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              padding: '4px 12px',
              background: 'rgba(0,212,170,0.06)',
              border: '1px solid rgba(0,212,170,0.15)',
              borderRadius: '20px', marginBottom: '14px',
            }}>
              <div style={{
                width: '6px', height: '6px', borderRadius: '50%',
                background: 'var(--teal)',
                animation: 'pulse 2s ease-in-out infinite',
              }}/>
              <span style={{
                fontSize: '10px', fontFamily: 'var(--mono)',
                color: 'var(--teal)', letterSpacing: '0.12em',
              }}>
                MULTI-AGENT DIAGNOSTIC SYSTEM
              </span>
            </div>

            <h1 style={{
              fontFamily: 'var(--font)', fontSize: '36px', fontWeight: 700,
              letterSpacing: '-0.03em', lineHeight: 1.06, marginBottom: '10px',
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

            <p style={{
              fontSize: '13.5px', color: 'var(--text2)',
              lineHeight: 1.7, maxWidth: '430px',
            }}>
              Describe symptoms in plain language or select from the list.
              Runs ML ensemble, semantic retrieval, and LLM synthesis — fully offline.
            </p>
          </div>

          {/* Patient ID */}
          <div style={card}>
            <label style={lbl}>
              <span>PATIENT ID <span style={{ fontWeight: 400, color: 'var(--text3)' }}>— OPTIONAL</span></span>
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
                fontSize: '13px', outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s',
                boxShadow: idFocused ? '0 0 0 3px var(--teal-glow)' : 'none',
              }}
            />
          </div>

          {/* Free text */}
          <div style={{
            ...card,
            border: `1px solid ${txtFocused ? 'rgba(0,212,170,0.35)' : 'var(--border)'}`,
            transition: 'border-color 0.2s, box-shadow 0.2s',
            boxShadow: txtFocused ? '0 0 0 3px var(--teal-glow)' : 'none',
          }}>
            <label style={lbl}>
              <span>DESCRIBE YOUR SYMPTOMS</span>
              <span style={{
                fontSize: '10px', fontFamily: 'var(--mono)',
                color: 'var(--teal)', background: 'var(--teal-glow)',
                padding: '2px 8px', borderRadius: '10px',
                border: '1px solid rgba(0,212,170,0.15)',
              }}>
                NLP AUTO-EXTRACT
              </span>
            </label>
            <textarea
              value={freeText}
              onChange={e => setFreeText(e.target.value)}
              onFocus={() => setTxtFocused(true)}
              onBlur={() => setTxtFocused(false)}
              placeholder="e.g. I have had fever and chills for 2 days, my whole body is aching and I feel very tired..."
              rows={3}
              style={{
                width: '100%', padding: '11px 14px',
                background: 'var(--bg2)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)', color: 'var(--text)',
                fontSize: '13px', outline: 'none',
                resize: 'vertical', lineHeight: 1.65,
              }}
            />
            <div style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              marginTop: '8px',
              fontSize: '11px', color: 'var(--text3)',
              fontFamily: 'var(--mono)',
            }}>
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                <circle cx="5.5" cy="5.5" r="4.5" stroke="var(--text3)" strokeWidth="1"/>
                <path d="M5.5 4v3M5.5 8v.5" stroke="var(--text3)" strokeWidth="1" strokeLinecap="round"/>
              </svg>
              Symptom names are extracted automatically from your description
            </div>
          </div>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}/>
            <span style={{
              fontSize: '10px', fontFamily: 'var(--mono)',
              color: 'var(--text3)', letterSpacing: '0.1em',
            }}>
              OR SELECT MANUALLY
            </span>
            <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}/>
          </div>

          {/* Symptom selector */}
          <div style={card}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <label style={{ fontSize: '10px', fontFamily: 'var(--mono)', color: 'var(--text3)', letterSpacing: '0.1em' }}>
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
            <SymptomSelector selected={symptoms} onChange={setSymptoms} />
          </div>

          {/* Pipeline badge */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '11px 16px',
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
          }}>
            <div style={{
              width: '7px', height: '7px', borderRadius: '50%',
              background: 'var(--teal)', flexShrink: 0,
              animation: 'pulse 2s ease-in-out infinite',
            }}/>
            <span style={{ fontSize: '11px', fontFamily: 'var(--mono)', color: 'var(--text3)' }}>
              {['RF + GB + NB ensemble', 'FAISS RAG', 'TinyLlama 1.1B', 'HMAC-SHA256'].map((t, i, arr) => (
                <span key={i}>
                  <span style={{ color: 'var(--text2)' }}>{t}</span>
                  {i < arr.length - 1 && <span style={{ margin: '0 6px', opacity: 0.3 }}>·</span>}
                </span>
              ))}
            </span>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: '10px',
              padding: '12px 16px',
              background: 'var(--red-dim)',
              border: '1px solid rgba(255,87,87,0.25)',
              borderRadius: 'var(--radius)',
              fontSize: '13px', color: 'var(--red)',
              animation: 'fadeIn 0.2s ease',
            }}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{ flexShrink: 0, marginTop: '1px' }}>
                <circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1.2"/>
                <path d="M7 4v3.5M7 9.5v.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
              </svg>
              {error}
            </div>
          )}

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleDiagnose}
              disabled={loading || !hasInput}
              style={{
                flex: 1, padding: '14px 20px',
                borderRadius: 'var(--radius)',
                fontSize: '14px', fontWeight: 600,
                letterSpacing: '0.01em', border: 'none',
                background: hasInput && !loading ? 'var(--teal)' : 'var(--surface2)',
                color: hasInput && !loading ? 'var(--bg)' : 'var(--text3)',
                cursor: hasInput && !loading ? 'pointer' : 'not-allowed',
                transition: 'all 0.2s',
                boxShadow: hasInput && !loading ? '0 0 20px rgba(0,212,170,0.2)' : 'none',
              }}
              onMouseEnter={e => { if (hasInput && !loading) e.currentTarget.style.boxShadow = '0 0 30px rgba(0,212,170,0.35)' }}
              onMouseLeave={e => { if (hasInput && !loading) e.currentTarget.style.boxShadow = '0 0 20px rgba(0,212,170,0.2)' }}
            >
              {loading
                ? 'Analysing...'
                : symptoms.length > 0
                  ? `Run Diagnosis — ${symptoms.length} symptom${symptoms.length !== 1 ? 's' : ''}`
                  : freeText.trim()
                    ? 'Run Diagnosis — from description'
                    : 'Run Diagnosis'
              }
            </button>

            {(result || hasInput) && (
              <button
                onClick={handleReset}
                style={{
                  padding: '14px 20px', background: 'transparent',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)', color: 'var(--text2)',
                  fontSize: '14px', transition: 'all 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--text)' }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}
              >
                Reset
              </button>
            )}
          </div>
        </div>

        {/* ── Right panel ── */}
        {showResult && (
          <div style={{ animation: 'fadeUp 0.4s ease 0.1s both' }}>
            {loading ? <LoadingState /> : <DiagnosisResult data={result} />}
          </div>
        )}
      </main>
    </div>
  )
}