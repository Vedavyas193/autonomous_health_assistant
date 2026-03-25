import { useState, useMemo } from 'react'
import { ALL_SYMPTOMS, SYMPTOM_LABELS, SYMPTOM_CATEGORIES } from '../constants/symptoms'

const CATEGORY_COLORS = {
  'Fever & Systemic': { color: 'var(--red)',    bg: 'rgba(255,87,87,0.08)',    border: 'rgba(255,87,87,0.2)'    },
  'Pain':             { color: 'var(--amber)',  bg: 'rgba(255,179,64,0.08)',   border: 'rgba(255,179,64,0.2)'   },
  'Respiratory':      { color: 'var(--blue)',   bg: 'rgba(77,159,255,0.08)',   border: 'rgba(77,159,255,0.2)'   },
  'Skin':             { color: 'var(--purple)', bg: 'rgba(167,139,250,0.08)',  border: 'rgba(167,139,250,0.2)'  },
  'Digestive':        { color: 'var(--teal)',   bg: 'rgba(0,212,170,0.08)',    border: 'rgba(0,212,170,0.2)'    },
  'Neurological':     { color: 'var(--purple)', bg: 'rgba(167,139,250,0.08)', border: 'rgba(167,139,250,0.2)'  },
  'Urinary':          { color: 'var(--blue)',   bg: 'rgba(77,159,255,0.08)',   border: 'rgba(77,159,255,0.2)'   },
  'Weight & Appetite':{ color: 'var(--amber)',  bg: 'rgba(255,179,64,0.08)',   border: 'rgba(255,179,64,0.2)'   },
  'Hormonal':         { color: 'var(--red)',    bg: 'rgba(255,87,87,0.08)',    border: 'rgba(255,87,87,0.2)'    },
  'Mental Health':    { color: 'var(--purple)', bg: 'rgba(167,139,250,0.08)', border: 'rgba(167,139,250,0.2)'  },
  'Musculoskeletal':  { color: 'var(--amber)',  bg: 'rgba(255,179,64,0.08)',   border: 'rgba(255,179,64,0.2)'   },
  'Cardiovascular':   { color: 'var(--red)',    bg: 'rgba(255,87,87,0.08)',    border: 'rgba(255,87,87,0.2)'    },
}

