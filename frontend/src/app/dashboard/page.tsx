'use client'

import React, { useState } from 'react'
import {
  DashboardHeader,
  UploadDropzones,
  SummaryMetrics,
  AnomalyAlertBanner,
  TransactionFeed,
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
  const [activeAnomaly, setActiveAnomaly] = useState<AnomalyItem | null>(null)
  const [isDisputeModalOpen, setIsDisputeModalOpen] = useState(false)
  const [chatInitialPrompt, setChatInitialPrompt] = useState<string | undefined>(undefined)

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
    }, 1500)
  }

  const handleDisputeClick = (anomaly: AnomalyItem) => {
    setActiveAnomaly(anomaly)
    setIsDisputeModalOpen(true)
  }

  const handleAskAIClick = (anomaly: AnomalyItem) => {
    setChatInitialPrompt(`Phân tích giúp tôi giao dịch bất thường ${anomaly.title}`)
  }

  const handleTransactionClick = (tx: DashboardTransaction) => {
    if (tx.isFlagged) {
      setActiveAnomaly({
        id: String(tx.id),
        title: tx.description,
        description: tx.alertReason || 'Giao dịch được hệ thống đánh dấu cần kiểm tra.',
        amount: `${tx.amount.toLocaleString('vi-VN')}₫`,
        sources: [tx.sourceName],
        severity: 'high',
        date: tx.date,
        disputeDeadlineDays: 54,
      })
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col font-sans">
      {/* ── Dashboard Shell Header ── */}
      <DashboardHeader
        onUploadClick={() => {
          const uploadEl = document.getElementById('upload-section')
          uploadEl?.scrollIntoView({ behavior: 'smooth' })
        }}
        onExportClick={() => {
          alert('Chức năng xuất báo cáo PDF tài chính chuẩn CFO đang khởi tạo...')
        }}
        notificationCount={2}
      />

      {/* ── Main Dashboard Workspace ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* 1. Proactive Anomaly Guardian Alert */}
        <AnomalyAlertBanner
          onDisputeClick={handleDisputeClick}
          onAskAIClick={handleAskAIClick}
        />

        {/* 2. Key Analytical Summary Cards */}
        <SummaryMetrics
          onAnomaliesClick={() => {
            const tableEl = document.getElementById('transactions-section')
            tableEl?.scrollIntoView({ behavior: 'smooth' })
          }}
          onSubscriptionsClick={() => {
            setChatInitialPrompt('Gợi ý hủy các gói subscription không sử dụng')
          }}
        />

        {/* 3. Multi-Source Statement Upload Zones */}
        <section id="upload-section">
          <UploadDropzones
            files={files}
            onUpload={handleUpload}
            onRemove={handleRemove}
            onAnalyze={handleAnalyze}
            isAnalyzing={isAnalyzing}
          />
        </section>

        {/* 4. Core Split-Layout: Transaction Feed (Left) & AI Guardian Chat (Right) */}
        <div id="transactions-section" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Transaction Feed & Multi-source Filters (7 cols on lg, 8 cols on xl) */}
          <div className="lg:col-span-7 xl:col-span-8 space-y-6">
            <TransactionFeed onTransactionClick={handleTransactionClick} />
          </div>

          {/* Right Column: AI Financial Guardian Assistant (5 cols on lg, 4 cols on xl) */}
          <div className="lg:col-span-5 xl:col-span-4 sticky top-24">
            <AIChatPanel
              key={chatInitialPrompt}
              onSendMessage={(text) => console.log('AI Query:', text)}
            />
          </div>
        </div>
      </main>

      {/* ── Dispute Modal Dialog ── */}
      <DisputeModal
        isOpen={isDisputeModalOpen}
        onClose={() => setIsDisputeModalOpen(false)}
        anomaly={activeAnomaly}
      />
    </div>
  )
}
