'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  DashboardHeader,
  LinearMetricsRibbon,
  LinearAnomalyBanner,
  LinearStatementBar,
  LinearTransactionLedger,
  AIChatPanel,
  DisputeModal,
  UploadSource,
  UploadedFileInfo,
  AnomalyItem,
  DashboardTransaction,
} from '@/components/dashboard'
import {
  transactionsApi,
  uploadApi,
  SubscriptionModelInfo,
  TransactionSummary,
} from '@/lib/api'
import { type FinancialMetricsData } from '@/components/dashboard/LinearMetricsRibbon'

// ─── Helpers ────────────────────────────────────────────────────────────────

function txSummaryToDashboard(tx: TransactionSummary): DashboardTransaction {
  const [date, time] = (tx.transaction_date || '').split('T')
  return {
    id: tx.id,
    source: tx.source === 'account' ? 'bank' : (tx.source as 'bank' | 'wallet' | 'card'),
    sourceName: tx.source === 'account' ? 'Ngân hàng' : tx.source === 'wallet' ? 'Ví điện tử' : 'Thẻ tín dụng',
    merchant: tx.merchant_name || tx.description?.slice(0, 30) || '—',
    description: tx.description || '',
    category: tx.category || 'Khác',
    amount: tx.amount,
    date: date ? new Date(date).toLocaleDateString('vi-VN') : '—',
    time: time ? time.slice(0, 5) : undefined,
    isFlagged: tx.is_flagged,
    alertReason: tx.alert_reason || undefined,
    isSubscription: tx.is_subscription,
    maskedCard: tx.masked_card || undefined,
  }
}

function computeMetrics(
  txs: TransactionSummary[],
  modelInfo: SubscriptionModelInfo | null
): FinancialMetricsData {
  const income = txs.filter((t) => t.amount > 0).reduce((s, t) => s + t.amount, 0)
  const expense = Math.abs(txs.filter((t) => t.amount < 0).reduce((s, t) => s + t.amount, 0))
  const subscriptions = txs.filter((t) => t.is_subscription)
  const flagged = txs.filter((t) => t.is_flagged)

  return {
    totalIncome: `+${income.toLocaleString('vi-VN')}₫`,
    totalExpense: `-${expense.toLocaleString('vi-VN')}₫`,
    netSavings: `${income - expense >= 0 ? '+' : ''}${(income - expense).toLocaleString('vi-VN')}₫`,
    anomaliesCount: flagged.length,
    unresolvedAnomalies: flagged.length,
    subscriptionsCount: subscriptions.length,
    monthlySubscriptionBurn: subscriptions.length > 0
      ? `${Math.abs(subscriptions.reduce((s, t) => s + t.amount, 0)).toLocaleString('vi-VN')}₫`
      : '0₫',
    savingsOpportunity: modelInfo ? `ML v${modelInfo.version}` : 'Chưa kết nối',
  }
}

