import React from 'react'

interface Props {
  children: React.ReactNode
  hover?: boolean
  style?: React.CSSProperties
  onClick?: () => void
}

export default function Card({ children, hover, style, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: 20,
        cursor: onClick ? 'pointer' : undefined,
        transition: hover || onClick ? 'border-color .18s, box-shadow .18s' : undefined,
        ...style,
      }}
      onMouseEnter={e => {
        if (hover || onClick) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border-2)'
          ;(e.currentTarget as HTMLDivElement).style.boxShadow = 'var(--shadow-sm)'
        }
      }}
      onMouseLeave={e => {
        if (hover || onClick) {
          (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border)'
          ;(e.currentTarget as HTMLDivElement).style.boxShadow = 'none'
        }
      }}
    >
      {children}
    </div>
  )
}
