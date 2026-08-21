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
    title: 'Phát hiện giao dịch Netflix 260.000₫ bị trừ trùng lặp 2 lần',
    description:
      'Giao dịch xuất hiện đồng thời trên Ví MoMo (02:15 ngày 15/02) và Thẻ Techcombank Visa **** 8829 (02:16 ngày 15/02).',
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
      role="alert"
      aria-live="polite"
      className={`rounded-2xl p-5 bg-amber-50/90 border border-amber-200 text-amber-950 shadow-card relative ${className}`}
    >
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Info & Description */}
        <div>
          <div className="flex items-center gap-2.5 flex-wrap mb-1.5">
            <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-warning text-white">
              Cảnh báo đối chiếu
            </span>
            {current.disputeDeadlineDays && (
              <span className="text-xs font-semibold text-amber-900">
                Hạn tra soát ngân hàng: <strong className="text-danger">{current.disputeDeadlineDays} ngày còn lại</strong>
              </span>
            )}
          </div>

          <h3 className="text-base font-bold text-amber-950 leading-snug mb-1">
            {current.title}
          </h3>
          <p className="text-sm text-amber-900/90 leading-relaxed max-w-3xl">
            {current.description}
          </p>
        </div>
        {/* Right: Actions */}
        <div className="flex items-center gap-3 shrink-0 pt-2 lg:pt-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAskAIClick?.(current)}
            className="text-xs bg-white text-neutral-800 border-neutral-300 hover:border-primary hover:text-primary font-medium"
          >
            Hỏi trợ lý AI
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onDisputeClick?.(current)}
            className="text-xs font-bold bg-primary hover:bg-primary-hover shadow-xs"
          >
            Tạo mẫu tra soát
          </Button>

          <button
            type="button"
            onClick={handleDismiss}
            className="text-xs text-amber-800 hover:text-amber-950 px-2 py-1 transition-colors"
          >
            Bỏ qua
          </button>
        </div>
      </div>
    </div>
  )
}
