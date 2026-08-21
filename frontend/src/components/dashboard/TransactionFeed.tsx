'use client'

import React, { useState } from 'react'

export type TransactionSourceType = 'bank' | 'wallet' | 'card'

export interface DashboardTransaction {
  id: string | number
  source: TransactionSourceType
  sourceName: string
  merchant: string
  description: string
  category: string
  amount: number
  currency?: string
  date: string
  time?: string
  isFlagged?: boolean
  alertReason?: string
  isSubscription?: boolean
  maskedCard?: string
}

export interface TransactionFeedProps {
  transactions?: DashboardTransaction[]
  onTransactionClick?: (tx: DashboardTransaction) => void
  className?: string
}

const SAMPLE_TRANSACTIONS: DashboardTransaction[] = [
  {
    id: 'tx-1',
    source: 'bank',
    sourceName: 'Vietcombank',
    merchant: 'Công Ty Công Nghệ ABC',
    description: 'Chuyển lương tháng 02/2026',
    category: 'Thu nhập',
    amount: 32000000,
    date: '15/02/2026',
    time: '09:30',
  },
  {
    id: 'tx-2',
    source: 'wallet',
    sourceName: 'Ví MoMo',
    merchant: 'Netflix Vietnam',
    description: 'Thanh toán gói Premium Ultra HD',
    category: 'Giải trí',
    amount: -260000,
    date: '15/02/2026',
    time: '02:15',
    isFlagged: true,
    alertReason: 'Phát hiện trừ tiền trùng lặp với thẻ Techcombank Visa cùng ngày',
    isSubscription: true,
  },
  {
    id: 'tx-3',
    source: 'card',
    sourceName: 'Techcombank Visa',
    merchant: 'Netflix.com',
    description: 'Recurring subscription #8829',
    category: 'Giải trí',
    amount: -260000,
    date: '15/02/2026',
    time: '02:16',
    isFlagged: true,
    alertReason: 'Khoản trừ 260.000₫ trùng lặp với Ví MoMo',
    isSubscription: true,
    maskedCard: '8829',
  },
  {
    id: 'tx-4',
    source: 'bank',
    sourceName: 'Vietcombank',
    merchant: 'EVN TP.HCM',
    description: 'Hóa đơn tiền điện sinh hoạt mã PE0200...',
    category: 'Hóa đơn',
    amount: -1450000,
    date: '14/02/2026',
    time: '14:20',
  },
  {
    id: 'tx-5',
    source: 'wallet',
    sourceName: 'Ví MoMo',
    merchant: 'GrabFood Vietnam',
    description: 'Bữa trưa văn phòng',
    category: 'Ăn uống',
    amount: -125000,
    date: '14/02/2026',
    time: '12:05',
  },
  {
    id: 'tx-6',
    source: 'card',
    sourceName: 'Techcombank Visa',
    merchant: 'Ngân hàng Techcombank',
    description: 'Phí thường niên thẻ tín dụng Signature',
    category: 'Phí ngân hàng',
    amount: -350000,
    date: '10/02/2026',
    time: '08:00',
    isFlagged: true,
    alertReason: 'Phí thường niên định kỳ — có thể liên hệ ngân hàng đề nghị hoàn phí',
    maskedCard: '8829',
  },
  {
    id: 'tx-7',
    source: 'card',
    sourceName: 'Techcombank Visa',
    merchant: 'Spotify AB',
    description: 'Gói nghe nhạc Premium',
    category: 'Giải trí',
    amount: -59000,
    date: '08/02/2026',
    time: '03:10',
    isSubscription: true,
    maskedCard: '8829',
  },
  {
    id: 'tx-8',
    source: 'wallet',
    sourceName: 'Ví MoMo',
    merchant: 'OpenAI ChatGPT Plus',
    description: 'Gia hạn gói dịch vụ AI $20',
    category: 'Công việc',
    amount: -500000,
    date: '05/02/2026',
    time: '01:00',
    isSubscription: true,
  },
]

