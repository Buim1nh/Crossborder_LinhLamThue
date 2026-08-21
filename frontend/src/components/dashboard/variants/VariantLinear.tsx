'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'

export interface VariantLinearProps {
  onDisputeClick?: (anomaly: any) => void
  onAIChatOpen?: () => void
}

export function VariantLinear({ onDisputeClick, onAIChatOpen }: VariantLinearProps) {
  const [sourceFilter, setSourceFilter] = useState<'all' | 'bank' | 'wallet' | 'card'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [onlyFlagged, setOnlyFlagged] = useState(false)
  const [selectedTx, setSelectedTx] = useState<any | null>(null)

  const transactions = [
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
      status: 'verified',
    },
    {
      id: 'tx-2',
      source: 'wallet',
      sourceName: 'Ví MoMo',
      merchant: 'Netflix Vietnam',
      description: 'Gói Premium Ultra HD',
      category: 'Giải trí',
      amount: -260000,
      date: '15/02/2026',
      time: '02:15',
      status: 'flagged',
      alertReason: 'Trừ tiền trùng lặp với thẻ Techcombank Visa cùng ngày',
      isSubscription: true,
    },
    {
      id: 'tx-3',
      source: 'card',
      sourceName: 'Techcombank Visa',
      merchant: 'Netflix.com',
      description: 'Recurring transaction #8829',
      category: 'Giải trí',
      amount: -260000,
      date: '15/02/2026',
      time: '02:16',
      status: 'flagged',
      alertReason: 'Trùng lặp 260.000₫ với giao dịch trên Ví MoMo',
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
      status: 'verified',
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
      status: 'verified',
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
      status: 'flagged',
      alertReason: 'Phí thường niên định kỳ - có thể liên hệ ngân hàng đề nghị hoàn phí',
      maskedCard: '8829',
    },
    {
      id: 'tx-7',
      source: 'card',
      sourceName: 'Techcombank Visa',
      merchant: 'Spotify AB',
      description: 'Gói nghe nhạc Premium cá nhân',
      category: 'Giải trí',
      amount: -59000,
      date: '08/02/2026',
      time: '03:10',
      status: 'subscription',
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
      status: 'subscription',
      isSubscription: true,
    },
  ]

  const filtered = transactions.filter((t) => {
    if (sourceFilter !== 'all' && t.source !== sourceFilter) return false
    if (onlyFlagged && t.status !== 'flagged') return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        t.merchant.toLowerCase().includes(q) ||
        t.description.toLowerCase().includes(q) ||
        t.category.toLowerCase().includes(q)
      )
    }
    return true
  })

  return (
    <div className="space-y-6">
      {/* ── Linear Metric Ribbon (Divided 4-Column Bar) ── */}
      <div className="bg-white rounded-xl border border-neutral-200 shadow-xs divide-y md:divide-y-0 md:divide-x divide-neutral-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
        <div className="p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-1">
            Dòng tiền ròng
          </p>
          <p className="text-2xl font-bold text-neutral-900 leading-tight">
            +17.150.000₫
          </p>
          <p className="text-xs text-neutral-500 mt-2">
            Thu: <span className="text-success font-semibold">+32.0M₫</span> · Chi: <span className="text-neutral-800 font-semibold">-14.8M₫</span>
          </p>
        </div>

        <div className="p-5">
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Cảnh báo đối chiếu
            </p>
            <span className="w-2 h-2 rounded-full bg-warning" />
          </div>
          <p className="text-2xl font-bold text-neutral-900 leading-tight">
            3 giao dịch
          </p>
          <p className="text-xs text-neutral-500 mt-2">
            2 khoản trùng lặp · 1 phí thường niên
          </p>
        </div>

        <div className="p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-1">
            Dịch vụ định kỳ
          </p>
          <p className="text-2xl font-bold text-neutral-900 leading-tight">
            4 gói đăng ký
          </p>
          <p className="text-xs text-neutral-500 mt-2">
            Tổng chi: <span className="font-semibold text-neutral-800">1.120.000₫ / tháng</span>
          </p>
        </div>

        <div className="p-5 bg-neutral-50/50">
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs font-semibold uppercase tracking-wider text-primary">
              Tiết kiệm tiềm năng
            </p>
            <span className="text-xs font-bold text-success">+610K/tháng</span>
          </div>
          <p className="text-2xl font-bold text-primary leading-tight">
            +610.000₫
          </p>
          <p className="text-xs text-neutral-500 mt-2">
            Từ việc hủy 1 trùng lặp & tra soát
          </p>
        </div>
      </div>

      {/* ── Anomaly Strip ── */}
      <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-sm">
        <div className="flex items-start gap-3">
          <span className="px-2 py-0.5 rounded text-xs font-bold bg-warning text-white mt-0.5">
            LƯU Ý
          </span>
          <div>
            <p className="font-bold text-amber-950">
              Giao dịch Netflix 260.000₫ bị trừ 2 lần trên Ví MoMo và Thẻ Visa
            </p>
            <p className="text-xs text-amber-900 mt-0.5">
              Thời hạn gửi khiếu nại ngân hàng còn 54 ngày.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={onAIChatOpen}
            className="text-xs bg-white text-neutral-800 border-neutral-300"
          >
            Hỏi trợ lý AI
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() =>
              onDisputeClick?.({
                id: 'tx-2',
                title: 'Trùng lặp Netflix 260.000₫',
                description: 'Giao dịch trừ 2 lần trên MoMo và Techcombank Visa',
                amount: '-260.000₫',
                date: '15/02/2026',
              })
            }
            className="text-xs font-bold"
          >
            Tạo mẫu tra soát
          </Button>
        </div>
      </div>

      {/* ── Main Ledger Table (Linear Style) ── */}
      <div className="bg-white rounded-xl border border-neutral-200 shadow-xs overflow-hidden">
        {/* Table Top Toolbar */}
        <div className="p-4 border-b border-neutral-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-neutral-50/50">
          {/* Segmented Source Tabs */}
          <div className="flex items-center gap-1 p-1 bg-neutral-200/60 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => setSourceFilter('all')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                sourceFilter === 'all'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Tất cả ({transactions.length})
            </button>
            <button
              type="button"
              onClick={() => setSourceFilter('bank')}
              className={`px-3 py-1.5 rounded-md transition-all ${
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
              className={`px-3 py-1.5 rounded-md transition-all ${
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
              className={`px-3 py-1.5 rounded-md transition-all ${
                sourceFilter === 'card'
                  ? 'bg-white text-neutral-900 shadow-xs'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
            >
              Thẻ tín dụng
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setOnlyFlagged(!onlyFlagged)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
                onlyFlagged
                  ? 'bg-warning text-white border-warning'
                  : 'bg-white text-neutral-700 border-neutral-200 hover:border-neutral-300'
              }`}
            >
              Chỉ xem cảnh báo
            </button>

            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm (/)..."
              className="px-3 py-1.5 rounded-lg bg-white border border-neutral-200 text-xs text-neutral-900 focus:outline-none focus:border-primary w-44"
            />
          </div>
        </div>

        {/* Ledger Rows */}
        <div className="divide-y divide-neutral-100 text-sm">
          {filtered.map((tx) => (
            <div
              key={tx.id}
              onClick={() => setSelectedTx(tx)}
              className="p-3.5 sm:px-5 hover:bg-neutral-50 transition-colors flex items-center justify-between gap-4 cursor-pointer group"
            >
              <div className="flex items-center gap-3.5 min-w-0">
                <span className="w-20 shrink-0 text-xs font-semibold px-2 py-0.5 rounded bg-neutral-100 text-neutral-700 text-center truncate">
                  {tx.sourceName}
                </span>

                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-neutral-900 truncate">{tx.merchant}</p>
                    {tx.status === 'flagged' && (
                      <span className="text-xs px-2 py-0.2 rounded font-bold bg-warning-light text-[#B45309]">
                        Trùng lặp
                      </span>
                    )}
                    {tx.isSubscription && (
                      <span className="text-xs px-2 py-0.2 rounded font-medium bg-neutral-100 text-neutral-600">
                        Định kỳ
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-neutral-500 truncate">{tx.description}</p>
                </div>
              </div>

              <div className="text-right shrink-0 flex items-center gap-4">
                <div>
                  <p
                    className={`font-bold ${
                      tx.amount > 0 ? 'text-success' : 'text-neutral-900'
                    }`}
                  >
                    {tx.amount > 0 ? `+${tx.amount.toLocaleString('vi-VN')}₫` : `${tx.amount.toLocaleString('vi-VN')}₫`}
                  </p>
                  <p className="text-xs text-neutral-400">{tx.date}</p>
                </div>
                <span className="text-neutral-300 group-hover:text-neutral-600 text-xs">→</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
