import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import type { Document } from '../types'

export default function Documents() {
  const { data, loading, refresh } = useApi(() => api.documents.list())
  const docs: Document[] = data?.documents ?? []
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ name: '', file_path: '' })
  const [saving, setSaving] = useState(false)

  async function addDoc() {
    if (!form.name.trim()) return
    setSaving(true)
    try {
      await api.documents.add({ name: form.name, file_path: form.file_path || `/documents/${form.name.toLowerCase().replace(/\s+/g, '_')}.pdf` })
      setForm({ name: '', file_path: '' })
      setAdding(false)
      refresh()
    } catch (e) {
      alert('Error: ' + (e instanceof Error ? e.message : e))
    } finally {
      setSaving(false)
    }
  }

  const statusVariant = (s: string): 'success' | 'warning' | 'error' | 'neutral' =>
    s === 'ready' ? 'success' : s === 'pending' ? 'warning' : s === 'expired' ? 'error' : 'neutral'

  return (
    <div style={{ padding: 28 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 24, margin: '0 0 4px', fontFamily: 'Manrope,sans-serif' }}>Documents</h2>
          <p style={{ color: 'var(--graphite)', fontSize: 14.5, margin: 0 }}>
            Documents RAAHI can access when preparing applications.
          </p>
        </div>
        <button
          onClick={() => setAdding(true)}
          style={{
            background: 'var(--accent)', color: '#fff', border: 'none',
            padding: '10px 18px', borderRadius: 'var(--radius-sm)',
            fontSize: 14, fontWeight: 600, cursor: 'pointer',
          }}
        >
          + Add Document
        </button>
      </div>

      {/* Add form */}
      {adding && (
        <Card style={{ marginBottom: 20, animation: 'slideUp .25s ease' }}>
          <h4 style={{ margin: '0 0 16px', fontFamily: 'Manrope,sans-serif' }}>Add New Document</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 12, color: 'var(--graphite-2)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Document Name *</label>
              <input
                value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Income Certificate"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid var(--border-2)', borderRadius: 'var(--radius-sm)', fontSize: 14, outline: 'none', background: 'var(--surface)' }}
              />
            </div>
            <div>
              <label style={{ fontSize: 12, color: 'var(--graphite-2)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.04em' }}>File Path</label>
              <input
                value={form.file_path}
                onChange={e => setForm(f => ({ ...f, file_path: e.target.value }))}
                placeholder="/documents/file.pdf"
                style={{ width: '100%', padding: '9px 12px', border: '1px solid var(--border-2)', borderRadius: 'var(--radius-sm)', fontSize: 14, outline: 'none', background: 'var(--surface)' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={addDoc}
              disabled={saving || !form.name.trim()}
              style={{ padding: '9px 20px', background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: 14, cursor: saving ? 'wait' : 'pointer' }}
            >
              {saving ? 'Saving…' : 'Save Document'}
            </button>
            <button
              onClick={() => setAdding(false)}
              style={{ padding: '9px 20px', background: 'transparent', color: 'var(--graphite)', border: '1px solid var(--border-2)', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: 14, cursor: 'pointer' }}
            >
              Cancel
            </button>
          </div>
        </Card>
      )}

      {/* Doc grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--graphite-2)' }}>Loading documents…</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14 }}>
          {docs.map(doc => (
            <Card key={doc.id} hover style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ width: 38, height: 38, borderRadius: 'var(--radius-sm)', background: 'var(--bg-alt)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>
                📄
              </div>
              <h4 style={{ margin: 0, fontSize: 14.5, fontFamily: 'Manrope,sans-serif', fontWeight: 600 }}>{doc.name}</h4>
              <div style={{ fontSize: 12, color: 'var(--graphite-2)' }}>Updated {doc.last_updated}</div>
              <Badge variant={statusVariant(doc.status)}>{doc.status}</Badge>
            </Card>
          ))}

          {docs.length === 0 && !adding && (
            <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: 48, color: 'var(--graphite-2)' }}>
              No documents yet. Add your documents so RAAHI can include them in applications.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
