import { useState, useMemo } from 'react'
import { ALL_SYMPTOMS, SYMPTOM_LABELS, SYMPTOM_CATEGORIES } from '../constants/symptoms'

export default function SymptomSelector({ selected, onChange }) {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState('All')

  const categories = ['All', ...Object.keys(SYMPTOM_CATEGORIES)]

  const filtered = useMemo(() => {
    let pool = activeCategory === 'All'
      ? ALL_SYMPTOMS
      : (SYMPTOM_CATEGORIES[activeCategory] || [])
    if (search.trim()) {
      const q = search.toLowerCase().replace(/\s+/g, '_')
      pool = pool.filter(s => s.includes(q) || SYMPTOM_LABELS[s].toLowerCase().includes(search.toLowerCase()))
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
    <div>
      {/* Search */}
      <div style={{ position: 'relative', marginBottom: '16px' }}>
        <svg style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.4 }}
          width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5" stroke="var(--text)" strokeWidth="1.5"/>
          <path d="M10.5 10.5L14 14" stroke="var(--text)" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search symptoms..."
          style={{
            width: '100%', padding: '10px 12px 10px 36px',
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: '8px', color: 'var(--text)', fontSize: '14px',
            outline: 'none', transition: 'border 0.2s',
          }}
          onFocus={e => e.target.style.borderColor = 'var(--teal)'}
          onBlur={e => e.target.style.borderColor = 'var(--border)'}
        />
      </div>

      {/* Category tabs */}
      <div style={{
        display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '16px',
      }}>
        {categories.map(cat => (
          <button key={cat} onClick={() => setActiveCategory(cat)} style={{
            padding: '4px 12px', borderRadius: '20px', fontSize: '12px',
            fontFamily: 'var(--font-body)', fontWeight: 500,
            background: activeCategory === cat ? 'var(--teal)' : 'var(--surface)',
            color: activeCategory === cat ? 'var(--bg)' : 'var(--text2)',
            border: `1px solid ${activeCategory === cat ? 'var(--teal)' : 'var(--border)'}`,
            transition: 'all 0.15s',
          }}>
            {cat}
          </button>
        ))}
      </div>

      {/* Selected pills */}
      {selected.length > 0 && (
        <div style={{
          padding: '10px 12px', background: 'var(--teal-glow)',
          border: '1px solid var(--teal-dim)', borderRadius: '8px',
          marginBottom: '16px',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--teal)', fontFamily: 'var(--font-mono)', marginBottom: '8px' }}>
            {selected.length} SYMPTOM{selected.length > 1 ? 'S' : ''} SELECTED
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {selected.map(s => (
              <span key={s} onClick={() => toggle(s)} style={{
                padding: '3px 10px', background: 'var(--teal)', color: 'var(--bg)',
                borderRadius: '20px', fontSize: '12px', fontWeight: 500,
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px',
              }}>
                {SYMPTOM_LABELS[s]}
                <span style={{ fontSize: '14px', lineHeight: 1 }}>×</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Symptom grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
        gap: '6px',
        maxHeight: '340px',
        overflowY: 'auto',
        paddingRight: '4px',
      }}>
        {filtered.map(sym => {
          const isSelected = selected.includes(sym)
          return (
            <button key={sym} onClick={() => toggle(sym)} style={{
              padding: '8px 10px', textAlign: 'left',
              background: isSelected ? 'var(--teal-glow)' : 'var(--surface)',
              border: `1px solid ${isSelected ? 'var(--teal)' : 'var(--border)'}`,
              borderRadius: '6px', color: isSelected ? 'var(--teal)' : 'var(--text2)',
              fontSize: '12px', fontFamily: 'var(--font-body)',
              transition: 'all 0.12s', cursor: 'pointer',
            }}
            onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border2)' }}
            onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--border)' }}
            >
              {SYMPTOM_LABELS[sym]}
            </button>
          )
        })}
        {filtered.length === 0 && (
          <div style={{ gridColumn: '1/-1', padding: '24px', textAlign: 'center', color: 'var(--text3)', fontSize: '13px' }}>
            No symptoms found for "{search}"
          </div>
        )}
      </div>
    </div>
  )
}