export default function SymptomSelector({ selected, onChange }) {
  const [search,         setSearch]   = useState('')
  const [activeCategory, setCategory] = useState('All')
  const [focused,        setFocused]  = useState(false)

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
          position: 'absolute', left: '13px', top: '50%',
          transform: 'translateY(-50%)',
          opacity: focused ? 0.8 : 0.35,
          transition: 'opacity 0.2s', pointerEvents: 'none',
        }} width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="6" cy="6" r="4.5" stroke="var(--teal)" strokeWidth="1.5"/>
          <path d="M9.5 9.5L13 13" stroke="var(--teal)" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search 180 symptoms..."
          style={{
            width: '100%', padding: '10px 36px 10px 38px',
            background: 'var(--bg2)',
            border: `1px solid ${focused ? 'var(--teal2)' : 'var(--border)'}`,
            borderRadius: 'var(--radius)', color: 'var(--text)',
            fontSize: '13px', outline: 'none',
            transition: 'border-color 0.2s, box-shadow 0.2s',
            boxShadow: focused ? '0 0 0 3px var(--teal-glow)' : 'none',
          }}
        />
        {search && (
          <button onClick={() => setSearch('')} style={{
            position: 'absolute', right: '10px', top: '50%',
            transform: 'translateY(-50%)',
            background: 'var(--border2)', border: 'none',
            borderRadius: '50%', width: '18px', height: '18px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--text2)', fontSize: '13px', lineHeight: 1,
            cursor: 'pointer',
          }}>×</button>
        )}
      </div>

      {/* Search result count */}
      {search.trim() && (
        <div style={{
          fontSize: '11px', fontFamily: 'var(--mono)',
          color: 'var(--text3)',
          animation: 'fadeIn 0.2s ease',
        }}>
          <span style={{ color: 'var(--teal)' }}>{filtered.length}</span>
          {' '}of {ALL_SYMPTOMS.length} symptoms match
          {' '}<span style={{ color: 'var(--text2)' }}>"{search}"</span>
        </div>
      )}

      {/* Category pills */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {categories.map(cat => {
          const isActive = activeCategory === cat
          const count    = cat === 'All' ? ALL_SYMPTOMS.length : (SYMPTOM_CATEGORIES[cat]?.length || 0)
          const catStyle = CATEGORY_COLORS[cat]

          return (
            <button key={cat} onClick={() => setCategory(cat)} style={{
              padding: '5px 11px', borderRadius: '20px', fontSize: '11px',
              fontWeight: 500, display: 'flex', alignItems: 'center', gap: '5px',
              background: isActive
                ? catStyle ? catStyle.bg : 'var(--teal-glow)'
                : 'var(--surface)',
              color: isActive
                ? catStyle ? catStyle.color : 'var(--teal)'
                : 'var(--text2)',
              border: `1px solid ${isActive
                ? catStyle ? catStyle.border : 'rgba(0,212,170,0.2)'
                : 'var(--border)'
              }`,
              transition: 'all 0.15s',
              fontFamily: 'var(--font)',
            }}>
              {cat}
              <span style={{
                fontSize: '9px', fontFamily: 'var(--mono)',
                opacity: isActive ? 0.8 : 0.4,
                background: isActive ? 'rgba(255,255,255,0.1)' : 'var(--border)',
                padding: '1px 5px', borderRadius: '6px',
              }}>
                {count}
              </span>
            </button>
          )
        })}
      </div>

      {/* Selected chips */}
      {selected.length > 0 && (
        <div style={{
          padding: '12px 14px',
          background: 'var(--teal-glow)',
          border: '1px solid rgba(0,212,170,0.2)',
          borderRadius: 'var(--radius)',
          animation: 'fadeIn 0.3s ease',
        }}>
          <div style={{
            display: 'flex', alignItems: 'center',
            justifyContent: 'space-between', marginBottom: '10px',
          }}>
            <span style={{
              fontSize: '11px', fontFamily: 'var(--mono)',
              color: 'var(--teal)', letterSpacing: '0.06em',
              display: 'flex', alignItems: 'center', gap: '6px',
            }}>
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                <path d="M1.5 5l2.5 2.5L8.5 2" stroke="currentColor" strokeWidth="1.8"
                  strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              {selected.length} SYMPTOM{selected.length !== 1 ? 'S' : ''} SELECTED
            </span>
            <button onClick={() => onChange([])} style={{
              fontSize: '11px', color: 'var(--text3)',
              fontFamily: 'var(--mono)', background: 'transparent',
              padding: '2px 8px', border: '1px solid var(--border)',
              borderRadius: '10px', transition: 'all 0.15s', cursor: 'pointer',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.color = 'var(--red)'
              e.currentTarget.style.borderColor = 'rgba(255,87,87,0.3)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color = 'var(--text3)'
              e.currentTarget.style.borderColor = 'var(--border)'
            }}
            >
              clear all
            </button>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {selected.map((s, i) => (
              <span key={s} onClick={() => toggle(s)} style={{
                padding: '4px 10px', borderRadius: '20px', fontSize: '12px',
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
                <span style={{ fontSize: '13px', lineHeight: 1 }}>×</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Symptom grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
        gap: '6px', maxHeight: '300px',
        overflowY: 'auto', paddingRight: '4px',
      }}>
        {filtered.map((sym, i) => {
          const isSelected = selected.includes(sym)
          return (
            <button key={sym} onClick={() => toggle(sym)} style={{
              padding: '9px 11px', textAlign: 'left', borderRadius: '8px',
              background: isSelected ? 'var(--teal-glow2)' : 'var(--surface)',
              border: `1px solid ${isSelected ? 'var(--teal)' : 'var(--border)'}`,
              color: isSelected ? 'var(--teal)' : 'var(--text2)',
              fontSize: '12px', fontWeight: isSelected ? 500 : 400,
              transition: 'all 0.12s', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '7px',
              animation: `fadeIn 0.15s ease ${Math.min(i * 0.008, 0.25)}s both`,
            }}
            onMouseEnter={e => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--border2)'
                e.currentTarget.style.color = 'var(--text)'
              }
            }}
            onMouseLeave={e => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.color = 'var(--text2)'
              }
            }}
            >
              {isSelected ? (
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none" style={{ flexShrink: 0 }}>
                  <path d="M1.5 5l2.5 2.5L8.5 2" stroke="var(--teal)" strokeWidth="1.8"
                    strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              ) : (
                <div style={{
                  width: '10px', height: '10px', borderRadius: '3px',
                  border: '1px solid var(--border2)', flexShrink: 0,
                }}/>
              )}
              <span style={{ lineHeight: 1.3 }}>{SYMPTOM_LABELS[sym]}</span>
            </button>
          )
        })}

        {filtered.length === 0 && (
          <div style={{
            gridColumn: '1/-1', padding: '32px 16px',
            textAlign: 'center', color: 'var(--text3)', fontSize: '13px',
            fontFamily: 'var(--mono)',
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
              style={{ margin: '0 auto 10px', display: 'block', opacity: 0.3 }}>
              <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="1.5"/>
              <path d="M21 21l-4.35-4.35" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
              <path d="M8 11h6M11 8v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            No symptoms match "{search}"
          </div>
        )}
      </div>
    </div>
  )
}