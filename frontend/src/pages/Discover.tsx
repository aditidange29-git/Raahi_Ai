import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import type { Opportunity } from '../types'

interface Props { onNav: (p: string) => void }

const CATEGORIES = ['all', 'scholarship', 'internship', 'grant', 'program']

export default function Discover({ onNav }: Props) {
  const [category, setCategory] = useState('all')
  const [keyword, setKeyword] = useState('')
  const [launching, setLaunching] = useState<string | null>(null)
  const [launched, setLaunched] = useState<string | null>(null)

  const { data, loading } = useApi(
    () => api.opportunities.list({ category, keyword }),
    [category, keyword]
  )
  const opportunities: Opportunity[] = data?.opportunities ?? []

  async function startMission(opp: Opportunity) {
    setLaunching(opp.id)
    try {
      await api.missions.create({ opportunity_id: opp.id })
      setLaunched(opp.id)
      setTimeout(() => onNav('missions'), 1500)
    } catch (e) {
      alert('Failed to start mission: ' + (e instanceof Error ? e.message : e))
    } finally {
      setLaunching(null)
    }
  }

  function scoreColor(s: number) {
    if (s >= 0.85) return 'var(--success)'
    if (s >= 0.65) return 'var(--warning)'
    return 'var(--error)'
  }

  return (
    <div style={{ padding: 28 }}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Discover Opportunities</h2>
        <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
          RAAHI matches opportunities to your profile. Start a mission to handle the rest automatically.
        </p>
      </div>

      {/* Search + filters */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
        <div style={{
          flex: 1, minWidth: 200, display: 'flex', alignItems: 'center', gap: 8,
          padding: '9px 14px', border: '1px solid var(--border-2)',
          borderRadius: 'var(--radius-sm)', background: 'var(--surface)',
        }}>
          <span style={{ color: 'var(--graphite-2)' }}>🔍</span>
          <input
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            placeholder="Search opportunities…"
            style={{ border: 'none', outline: 'none', background: 'transparent', fontSize: 14, width: '100%', color: 'var(--ink)' }}
          />
        </div>
      </div>

      {/* Category chips */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 22 }}>
        {CATEGORIES.map(c => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            style={{
              padding: '7px 14px', borderRadius: 100,
              border: `1px solid ${category === c ? 'var(--accent)' : 'var(--border-2)'}`,
              fontSize: 13, fontWeight: 600,
              color: category === c ? '#fff' : 'var(--graphite)',
              background: category === c ? 'var(--accent)' : 'var(--surface)',
              cursor: 'pointer', transition: 'all .15s',
            }}
          >
            {c.charAt(0).toUpperCase() + c.slice(1)}
          </button>
        ))}
      </div>

      {/* Opportunity grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--graphite-2)' }}>
          <div style={{ fontSize: 32, marginBottom: 12, animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</div>
          <p>Loading opportunities…</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 14 }}>
          {opportunities.map(opp => (
            <Card key={opp.id} hover style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {/* Top */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 4px', fontSize: 16, fontFamily: 'Manrope,sans-serif', fontWeight: 700 }}>{opp.title}</h4>
                  <span style={{ fontSize: 12, color: 'var(--graphite-2)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                    {opp.category}
                  </span>
                </div>
                {/* Match ring */}
                <div style={{
                  width: 50, height: 50, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: `conic-gradient(${scoreColor(opp.eligibility_score)} ${opp.eligibility_score * 100}%, var(--bg-alt) 0)`,
                }}>
                  <div style={{
                    background: 'var(--surface)', width: 38, height: 38, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 12, fontWeight: 800, color: scoreColor(opp.eligibility_score),
                  }}>
                    {Math.round(opp.eligibility_score * 100)}%
                  </div>
                </div>
              </div>

              {/* Meta */}
              <div style={{ display: 'flex', gap: 18, fontSize: 13, color: 'var(--graphite)', flexWrap: 'wrap' }}>
                <span>💰 <b style={{ color: 'var(--ink)' }}>{opp.prize_amount ?? 'Varies'}</b></span>
                <span>📅 <b style={{ color: 'var(--ink)' }}>{opp.deadline}</b></span>
              </div>

              {/* Description */}
              <p style={{
                fontSize: 13, color: 'var(--graphite)', background: 'var(--bg-alt)',
                padding: '10px 12px', borderRadius: 'var(--radius-sm)', margin: 0, fontStyle: 'italic',
              }}>
                {opp.description.slice(0, 120)}…
              </p>

              {/* Actions */}
              <div style={{ display: 'flex', gap: 10, marginTop: 2 }}>
                <button
                  onClick={() => startMission(opp)}
                  disabled={!!launching || launched === opp.id}
                  style={{
                    flex: 1, padding: '9px 0', borderRadius: 'var(--radius-sm)',
                    background: launched === opp.id ? 'var(--success)' : 'var(--accent)',
                    color: '#fff', border: 'none', fontSize: 14, fontWeight: 600,
                    cursor: launching ? 'wait' : 'pointer', opacity: (launching && launching !== opp.id) ? 0.5 : 1,
                    transition: 'background .18s',
                  }}
                >
                  {launched === opp.id ? '✓ Mission Started!' : launching === opp.id ? 'Starting…' : '⚡ Start Mission'}
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
