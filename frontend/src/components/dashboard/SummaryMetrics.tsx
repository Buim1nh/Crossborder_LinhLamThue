'use client'

import React from 'react'

export interface FinancialSummaryData {
  totalIncome: string
  totalExpense: string
  netSavings: string
  incomeGrowth?: string
  anomaliesCount: number
  unresolvedAnomalies: number
  subscriptionsCount: number
  monthlySubscriptionBurn: string
  savingsOpportunity: string
}

export interface SummaryMetricsProps {
  data?: FinancialSummaryData
  onAnomaliesClick?: () => void
  onSubscriptionsClick?: () => void
  className?: string
}

const DEFAULT_SUMMARY_DATA: FinancialSummaryData = {
  totalIncome: '+32.000.000₫',
  totalExpense: '-14.850.000₫',
  netSavings: '+17.150.000₫',
  incomeGrowth: '+12% so với tháng trước',
  anomaliesCount: 3,
  unresolvedAnomalies: 2,
  subscriptionsCount: 4,
  monthlySubscriptionBurn: '1.120.000₫',
  savingsOpportunity: '+610.000₫ / tháng',
}

export function SummaryMetrics({
  data = DEFAULT_SUMMARY_DATA,
  onAnomaliesClick,
  onSubscriptionsClick,
  className = '',
}: SummaryMetricsProps) {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {/* ── Metric 1: Cashflow ── */}
      <div className="bg-white rounded-xl p-5 border border-neutral-200 shadow-card flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Dòng tiền ròng
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-success-light text-success">
              {data.incomeGrowth || '+12%'}
            </span>
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-neutral-900 leading-tight">
            {data.netSavings}
          </p>
        </div>

        <div className="pt-3 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-600">
          <span>Thu: <strong className="text-success font-semibold">{data.totalIncome}</strong></span>
          <span>Chi: <strong className="text-neutral-900 font-semibold">{data.totalExpense}</strong></span>
        </div>
      </div>

      {/* ── Metric 2: Anomalies ── */}
      <div
        role="button"
        tabIndex={0}
        onClick={onAnomaliesClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onAnomaliesClick?.()
          }
        }}
        aria-label={`Cảnh báo chi tiêu: ${data.anomaliesCount} giao dịch cần xác nhận`}
        className="bg-white rounded-xl p-5 border border-warning/40 hover:border-warning focus:border-warning focus:outline-none focus:ring-2 focus:ring-primary/20 shadow-card hover:shadow-card-hover transition-all cursor-pointer flex flex-col justify-between group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Cảnh báo chi tiêu
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-warning-light text-[#B45309]">
              Cần xác nhận
            </span>
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-neutral-900 leading-tight group-hover:text-primary transition-colors">
            {data.anomaliesCount} giao dịch
          </p>
        </div>

        <div className="pt-3 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-500">
          <span>{data.unresolvedAnomalies} khoản chưa tra soát</span>
          <span className="text-primary font-semibold group-hover:underline">Chi tiết →</span>
        </div>
      </div>

      {/* ── Metric 3: Subscriptions ── */}
      <div
        role="button"
        tabIndex={0}
        onClick={onSubscriptionsClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onSubscriptionsClick?.()
          }
        }}
        aria-label={`Dịch vụ định kỳ: ${data.subscriptionsCount} gói đăng ký tiêu hao ${data.monthlySubscriptionBurn}`}
        className="bg-white rounded-xl p-5 border border-neutral-200 hover:border-primary/50 focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/20 shadow-card hover:shadow-card-hover transition-all cursor-pointer flex flex-col justify-between group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Dịch vụ định kỳ
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700">
              Tự động gia hạn
            </span>
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-neutral-900 leading-tight">
            {data.subscriptionsCount} gói đăng ký
          </p>
        </div>

        <div className="pt-3 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-600">
          <span>Tiêu hao: <strong className="text-neutral-900">{data.monthlySubscriptionBurn}/tháng</strong></span>
          <span className="text-primary font-semibold group-hover:underline">Xem →</span>
        </div>
      </div>

      {/* ── Metric 4: Savings Potential ── */}
      <div className="bg-primary-light/40 rounded-xl p-5 border border-primary/30 shadow-card flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              Tiềm năng tiết kiệm
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded bg-success text-white">
              AI Đề xuất
            </span>
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-primary leading-tight">
            {data.savingsOpportunity}
          </p>
        </div>

        <div className="pt-3 mt-4 border-t border-primary/20 flex justify-between items-center text-xs text-neutral-700">
          <span>Hủy 1 trùng lặp & 1 phí thường niên</span>
        </div>
      </div>
    </div>
  )
}