// ─── Page ─────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [files, setFiles] = useState<Partial<Record<UploadSource, UploadedFileInfo>>>({})
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isAIChatOpen, setIsAIChatOpen] = useState(false)
  const [activeAnomaly, setActiveAnomaly] = useState<AnomalyItem | null>(null)
  const [isDisputeModalOpen, setIsDisputeModalOpen] = useState(false)

  const [transactions, setTransactions] = useState<TransactionSummary[]>([])
  const [dashboardTxs, setDashboardTxs] = useState<DashboardTransaction[]>([])
  const [isLoadingTxs, setIsLoadingTxs] = useState(false)
  const [txError, setTxError] = useState<string | null>(null)

  const [metrics, setMetrics] = useState<FinancialMetricsData | null>(null)
  const [modelInfo, setModelInfo] = useState<SubscriptionModelInfo | null>(null)

  // ── Fetch transactions + model info on mount ──
  const fetchData = useCallback(async () => {
    setIsLoadingTxs(true)
    setTxError(null)
    try {
      const txResult = await transactionsApi.list({ limit: 200 })
      setTransactions(txResult.transactions)
      setDashboardTxs(txResult.transactions.map(txSummaryToDashboard))
      setMetrics(computeMetrics(txResult.transactions, modelInfo))
    } catch (err) {
      setTxError(err instanceof Error ? err.message : 'Lỗi tải dữ liệu')
    } finally {
      setIsLoadingTxs(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    fetchData()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Update metrics when model info arrives
  useEffect(() => {
    if (transactions.length > 0) {
      setMetrics(computeMetrics(transactions, modelInfo))
    }
  }, [modelInfo, transactions])

  // ── Upload handler ──
  const handleUpload = async (source: UploadSource, file: File) => {
    const formattedSize =
      file.size > 1024 * 1024
        ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
        : `${Math.round(file.size / 1024)} KB`

    setFiles((prev) => ({
      ...prev,
      [source]: {
        name: file.name,
        size: formattedSize,
        transactionCount: 0,
        uploadedAt: new Date().toLocaleDateString('vi-VN'),
      },
    }))

    setIsAnalyzing(true)
    try {
      const result = await uploadApi.uploadStatement(source, file)
      setFiles((prev) => ({
        ...prev,
        [source]: {
          name: file.name,
          size: formattedSize,
          transactionCount: result.total_parsed,
          uploadedAt: new Date().toLocaleDateString('vi-VN'),
        },
      }))
      // Refresh transactions
      await fetchData()
    } catch (err) {
      setFiles((prev) => {
        const updated = { ...prev }
        delete updated[source]
        return updated
      })
      alert(err instanceof Error ? err.message : 'Upload thất bại')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleRemove = (source: UploadSource) => {
    setFiles((prev) => {
      const updated = { ...prev }
      delete updated[source]
      return updated
    })
  }

  const handleAnalyze = () => {
    setIsAnalyzing(true)
    setTimeout(() => {
      setIsAnalyzing(false)
    }, 800)
  }

  const handleDisputeClick = (anomaly: AnomalyItem) => {
    setActiveAnomaly(anomaly)
    setIsDisputeModalOpen(true)
  }

  const handleAskAIClick = (_anomaly: AnomalyItem) => {
    setIsAIChatOpen(true)
  }

  const handleTransactionClick = (tx: DashboardTransaction) => {
    if (tx.isFlagged) {
      setActiveAnomaly({
        id: String(tx.id),
        title: tx.merchant,
        description: tx.alertReason || 'Giao dịch được đánh dấu cần kiểm tra.',
        amount: `${Math.abs(tx.amount).toLocaleString('vi-VN')}₫`,
        sources: [tx.sourceName],
        severity: 'high',
        date: tx.date,
        disputeDeadlineDays: 54,
      })
      setIsDisputeModalOpen(true)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col font-sans">
      {/* ── Dashboard Shell Header ── */}
      <DashboardHeader
        onUploadClick={() => {
          const el = document.getElementById('statements-section')
          el?.scrollIntoView({ behavior: 'smooth' })
        }}
        onExportClick={() => {
          alert('Tính năng xuất báo cáo PDF tài chính chuẩn CFO đang khởi tạo...')
        }}
        onAIChatClick={() => setIsAIChatOpen(!isAIChatOpen)}
        isChatOpen={isAIChatOpen}
        notificationCount={transactions.filter((t) => t.is_flagged).length}
      />

      {/* ── Main Linear Workspace ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10 space-y-8">
        {/* 1. Linear Metrics Ribbon */}
        <LinearMetricsRibbon
          data={metrics ?? undefined}
          onAnomaliesClick={() => {
            const el = document.getElementById('ledger-section')
            el?.scrollIntoView({ behavior: 'smooth' })
          }}
          onSubscriptionsClick={() => setIsAIChatOpen(true)}
        />

        {/* 2. Proactive Anomaly Alert Banner */}
        <LinearAnomalyBanner
          onDisputeClick={handleDisputeClick}
          onAskAIClick={handleAskAIClick}
        />

        {/* 3. 3-Source Statement Manager */}
        <section id="statements-section">
          <LinearStatementBar
            files={files}
            onUpload={handleUpload}
            onRemove={handleRemove}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
          />
        </section>

        {/* 4. Full-Width Transaction Ledger */}
        <section id="ledger-section">
          {isLoadingTxs ? (
            <div className="bg-white rounded-2xl border border-neutral-200 shadow-card p-20 flex items-center justify-center">
              <div className="flex flex-col items-center gap-3 text-neutral-500">
                <svg className="animate-spin w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <p className="text-sm font-medium">Đang tải giao dịch...</p>
              </div>
            </div>
          ) : txError ? (
            <div className="bg-white rounded-2xl border border-danger/30 shadow-card p-10 text-center">
              <p className="text-danger font-semibold">{txError}</p>
              <button
                onClick={fetchData}
                className="mt-3 text-sm text-primary hover:underline font-medium"
              >
                Thử lại
              </button>
            </div>
          ) : (
            <LinearTransactionLedger
              transactions={dashboardTxs}
              onTransactionClick={handleTransactionClick}
            />
          )}
        </section>
      </main>

      {/* ── Slide-Over AI Financial Guardian Assistant ── */}
      <AIChatPanel
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
      />

      {/* ── Backdrop for Mobile AI Chat ── */}
      {isAIChatOpen && (
        <div
          onClick={() => setIsAIChatOpen(false)}
          className="fixed inset-0 bg-neutral-900/30 backdrop-blur-xs z-30 sm:hidden animate-in fade-in duration-200"
        />
      )}

      {/* ── Dispute Modal Dialog ── */}
      <DisputeModal
        isOpen={isDisputeModalOpen}
        onClose={() => setIsDisputeModalOpen(false)}
        anomaly={activeAnomaly}
      />
    </div>
  )
}
