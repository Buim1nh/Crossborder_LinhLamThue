'use client'

import React from 'react'
import Link from 'next/link'
import { useReveal } from '@/hooks/useReveal'
import { PricingPlan } from '@/types/landing'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Badge'
export interface PricingCardProps extends PricingPlan {
  onSelect?: () => void
  className?: string
}

export function PricingCard({
  name,
  price,
  period,
  desc,
  features,
  highlight = false,
  onSelect,
  className = '',
}: PricingCardProps) {
  const { ref, visible } = useReveal()

  return (
    <div
      ref={ref}
      className={`rounded-xl p-6 sm:p-8 transition-all duration-700 flex flex-col justify-between ${
        highlight
          ? 'bg-primary text-white shadow-card-hover sm:-translate-y-2'
          : 'bg-white border border-neutral-200 shadow-card'
      } ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${className}`}
    >
      <div>
        {highlight && (
          <div className="mb-4 -mt-2">
            <Badge variant="neutral">PHỔ BIẾN NHẤT</Badge>
          </div>
        )}
        <p
          className={`text-sm font-semibold uppercase tracking-widest mb-1 ${
            highlight ? 'text-white/70' : 'text-neutral-500'
          }`}
        >
          {name}
        </p>
        <div className="flex items-baseline gap-1 mb-1">
          <p
            className={`font-display text-4xl sm:text-5xl leading-none font-semibold ${
              highlight ? 'text-white' : 'text-neutral-900'
            }`}
          >
            {price}
          </p>
          <p
            className={`text-sm ${
              highlight ? 'text-white/80' : 'text-neutral-500'
            }`}
          >
            {period.startsWith('vĩnh') ? `(${period})` : `/${period}`}
          </p>
        </div>
        <p
          className={`text-sm leading-relaxed mb-8 pb-8 border-b ${
            highlight
              ? 'border-white/20 text-white/80'
              : 'border-neutral-200 text-neutral-500'
          }`}
        >
          {desc}
        </p>
        <ul className="space-y-3 mb-8">
          {features.map((f, i) => (
            <li key={i} className="flex items-start gap-3">
              <svg
                className={`w-5 h-5 shrink-0 mt-0.5 ${
                  highlight ? 'text-white' : 'text-primary'
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span className={`text-sm ${highlight ? 'text-white' : 'text-neutral-700'}`}>
                {f}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {onSelect ? (
        <button
          onClick={onSelect}
          className={`w-full min-h-[48px] py-3.5 px-6 rounded-lg font-bold text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/30 active:scale-[0.99] ${
            highlight
              ? 'bg-white text-primary hover:bg-primary-light active:bg-orange-100'
              : 'bg-primary text-white hover:bg-primary-hover shadow-[0_2px_8px_rgba(255,107,26,0.3)] active:bg-orange-700'
          }`}
        >
          {highlight ? 'Bắt đầu dùng thử' : 'Chọn gói này'}
        </button>
      ) : (
        <Link href="/register" className="block w-full">
          <button
            type="button"
            className={`w-full min-h-[48px] py-3.5 px-6 rounded-lg font-bold text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-primary/30 active:scale-[0.99] ${
              highlight
                ? 'bg-white text-primary hover:bg-primary-light active:bg-orange-100'
                : 'bg-primary text-white hover:bg-primary-hover shadow-[0_2px_8px_rgba(255,107,26,0.3)] active:bg-orange-700'
            }`}
          >
            {highlight ? 'Bắt đầu dùng thử' : 'Chọn gói này'}
          </button>
        </Link>
      )}
    </div>
  )
}
