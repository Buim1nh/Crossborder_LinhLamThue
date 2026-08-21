'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'

export interface AnomalyItem {
  id: string
  title: string
  description: string
  amount: string
  sources: string[]
  severity: 'high' | 'medium' | 'info'
  date: string
  disputeDeadlineDays?: number
}

export interface AnomalyAlertBannerProps {
  anomalies?: AnomalyItem[]
  onDisputeClick?: (anomaly: AnomalyItem) => void
  onAskAIClick?: (anomaly: AnomalyItem) => void
  onDismissClick?: (anomalyId: string) => void
  className?: string
}

const DEFAULT_ANOMALIES: AnomalyItem[] = [
  {
    id: 'anom-netflix-dup',
    title: 'Phát hiện khoản trừ Netflix 260.000₫ bị trùng lặp 2 lần',
    description:
      'Giao dịch xuất hiện đồng thời trên Ví MoMo (02:15 AM ngày 15/02) và Thẻ Techcombank Visa **** 8829 (02:16 AM ngày 15/02).',
    amount: '-260.000₫',
    sources: ['Ví MoMo', 'Techcombank Visa'],
    severity: 'high',
    date: '15/02/2026',
    disputeDeadlineDays: 54,
  },
]

export function AnomalyAlertBanner({
  anomalies = DEFAULT_ANOMALIES,
  onDisputeClick,
  onAskAIClick,
  onDismissClick,
  className = '',
}: AnomalyAlertBannerProps) {
  const [dismissedIds, setDismissedIds] = useState<string[]>([])

  const activeAnomalies = anomalies.filter((a) => !dismissedIds.includes(a.id))
  if (activeAnomalies.length === 0) return null

  const current = activeAnomalies[0]

  const handleDismiss = () => {
    setDismissedIds([...dismissedIds, current.id])
    onDismissClick?.(current.id)
  }

  return (
    <div
      className={`rounded-2xl p-5 bg-gradient-to-r from-warning-light via-amber-50 to-orange-50 border border-warning/40 shadow-sm relative animate-in fade-in slide-in-from-top-2 duration-300 ${className}`}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Warning icon and description */}
        <div className="flex items-start gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-warning/20 text-[#B45309] flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
            <svg className="w-6 h-6 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#B45309] text-white">
                Cảnh báo đối chiếu đa nguồn
              </span>
              {current.disputeDeadlineDays && (
                <span className="text-xs font-semibold text-neutral-600">
                  Hạn tra soát ngân hàng: còn <strong className="text-danger">{current.disputeDeadlineDays} ngày</strong>
                </span>
              )}
            </div>

            <h3 className="text-sm sm:text-base font-bold text-neutral-900 leading-tight mb-1">
              {current.title}
            </h3>
            <p className="text-xs text-neutral-700 leading-relaxed max-w-3xl">
              {current.description}
            </p>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2.5 shrink-0 pt-2 lg:pt-0 border-t lg:border-t-0 border-amber-200">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAskAIClick?.(current)}
            className="text-xs bg-white/90 border-amber-300 text-neutral-800 hover:text-primary hover:border-primary"
          >
            💬 Hỏi AI Trợ Lý
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onDisputeClick?.(current)}
            className="text-xs font-bold bg-primary hover:bg-primary-hover shadow-sm"
          >
            Tạo Mẫu Tra Soát Ngân Hàng
          </Button>

          <button
            type="button"
            onClick={handleDismiss}
            className="p-1.5 text-neutral-400 hover:text-neutral-600 rounded-lg hover:bg-white/60 transition-colors ml-1"
            aria-label="Ẩn cảnh báo này"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
