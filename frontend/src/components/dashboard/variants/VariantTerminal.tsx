'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'

export interface VariantTerminalProps {
  onDisputeClick?: (anomaly: any) => void
  onAIChatOpen?: () => void
}

export function VariantTerminal({ onDisputeClick, onAIChatOpen }: VariantTerminalProps) {
  const [selectedRow, setSelectedRow] = useState<string>('tx-2')
  const [filterSource, setFilterSource] = useState<string>('ALL')

  const auditMatrix = [
    { source: 'VIETCOMBANK', txs: 42, volume: '+32.000.000₫', fee: '0₫', status: 'SYNCHRONIZED' },
    { source: 'VÍ MOMO', txs: 28, volume: '-2.450.000₫', fee: '0₫', status: '1 ANOMALY' },
    { source: 'TECHCOMBANK VISA', txs: 19, volume: '-12.400.000₫', fee: '-350.000₫', status: '2 ANOMALIES' },
  ]

  const records = [
    {
      id: 'tx-1',
      date: '2026-02-15 09:30',
      source: 'BANK:VCB',
      ref: 'VCB-984210',
      merchant: 'ABC TECH CORP',
      category: 'INCOME',
      amount: '+32.000.000',
      flag: 'VERIFIED',
    },
    {
      id: 'tx-2',
      date: '2026-02-15 02:15',
      source: 'WALLET:MOMO',
      ref: 'MM-29104',
      merchant: 'NETFLIX VIETNAM',
      category: 'ENTERTAINMENT',
      amount: '-260.000',
      flag: 'DUPLICATE',
      note: 'Cross-match collision with VISA:TCB at 02:16',
    },
    {
      id: 'tx-3',
      date: '2026-02-15 02:16',
      source: 'CARD:TCB_8829',
      ref: 'VISA-88291',
      merchant: 'NETFLIX.COM',
      category: 'ENTERTAINMENT',
      amount: '-260.000',
      flag: 'DUPLICATE',
      note: 'Cross-match collision with WALLET:MOMO at 02:15',
    },
    {
      id: 'tx-4',
      date: '2026-02-14 14:20',
      source: 'BANK:VCB',
      ref: 'VCB-983100',
      merchant: 'EVN HCMC ELECTRICITY',
      category: 'UTILITIES',
      amount: '-1.450.000',
      flag: 'VERIFIED',
    },
    {
      id: 'tx-5',
      date: '2026-02-14 12:05',
      source: 'WALLET:MOMO',
      ref: 'MM-29001',
      merchant: 'GRABFOOD VIETNAM',
      category: 'DINING',
      amount: '-125.000',
      flag: 'VERIFIED',
    },
    {
      id: 'tx-6',
      date: '2026-02-10 08:00',
      source: 'CARD:TCB_8829',
      ref: 'VISA-FEE01',
      merchant: 'TECHCOMBANK ANNUAL FEE',
      category: 'FEES',
      amount: '-350.000',
      flag: 'HIDDEN_FEE',
      note: 'Annual recurring fee. Eligible for waiver request.',
    },
  ]

  const activeRecord = records.find((r) => r.id === selectedRow) || records[1]

  return (
    <div className="space-y-5 font-mono">
      {/* ── Terminal Command Bar & Status Ribbon ── */}
      <div className="bg-neutral-900 text-white rounded-xl p-4 border border-neutral-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-success animate-pulse" />
          <span className="text-xs font-bold tracking-widest text-neutral-300">
            TERMINAL // WEALIFY FINANCIAL AUDIT ENGINE 0.1.0
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <span>NET CASHFLOW: <strong className="text-success font-bold">+17.150.000 VND</strong></span>
          <span className="text-neutral-600">|</span>
          <span>ANOMALIES: <strong className="text-warning font-bold">3 DETECTED</strong></span>
          <Button
            variant="outline"
            size="sm"
            onClick={onAIChatOpen}
            className="text-xs bg-neutral-800 text-neutral-200 border-neutral-700 hover:text-white"
          >
            AI ANALYST [Ctrl+K]
          </Button>
        </div>
      </div>

      {/* ── Reconciliation Matrix (3 Sources) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {auditMatrix.map((item) => (
          <div key={item.source} className="bg-white rounded-xl p-4 border border-neutral-200 shadow-xs">
            <div className="flex items-center justify-between text-xs text-neutral-500 mb-2">
              <span>{item.source}</span>
              <span className={`font-bold ${item.status.includes('ANOMALY') ? 'text-warning' : 'text-success'}`}>
                [{item.status}]
              </span>
            </div>
            <p className="text-xl font-bold text-neutral-900">{item.volume}</p>
            <div className="flex justify-between text-xs text-neutral-500 mt-3 pt-2 border-t border-neutral-100">
              <span>TX COUNT: {item.txs}</span>
              <span>FEES: {item.fee}</span>
            </div>
          </div>
        ))}
      </div>

      {/* ── Split Terminal Pane: Raw Ledger Table + Inspection Inspector ── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Dense Ledger Table (Span 8) */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-neutral-200 shadow-xs overflow-hidden">
          <div className="p-3 bg-neutral-50 border-b border-neutral-200 flex items-center justify-between text-xs">
            <span className="font-bold text-neutral-700">TRANSACTION AUDIT LEDGER (8 ENTRIES)</span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setFilterSource('ALL')}
                className={`px-2 py-0.5 rounded ${filterSource === 'ALL' ? 'bg-neutral-900 text-white' : 'text-neutral-600'}`}
              >
                ALL
              </button>
              <button
                type="button"
                onClick={() => setFilterSource('FLAG')}
                className={`px-2 py-0.5 rounded ${filterSource === 'FLAG' ? 'bg-warning text-white' : 'text-neutral-600'}`}
              >
                FLAGGED ONLY
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-neutral-100/70 border-b border-neutral-200 text-neutral-500 font-bold">
                <tr>
                  <th className="p-3">SOURCE</th>
                  <th className="p-3">MERCHANT / DESCRIPTION</th>
                  <th className="p-3">CATEGORY</th>
                  <th className="p-3">FLAG</th>
                  <th className="p-3 text-right">AMOUNT (VND)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {records
                  .filter((r) => filterSource === 'ALL' || r.flag !== 'VERIFIED')
                  .map((r) => (
                    <tr
                      key={r.id}
                      onClick={() => setSelectedRow(r.id)}
                      className={`hover:bg-neutral-50 cursor-pointer transition-colors ${
                        selectedRow === r.id ? 'bg-primary-light/50 font-semibold text-neutral-950' : ''
                      }`}
                    >
                      <td className="p-3 font-semibold text-neutral-800">{r.source}</td>
                      <td className="p-3">
                        <p className="font-bold text-neutral-900">{r.merchant}</p>
                        <p className="text-xs text-neutral-500">{r.ref} • {r.date}</p>
                      </td>
                      <td className="p-3 text-neutral-600">{r.category}</td>
                      <td className="p-3">
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-bold ${
                            r.flag === 'DUPLICATE'
                              ? 'bg-warning-light text-[#B45309]'
                              : r.flag === 'HIDDEN_FEE'
                              ? 'bg-rose-100 text-danger'
                              : 'bg-neutral-100 text-neutral-600'
                          }`}
                        >
                          {r.flag}
                        </span>
                      </td>
                      <td
                        className={`p-3 text-right font-bold ${
                          r.amount.startsWith('+') ? 'text-success' : 'text-neutral-900'
                        }`}
                      >
                        {r.amount}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Inspection Inspector Panel (Span 4) */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-neutral-200 shadow-xs p-5 space-y-4">
          <div className="pb-3 border-b border-neutral-100 flex items-center justify-between">
            <span className="text-xs font-bold text-neutral-500 uppercase">INSPECTOR</span>
            <span className="text-xs font-mono font-bold text-neutral-800">{activeRecord.ref}</span>
          </div>

          <div>
            <p className="text-lg font-bold text-neutral-900">{activeRecord.merchant}</p>
            <p className="text-2xl font-bold text-primary mt-1">{activeRecord.amount} VND</p>
          </div>

          <div className="space-y-2 text-xs text-neutral-600 bg-neutral-50 p-3 rounded-lg border border-neutral-200">
            <p><strong>Source:</strong> {activeRecord.source}</p>
            <p><strong>Timestamp:</strong> {activeRecord.date}</p>
            <p><strong>Category:</strong> {activeRecord.category}</p>
            {activeRecord.note && (
              <p className="text-danger pt-1 border-t border-neutral-200 mt-2">
                <strong>ALERT NOTE:</strong> {activeRecord.note}
              </p>
            )}
          </div>

          {activeRecord.flag === 'DUPLICATE' && (
            <Button
              variant="primary"
              size="md"
              onClick={() =>
                onDisputeClick?.({
                  id: activeRecord.id,
                  title: activeRecord.merchant,
                  description: activeRecord.note || 'Duplicate transaction collision',
                  amount: `${activeRecord.amount}₫`,
                  date: activeRecord.date,
                })
              }
              className="w-full justify-center text-xs font-bold"
            >
              GENERATE DISPUTE FILING →
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
