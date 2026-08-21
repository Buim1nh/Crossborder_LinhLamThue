'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'

export interface VariantBentoProps {
  onDisputeClick?: (anomaly: any) => void
  onAIChatOpen?: () => void
}

export function VariantBento({ onDisputeClick, onAIChatOpen }: VariantBentoProps) {
  const [activeSource, setActiveSource] = useState<'all' | 'bank' | 'wallet' | 'card'>('all')

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
      isFlagged: true,
      alertReason: 'Trùng lặp với thẻ Visa cùng ngày',
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
      alertReason: 'Khoản trừ trùng lặp với Ví MoMo',
      isSubscription: true,
      maskedCard: '8829',
    },
    {
      id: 'tx-4',
      source: 'bank',
      sourceName: 'Vietcombank',
      merchant: 'EVN TP.HCM',
      description: 'Hóa đơn tiền điện sinh hoạt',
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
      alertReason: 'Phí thường niên định kỳ',
      maskedCard: '8829',
    },
  ]

  const filtered = transactions.filter((t) => {
    if (activeSource !== 'all' && t.source !== activeSource) return false
    return true
  })

  return (
    <div className="space-y-6">
      {/* ── Asymmetric Bento Grid (Tier 1) ── */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
        {/* Cell 1: Cashflow Visualizer (Span 7) */}
        <div className="md:col-span-7 bg-white rounded-2xl p-6 border border-neutral-200 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">
                  Dòng tiền tổng hợp
                </p>
                <p className="text-3xl font-bold text-neutral-900 mt-1">
                  +17.150.000₫
                </p>
              </div>
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-success-light text-success border border-success/20">
                Tiết kiệm 53.6%
              </span>
            </div>

            {/* Visual Cashflow Bar */}
            <div className="space-y-2 mt-6">
              <div className="flex justify-between text-xs text-neutral-600">
                <span>Thu: <strong className="text-success">+32.000.000₫</strong></span>
                <span>Chi: <strong className="text-neutral-900">-14.850.000₫</strong></span>
              </div>
              <div className="h-3 bg-neutral-100 rounded-full overflow-hidden flex">
                <div className="bg-success h-full" style={{ width: '68%' }} />
                <div className="bg-primary h-full" style={{ width: '32%' }} />
              </div>
            </div>
          </div>

          <div className="pt-4 mt-6 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-500">
            <span>Đối chiếu 3 nguồn: Vietcombank, MoMo, Visa</span>
            <button
              type="button"
              onClick={onAIChatOpen}
              className="text-primary font-semibold hover:underline"
            >
              Xem phân tích AI →
            </button>
          </div>
        </div>

        {/* Cell 2: Spotlight Anomaly Card (Span 5) */}
        <div className="md:col-span-5 bg-amber-50/90 rounded-2xl p-6 border border-amber-200 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-warning text-white">
                Cảnh báo trùng lặp
              </span>
              <span className="text-xs font-semibold text-danger">Còn 54 ngày</span>
            </div>
            <h3 className="text-base font-bold text-amber-950 mt-2 leading-snug">
              Netflix 260.000₫ trừ 2 lần
            </h3>
            <p className="text-xs text-amber-900/90 mt-1 leading-relaxed">
              Trừ đồng thời trên MoMo (02:15) và Techcombank Visa (02:16 ngày 15/02).
            </p>
          </div>

          <div className="pt-4 mt-4 border-t border-amber-200/80 flex items-center justify-between gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onAIChatOpen}
              className="text-xs bg-white text-neutral-800 border-amber-300"
            >
              Hỏi AI
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
              Tạo đơn tra soát
            </Button>
          </div>
        </div>
      </div>

      {/* ── Bento Tier 2: 3-Source Statement Triage Deck ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl p-5 border border-neutral-200 shadow-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase text-neutral-500">Ngân hàng</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-success-light text-success">
              42 giao dịch
            </span>
          </div>
          <p className="font-bold text-base text-neutral-900">Vietcombank</p>
          <p className="text-xs text-neutral-500 mt-1">Sao kê định kỳ T02/2026 (.csv)</p>
          <div className="pt-3 mt-3 border-t border-neutral-100 text-xs text-neutral-400">
            Cập nhật: 15/02/2026
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-neutral-200 shadow-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase text-neutral-500">Ví điện tử</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-50 text-purple-700">
              28 giao dịch
            </span>
          </div>
          <p className="font-bold text-base text-neutral-900">Ví MoMo</p>
          <p className="text-xs text-neutral-500 mt-1">Lịch sử thanh toán (.pdf)</p>
          <div className="pt-3 mt-3 border-t border-neutral-100 text-xs text-neutral-400">
            Cập nhật: 15/02/2026
          </div>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-neutral-200 shadow-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase text-neutral-500">Thẻ tín dụng</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-rose-50 text-rose-700">
              19 giao dịch
            </span>
          </div>
          <p className="font-bold text-base text-neutral-900">Techcombank Visa</p>
          <p className="text-xs text-neutral-500 mt-1">Sao kê thẻ **** 8829 (.pdf)</p>
          <div className="pt-3 mt-3 border-t border-neutral-100 text-xs text-neutral-400">
            Cập nhật: 15/02/2026
          </div>
        </div>
      </div>

      {/* ── Bento Tier 3: Transaction List with Source Tabs ── */}
      <div className="bg-white rounded-2xl p-6 border border-neutral-200 shadow-card">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5 pb-4 border-b border-neutral-100">
          <div>
            <h3 className="text-base font-bold text-neutral-900">Lịch sử đối chiếu</h3>
            <p className="text-xs text-neutral-500">Xem toàn bộ giao dịch từ 3 nguồn sao kê</p>
          </div>

          <div className="flex items-center gap-1.5 p-1 bg-neutral-100 rounded-xl text-xs font-semibold">
            <button
              type="button"
              onClick={() => setActiveSource('all')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeSource === 'all' ? 'bg-white text-neutral-900 shadow-xs' : 'text-neutral-600'
              }`}
            >
              Tất cả
            </button>
            <button
              type="button"
              onClick={() => setActiveSource('bank')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeSource === 'bank' ? 'bg-white text-neutral-900 shadow-xs' : 'text-neutral-600'
              }`}
            >
              Ngân hàng
            </button>
            <button
              type="button"
              onClick={() => setActiveSource('wallet')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeSource === 'wallet' ? 'bg-white text-neutral-900 shadow-xs' : 'text-neutral-600'
              }`}
            >
              Ví MoMo
            </button>
            <button
              type="button"
              onClick={() => setActiveSource('card')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeSource === 'card' ? 'bg-white text-neutral-900 shadow-xs' : 'text-neutral-600'
              }`}
            >
              Thẻ Visa
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {filtered.map((tx) => (
            <div
              key={tx.id}
              className="p-4 rounded-xl border border-neutral-100 hover:border-neutral-200 bg-neutral-50/50 hover:bg-white transition-all flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-white border border-neutral-200 text-neutral-700">
                  {tx.sourceName}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-neutral-900">{tx.merchant}</p>
                    {tx.isFlagged && (
                      <span className="text-xs px-2 py-0.2 rounded bg-warning-light text-[#B45309] font-bold">
                        Cảnh báo
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-neutral-500">{tx.description}</p>
                </div>
              </div>

              <div className="text-right">
                <p className={`text-base font-bold ${tx.amount > 0 ? 'text-success' : 'text-neutral-900'}`}>
                  {tx.amount > 0 ? `+${tx.amount.toLocaleString('vi-VN')}₫` : `${tx.amount.toLocaleString('vi-VN')}₫`}
                </p>
                <p className="text-xs text-neutral-400">{tx.date}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
