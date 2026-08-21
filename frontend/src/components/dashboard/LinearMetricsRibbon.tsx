'use client'

import React from 'react'

export interface FinancialMetricsData {
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

export interface LinearMetricsRibbonProps {
  data?: FinancialMetricsData
  onAnomaliesClick?: () => void
  onSubscriptionsClick?: () => void
  className?: string
}

const DEFAULT_METRICS: FinancialMetricsData = {
  totalIncome: '+32.000.000₫',
  totalExpense: '-14.850.000₫',
  netSavings: '+17.150.000₫',
  incomeGrowth: '+12%',
  anomaliesCount: 3,
  unresolvedAnomalies: 2,
  subscriptionsCount: 4,
  monthlySubscriptionBurn: '1.120.000₫',
  savingsOpportunity: '+610.000₫ / tháng',
}

export function LinearMetricsRibbon({
  data = DEFAULT_METRICS,
  onAnomaliesClick,
  onSubscriptionsClick,
  className = '',
}: LinearMetricsRibbonProps) {
  return (
    <div
      className={`bg-white rounded-2xl border border-neutral-200 shadow-card divide-y md:divide-y-0 md:divide-x divide-neutral-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 ${className}`}
    >
      {/* ── Metric 1: Net Cashflow ── */}
      <div className="p-6 sm:p-7 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-neutral-500">
              Dòng tiền ròng
            </span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-success-light text-success">
              {data.incomeGrowth || '+12%'}
            </span>
          </div>
          <p className="text-3xl sm:text-4xl font-bold text-neutral-900 leading-tight">
            {data.netSavings}
          </p>
        </div>

        <div className="pt-4 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs sm:text-sm text-neutral-600">
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
        aria-label={`Cảnh báo đối chiếu: ${data.anomaliesCount} giao dịch cần xác nhận`}
        className="p-6 sm:p-7 flex flex-col justify-between hover:bg-neutral-50/70 focus:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors cursor-pointer group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-neutral-500">
              Cảnh báo chi tiêu
            </span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-warning-light text-[#B45309]">
              Cần xác nhận
            </span>
          </div>
          <p className="text-3xl sm:text-4xl font-bold text-neutral-900 leading-tight group-hover:text-primary transition-colors">
            {data.anomaliesCount} giao dịch
          </p>
        </div>

        <div className="pt-4 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs sm:text-sm text-neutral-500">
          <span>{data.unresolvedAnomalies} khoản chưa tra soát</span>
          <span className="text-primary font-bold group-hover:underline">Chi tiết →</span>
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
        className="p-6 sm:p-7 flex flex-col justify-between hover:bg-neutral-50/70 focus:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors cursor-pointer group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-neutral-500">
              Dịch vụ định kỳ
            </span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-700">
              Tự động trừ tiền
            </span>
          </div>
          <p className="text-3xl sm:text-4xl font-bold text-neutral-900 leading-tight">
            {data.subscriptionsCount} gói đăng ký
          </p>
        </div>

        <div className="pt-4 mt-4 border-t border-neutral-100 flex justify-between items-center text-xs sm:text-sm text-neutral-600">
          <span>Tiêu hao: <strong className="text-neutral-900">{data.monthlySubscriptionBurn}/tháng</strong></span>
          <span className="text-primary font-bold group-hover:underline">Xem →</span>
        </div>
      </div>

      {/* ── Metric 4: Savings Potential ── */}
      <div className="p-6 sm:p-7 flex flex-col justify-between bg-primary-light/30">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-primary">
              Tiềm năng tiết kiệm
            </span>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-success text-white">
              AI Đề xuất
            </span>
          </div>
          <p className="text-3xl sm:text-4xl font-bold text-primary leading-tight">
            {data.savingsOpportunity}
          </p>
        </div>

        <div className="pt-4 mt-4 border-t border-primary/20 flex justify-between items-center text-xs sm:text-sm text-neutral-700">
          <span>Từ việc hủy 1 trùng lặp & 1 phí ẩn</span>
        </div>
      </div>
    </div>
  )
}