export function TransactionFeed({
  transactions = SAMPLE_TRANSACTIONS,
  onTransactionClick,
  className = '',
}: TransactionFeedProps) {
  const [sourceFilter, setSourceFilter] = useState<'all' | 'bank' | 'wallet' | 'card'>('all')
  const [onlyFlagged, setOnlyFlagged] = useState(false)
  const [onlySubscription, setOnlySubscription] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const flaggedCount = transactions.filter((t) => t.isFlagged).length
  const subscriptionCount = transactions.filter((t) => t.isSubscription).length

  const filteredList = transactions.filter((tx) => {
    if (sourceFilter === 'bank' && tx.source !== 'bank') return false
    if (sourceFilter === 'wallet' && tx.source !== 'wallet') return false
    if (sourceFilter === 'card' && tx.source !== 'card') return false

    if (onlyFlagged && !tx.isFlagged) return false
    if (onlySubscription && !tx.isSubscription) return false

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        tx.merchant.toLowerCase().includes(q) ||
        tx.description.toLowerCase().includes(q) ||
        tx.category.toLowerCase().includes(q) ||
        tx.sourceName.toLowerCase().includes(q)
      )
    }
    return true
  })

  const formatVND = (num: number) => {
    const formatted = Math.abs(num).toLocaleString('vi-VN')
    if (num > 0) return `+${formatted}₫`
    return `-${formatted}₫`
  }

  const getSourceBadgeClass = (source: TransactionSourceType) => {
    switch (source) {
      case 'bank':
        return 'bg-success-light text-success border-success/20'
      case 'wallet':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      case 'card':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      default:
        return 'bg-neutral-100 text-neutral-700 border-neutral-200'
    }
  }

  return (
    <div className={`bg-white rounded-2xl shadow-card border border-neutral-200 overflow-hidden ${className}`}>
      {/* Header bar & Search */}
      <div className="p-6 border-b border-neutral-100">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-lg font-bold text-neutral-900 leading-tight">
              Lịch Sử Giao Dịch Hợp Nhất
            </h2>
            <p className="text-xs text-neutral-500 mt-1">
              Hiển thị {filteredList.length} / {transactions.length} giao dịch đã được đối chiếu & phân loại
            </p>
          </div>

          {/* Search box */}
          <div className="relative w-full sm:w-72">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm giao dịch, danh mục..."
              className="w-full pl-9 pr-4 py-2 rounded-lg bg-neutral-50 border border-neutral-200 text-sm text-neutral-900 focus:outline-none focus:border-primary focus:bg-white transition-all placeholder:text-neutral-400"
            />
            <svg
              className="w-4 h-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        {/* ── Multi-Faceted Filters ── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
          {/* Source Filter Segmented Control */}
          <div className="flex items-center p-1 bg-neutral-100 rounded-lg gap-1 text-xs overflow-x-auto">
            <button
              type="button"
              onClick={() => setSourceFilter('all')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                sourceFilter === 'all'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Tất cả nguồn ({transactions.length})
            </button>

            <button
              type="button"
              onClick={() => setSourceFilter('bank')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                sourceFilter === 'bank'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Ngân hàng
            </button>

            <button
              type="button"
              onClick={() => setSourceFilter('wallet')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                sourceFilter === 'wallet'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Ví điện tử
            </button>

            <button
              type="button"
              onClick={() => setSourceFilter('card')}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                sourceFilter === 'card'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Thẻ tín dụng
            </button>
          </div>

          {/* Status Facets */}
          <div className="flex items-center gap-2 text-xs">
            <button
              type="button"
              onClick={() => setOnlyFlagged(!onlyFlagged)}
              className={`px-3 py-1.5 rounded-md font-semibold border transition-all flex items-center gap-1.5 ${
                onlyFlagged
                  ? 'bg-warning text-white border-warning'
                  : 'bg-white text-neutral-700 border-neutral-200 hover:border-warning hover:text-[#B45309]'
              }`}
            >
              <span>Cảnh báo bất thường</span>
              <span className={`px-1.5 py-0.2 rounded text-[11px] font-bold ${onlyFlagged ? 'bg-white/20 text-white' : 'bg-warning-light text-[#B45309]'}`}>
                {flaggedCount}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setOnlySubscription(!onlySubscription)}
              className={`px-3 py-1.5 rounded-md font-semibold border transition-all flex items-center gap-1.5 ${
                onlySubscription
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-neutral-700 border-neutral-200 hover:border-primary hover:text-primary'
              }`}
            >
              <span>Gói định kỳ</span>
              <span className={`px-1.5 py-0.2 rounded text-[11px] font-bold ${onlySubscription ? 'bg-white/20 text-white' : 'bg-primary-light text-primary'}`}>
                {subscriptionCount}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Transaction List Rows */}
      <div className="divide-y divide-neutral-100 overflow-x-auto">
        {filteredList.length === 0 ? (
          <div className="py-16 text-center text-neutral-500 text-sm">
            Không tìm thấy giao dịch nào phù hợp với bộ lọc.
          </div>
        ) : (
          filteredList.map((tx) => (
            <div
              key={tx.id}
              role="button"
              tabIndex={0}
              onClick={() => onTransactionClick?.(tx)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onTransactionClick?.(tx)
                }
              }}
              aria-label={`Giao dịch ${tx.merchant} ${formatVND(tx.amount)}`}
              className={`p-4 sm:px-6 hover:bg-neutral-50 focus:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-inset transition-colors cursor-pointer ${
                tx.isFlagged ? 'bg-amber-50/40' : ''
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                {/* Left: Source Tag, Merchant, and Category */}
                <div className="flex items-start gap-4">
                  <div className="pt-0.5">
                    <span
                      className={`inline-block px-2.5 py-1 text-xs font-semibold rounded border ${getSourceBadgeClass(
                        tx.source
                      )}`}
                    >
                      {tx.sourceName}
                    </span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <p className="text-sm font-bold text-neutral-900">
                        {tx.merchant}
                      </p>

                      <span className="text-xs font-medium px-2 py-0.5 rounded bg-neutral-100 text-neutral-600">
                        {tx.category}
                      </span>

                      {tx.isSubscription && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-primary-light text-primary">
                          Định kỳ
                        </span>
                      )}

                      {tx.maskedCard && (
                        <span className="text-xs text-neutral-400 font-mono">
                          •••• {tx.maskedCard}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-neutral-600 mt-1">{tx.description}</p>

                    {/* Inline Anomaly Callout */}
                    {tx.isFlagged && tx.alertReason && (
                      <div className="mt-2.5 p-2.5 rounded-lg bg-warning-light/90 border border-warning/30 text-xs text-[#92400E] flex items-center gap-2">
                        <span className="font-bold shrink-0">Lưu ý:</span>
                        <span>{tx.alertReason}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Right: Date, Time and Amount */}
                <div className="text-right shrink-0">
                  <p
                    className={`text-base sm:text-lg font-bold leading-tight ${
                      tx.amount > 0 ? 'text-success' : 'text-neutral-900'
                    }`}
                  >
                    {formatVND(tx.amount)}
                  </p>
                  <p className="text-xs text-neutral-400 mt-1">
                    {tx.date} {tx.time ? `• ${tx.time}` : ''}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
