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
  incomeGrowth: '+12%',
  anomaliesCount: 3,
  unresolvedAnomalies: 2,
  subscriptionsCount: 4,
  monthlySubscriptionBurn: '1.120.000₫/tháng',
  savingsOpportunity: '+610.000₫/tháng',
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
      <div className="bg-white rounded-xl p-5 border border-neutral-200/80 shadow-card flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider">
              Dòng Tiền Tháng Này
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-success-light text-success">
              {data.incomeGrowth || '+12%'}
            </span>
          </div>
          <p className="font-display text-2xl sm:text-3xl font-semibold text-neutral-900 leading-tight">
            {data.netSavings}
          </p>
        </div>

        <div className="pt-3 mt-3 border-t border-neutral-100 flex justify-between items-center text-xs">
          <span className="text-neutral-500">
            Thu: <strong className="text-success font-semibold">{data.totalIncome}</strong>
          </span>
          <span className="text-neutral-500">
            Chi: <strong className="text-neutral-900 font-semibold">{data.totalExpense}</strong>
          </span>
        </div>
      </div>

      {/* ── Metric 2: Anomalies Flagged ── */}
      <div
        onClick={onAnomaliesClick}
        className="bg-white rounded-xl p-5 border border-warning/30 hover:border-warning shadow-card hover:shadow-card-hover transition-all cursor-pointer flex flex-col justify-between group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider">
              Cảnh Báo Bất Thường
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-warning-light text-[#B45309]">
              ⚠️ Cần xác nhận
            </span>
          </div>
          <p className="font-display text-2xl sm:text-3xl font-semibold text-neutral-900 leading-tight group-hover:text-primary transition-colors">
            {data.anomaliesCount} Giao Dịch
          </p>
        </div>

        <div className="pt-3 mt-3 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-500">
          <span>{data.unresolvedAnomalies} khoản chưa xử lý</span>
          <span className="text-primary font-bold group-hover:underline">Xem ngay →</span>
        </div>
      </div>

      {/* ── Metric 3: Subscriptions ── */}
      <div
        onClick={onSubscriptionsClick}
        className="bg-white rounded-xl p-5 border border-neutral-200/80 hover:border-primary/50 shadow-card hover:shadow-card-hover transition-all cursor-pointer flex flex-col justify-between group"
      >
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-wider">
              Dịch Vụ Định Kỳ
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-primary-light text-primary">
              Tự động trừ tiền
            </span>
          </div>
          <p className="font-display text-2xl sm:text-3xl font-semibold text-neutral-900 leading-tight">
            {data.subscriptionsCount} Gói Đăng Ký
          </p>
        </div>

        <div className="pt-3 mt-3 border-t border-neutral-100 flex justify-between items-center text-xs text-neutral-500">
          <span>Tiêu hao: <strong className="text-neutral-900">{data.monthlySubscriptionBurn}</strong></span>
          <span className="text-primary font-bold group-hover:underline">Chi tiết →</span>
        </div>
      </div>

      {/* ── Metric 4: Savings Opportunity ── */}
      <div className="bg-primary-light/40 rounded-xl p-5 border border-primary/30 shadow-card flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-primary uppercase tracking-wider">
              Tiềm Năng Tiết Kiệm
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-success text-white">
              AI Đề Xuất
            </span>
          </div>
          <p className="font-display text-2xl sm:text-3xl font-semibold text-primary leading-tight">
            {data.savingsOpportunity}
          </p>
        </div>

        <div className="pt-3 mt-3 border-t border-primary/20 flex justify-between items-center text-xs text-neutral-700">
          <span>Từ việc hủy 1 khoản trùng & 1 phí ẩn</span>
        </div>
      </div>
    </div>
  )
}
