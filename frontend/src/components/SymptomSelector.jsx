import { useState, useMemo } from 'react'
import { ALL_SYMPTOMS, SYMPTOM_LABELS, SYMPTOM_CATEGORIES } from '../constants/symptoms'

const CATEGORY_ICONS = {
  'Fever & Systemic': '🌡',
  'Pain': '⚡',
  'Respiratory': '🫁',
  'Skin': '🩺',
  'Digestive': '💊',
  'Neurological': '🧠',
  'Urinary': '💧',
  'Other': '➕',
}

export default function SymptomSelector({ selected, onChange }) {
  const [search, setSearch]           = useState('')
  const [activeCategory, setCategory] = useState('All')
  const [focused, setFocused]         = useState(false)

  const categories = ['All', ...Object.keys(SYMPTOM_CATEGORIES)]

  const filtered = useMemo(() => {
    let pool = activeCategory === 'All'
      ? ALL_SYMPTOMS
      : (SYMPTOM_CATEGORIES[activeCategory] || [])
    if (search.trim()) {
      const q = search.toLowerCase().replace(/\s+/g, '_')
      pool = pool.filter(s =>
        s.includes(q) || SYMPTOM_LABELS[s].toLowerCase().includes(search.toLowerCase())
      )
    }
    return pool
  }, [search, activeCategory])

  const toggle = (sym) => {
    onChange(selected.includes(sym)
      ? selected.filter(s => s !== sym)
      : [...selected, sym]
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

      {/* Search bar */}
      <div style={{ position: 'relative' }}>
        <svg style={{
          position: 'absolute', left: '14px', top: '50%',
          transform: 'translateY(-50%)', opacity: focused ? 0.7 : 0.3,
          transition: 'opacity 0.2s', pointerEvents: 'none',
        }} width="15" height="15" viewBox="0 0 15 15" fill="none">
          <circle cx="6.5" cy="6.5" r="5" stroke="var(--teal)" strokeWidth="1.5"/>
          <path d="M10.5 10.5L14 14" stroke="var(--teal)" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search symptoms..."
          style={{
            width: '100%', padding: '11px 14px 11px 40px',
            background: 'var(--bg2)',
            border: `1px solid ${focused ? 'var(--teal2)' : 'var(--border)'}`,
            borderRadius: 'var(--radius)', color: 'var(--text)',
            fontSize: '14px', outline: 'none',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            boxShadow: focused ? '0 0 0 3px var(--teal-glow)' : 'none',
          }}
        />
        {search && (
          <button onClick={() => setSearch('')} style={{
            position: 'absolute', right: '12px', top: '50%',
            transform: 'translateY(-50%)', background: 'var(--border)',
            border: 'none', borderRadius: '50%', width: '18px', height: '18px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--text2)', fontSize: '12px',
          }}>×</button>
        )}
      </div>

      {/* Category pills */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {categories.map(cat => {
          const isActive = activeCategory === cat
          return (
            <button key={cat} onClick={() => setCategory(cat)} style={{
              padding: '5px 13px', borderRadius: '20px', fontSize: '12px',
              fontWeight: 500, display: 'flex', alignItems: 'center', gap: '5px',
              background: isActive ? 'var(--teal)' : 'var(--surface)',
              color: isActive ? 'var(--bg)' : 'var(--text2)',
              border: `1px solid ${isActive ? 'var(--teal)' : 'var(--border)'}`,
              transition: 'all 0.15s', transform: isActive ? 'scale(1.02)' : 'scale(1)',
            }}>
              {CATEGORY_ICONS[cat] && (
                <span style={{ fontSize: '11px' }}>{CATEGORY_ICONS[cat]}</span>
              )}
              {cat}
            </button>
          )
        })}
      </div>

      {/* Selected chips */}
      {selected.length > 0 && (
        <div style={{
          padding: '12px 14px',
          background: 'linear-gradient(135deg, var(--teal-glow) 0%, rgba(0,212,170,0.04) 100%)',
          border: '1px solid var(--teal2)',
          borderRadius: 'var(--radius)',
          animation: 'fadeIn 0.3s ease',
        }}>
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            marginBottom: '10px',
          }}>
            <span style={{
              fontSize: '11px', fontFamily: 'var(--mono)',
              color: 'var(--teal)', letterSpacing: '0.06em',
            }}>
              {selected.length} SYMPTOM{selected.length !== 1 ? 'S' : ''} SELECTED
            </span>
            <button onClick={() => onChange([])} style={{
              fontSize: '11px', color: 'var(--text3)', background: 'transparent',
              padding: '2px 8px', border: '1px solid var(--border)',
              borderRadius: '10px', transition: 'all 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--red)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text3)'}
            >
              clear all
            </button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {selected.map((s, i) => (
              <span key={s} onClick={() => toggle(s)} style={{
                padding: '4px 11px', borderRadius: '20px', fontSize: '12px',
                fontWeight: 500, cursor: 'pointer',
                background: 'var(--teal)', color: 'var(--bg)',
                display: 'flex', alignItems: 'center', gap: '5px',
                animation: `fadeIn 0.2s ease ${i * 0.03}s both`,
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--teal2)'}
              onMouseLeave={e => e.currentTarget.style.background = 'var(--teal)'}
              >
                {SYMPTOM_LABELS[s]}
                <span style={{ fontSize: '13px', lineHeight: 1, marginTop: '-1px' }}>×</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Symptom grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(155px, 1fr))',
        gap: '6px',
        maxHeight: '320px',
        overflowY: 'auto',
        paddingRight: '4px',
      }}>
        {filtered.map((sym, i) => {
          const isSelected = selected.includes(sym)
          return (
            <button key={sym} onClick={() => toggle(sym)} style={{
              padding: '9px 12px', textAlign: 'left', borderRadius: '8px',
              background: isSelected ? 'var(--teal-glow2)' : 'var(--surface)',
              border: `1px solid ${isSelected ? 'var(--teal)' : 'var(--border)'}`,
              color: isSelected ? 'var(--teal)' : 'var(--text2)',
              fontSize: '12px', fontWeight: isSelected ? 500 : 400,
              transition: 'all 0.12s',
              transform: isSelected ? 'scale(1.01)' : 'scale(1)',
              animation: `fadeIn 0.15s ease ${Math.min(i * 0.01, 0.3)}s both`,
              display: 'flex', alignItems: 'center', gap: '7px',
            }}
            onMouseEnter={e => { if (!isSelected) { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--text)' }}}
            onMouseLeave={e => { if (!isSelected) { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text2)' }}}
            >
              {isSelected && (
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ flexShrink: 0 }}>
                  <path d="M1.5 5l2.5 2.5L8.5 2" stroke="var(--teal)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
              <span style={{ lineHeight: 1.3 }}>{SYMPTOM_LABELS[sym]}</span>
            </button>
          )
        })}
        {filtered.length === 0 && (
          <div style={{
            gridColumn: '1/-1', padding: '32px', textAlign: 'center',
            color: 'var(--text3)', fontSize: '13px',
          }}>
            No symptoms match "{search}"
          </div>
        )}
      </div>
    </div>
  )
}