'use client'

import React, { useState } from 'react'
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

export default function DashboardPage() {
  const [files, setFiles] = useState<Partial<Record<UploadSource, UploadedFileInfo>>>({
    bank: {
      name: 'Vietcombank_SaoKe_T022026.csv',
      size: '248 KB',
      transactionCount: 42,
      uploadedAt: '15/02/2026',
    },
    wallet: {
      name: 'MoMo_Statement_Feb2026.pdf',
      size: '1.2 MB',
      transactionCount: 28,
      uploadedAt: '15/02/2026',
    },
    card: {
      name: 'Techcombank_Visa_Feb2026.pdf',
      size: '850 KB',
      transactionCount: 19,
      uploadedAt: '15/02/2026',
    },
  })

  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isAIChatOpen, setIsAIChatOpen] = useState(false)
  const [activeAnomaly, setActiveAnomaly] = useState<AnomalyItem | null>(null)
  const [isDisputeModalOpen, setIsDisputeModalOpen] = useState(false)

  const handleUpload = (source: UploadSource, file: File) => {
    const formattedSize =
      file.size > 1024 * 1024
        ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
        : `${Math.round(file.size / 1024)} KB`

    setFiles((prev) => ({
      ...prev,
      [source]: {
        name: file.name,
        size: formattedSize,
        transactionCount: Math.floor(Math.random() * 20) + 15,
        uploadedAt: new Date().toLocaleDateString('vi-VN'),
      },
    }))
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
    }, 1200)
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
        title: tx.description,
        description: tx.alertReason || 'Giao dịch được đánh dấu cần kiểm tra.',
        amount: `${tx.amount.toLocaleString('vi-VN')}₫`,
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
        notificationCount={2}
      />

      {/* ── Main Linear Workspace ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-10 space-y-8">
        {/* 1. Linear Metrics Ribbon (4-Column Divided Ribbon) */}
        <LinearMetricsRibbon
          onAnomaliesClick={() => {
            const el = document.getElementById('ledger-section')
            el?.scrollIntoView({ behavior: 'smooth' })
          }}
          onSubscriptionsClick={() => {
            setIsAIChatOpen(true)
          }}
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
          <LinearTransactionLedger onTransactionClick={handleTransactionClick} />
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
