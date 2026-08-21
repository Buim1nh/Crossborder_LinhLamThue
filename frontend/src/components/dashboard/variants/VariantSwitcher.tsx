'use client'

import React from 'react'

export type DashboardVariantId = 'linear' | 'bento' | 'terminal'

export interface VariantSwitcherProps {
  currentVariant: DashboardVariantId
  onSelectVariant: (variant: DashboardVariantId) => void
  className?: string
}

export function VariantSwitcher({
  currentVariant,
  onSelectVariant,
  className = '',
}: VariantSwitcherProps) {
  const variants: Array<{ id: DashboardVariantId; label: string; tag: string }> = [
    { id: 'linear', label: '1. Linear Minimalist', tag: 'Thoáng · Gọn' },
    { id: 'bento', label: '2. Bento Studio', tag: 'Apple · Khối' },
    { id: 'terminal', label: '3. Financial Terminal', tag: 'Chuyên gia · Dữ liệu' },
  ]

  return (
    <div
      className={`bg-neutral-900 text-white rounded-2xl p-2 sm:p-2.5 shadow-2xl border border-neutral-700/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${className}`}
    >
      <div className="flex items-center gap-2.5 px-3">
        <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
        <span className="text-xs font-bold uppercase tracking-wider text-neutral-300">
          Chế độ giao diện (3 Phiên bản)
        </span>
      </div>

      <div className="flex items-center gap-1.5 p-1 bg-neutral-800 rounded-xl text-xs">
        {variants.map((v) => {
          const isActive = currentVariant === v.id
          return (
            <button
              key={v.id}
              type="button"
              onClick={() => onSelectVariant(v.id)}
              className={`px-3 py-2 rounded-lg font-semibold transition-all flex items-center gap-2 ${
                isActive
                  ? 'bg-primary text-white shadow-xs scale-[1.02]'
                  : 'text-neutral-300 hover:text-white hover:bg-neutral-700/60'
              }`}
            >
              <span>{v.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded font-normal ${
                  isActive ? 'bg-white/20 text-white' : 'bg-neutral-700 text-neutral-400'
                }`}
              >
                {v.tag}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
