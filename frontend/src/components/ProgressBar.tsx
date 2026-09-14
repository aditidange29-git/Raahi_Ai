import React from 'react'

interface Props {
  value: number // 0-100
  color?: string
  height?: number
}

export default function ProgressBar({ value, color = 'var(--accent)', height = 6 }: Props) {
  return (
    <div style={{
      height, borderRadius: 100, background: 'var(--bg-alt)', overflow: 'hidden',
    }}>
      <div style={{
        height: '100%', borderRadius: 100,
        background: color,
        width: `${Math.max(0, Math.min(100, value))}%`,
        transition: 'width .5s ease',
      }} />
    </div>
  )
}
