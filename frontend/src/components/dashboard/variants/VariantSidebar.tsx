'use client'

import React, { useState } from 'react'
import {
  DashboardSidebar,
  DashboardNavTab,
} from '@/components/dashboard/DashboardSidebar'
import { SidebarTopHeader } from '@/components/dashboard/SidebarTopHeader'
import { SummaryMetrics } from '@/components/dashboard/SummaryMetrics'
import { UploadDropzones, UploadSource, UploadedFileInfo } from '@/components/dashboard/UploadDropzones'
import { AnomalyAlertBanner, AnomalyItem } from '@/components/dashboard/AnomalyAlertBanner'
import { TransactionFeed } from '@/components/dashboard/TransactionFeed'
import { AIChatPanel } from '@/components/dashboard/AIChatPanel'

export interface VariantSidebarProps {
  onDisputeClick?: (anomaly: AnomalyItem) => void
  onAIChatOpen?: () => void
}

export function VariantSidebar({ onDisputeClick, onAIChatOpen }: VariantSidebarProps) {
  const [activeTab, setActiveTab] = useState<DashboardNavTab>('overview')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [searchValue, setSearchValue] = useState('')

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

  const tabTitles: Record<DashboardNavTab, string> = {
    overview: 'Tổng Quan',
    statements: 'Nguồn Sao Kê (3 Nguồn)',
    transactions: 'Lịch Sử Giao Dịch',
    anomalies: 'Cảnh Báo Chi Tiêu & Tra Soát',
    subscriptions: 'Dịch Vụ Định Kỳ',
    assistant: 'Trợ Lý Tài Chính AI',
  }

  return (
    <div className="flex min-h-[calc(100vh-80px)] bg-neutral-50 rounded-2xl border border-neutral-200 overflow-hidden shadow-card">
      {/* ── Left Sidebar Navigation ── */}
      <DashboardSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        notificationCount={2}
        subscriptionCount={4}
      />

      {/* ── Main Content Area with Top Header ── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Sidebar Top Header */}
        <SidebarTopHeader
          title={tabTitles[activeTab]}
          breadcrumb="Không Gian Làm Việc"
          onUploadClick={() => setActiveTab('statements')}
          onExportClick={() => alert('Đang xuất báo cáo tài chính PDF...')}
          searchValue={searchValue}
          onSearchChange={setSearchValue}
          notificationCount={2}
        />

        {/* Dynamic Tab Body */}
        <div className="p-6 lg:p-8 space-y-6 overflow-y-auto flex-1">
          {/* TAB: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <AnomalyAlertBanner
                onDisputeClick={onDisputeClick}
                onAskAIClick={() => setActiveTab('assistant')}
              />

              <SummaryMetrics
                onAnomaliesClick={() => setActiveTab('anomalies')}
                onSubscriptionsClick={() => setActiveTab('subscriptions')}
              />

              <UploadDropzones
                files={files}
                onUpload={handleUpload}
                onRemove={handleRemove}
                onAnalyze={handleAnalyze}
                isAnalyzing={isAnalyzing}
              />

              <TransactionFeed
                onTransactionClick={(tx) => {
                  if (tx.isFlagged) {
                    onDisputeClick?.({
                      id: String(tx.id),
                      title: tx.description,
                      description: tx.alertReason || 'Cần kiểm tra',
                      amount: `${tx.amount.toLocaleString('vi-VN')}₫`,
                      sources: [tx.sourceName],
                      severity: 'high',
                      date: tx.date,
                      disputeDeadlineDays: 54,
                    })
                  }
                }}
              />
            </div>
          )}

          {/* TAB: STATEMENTS */}
          {activeTab === 'statements' && (
            <div className="space-y-6">
              <UploadDropzones
                files={files}
                onUpload={handleUpload}
                onRemove={handleRemove}
                onAnalyze={handleAnalyze}
                isAnalyzing={isAnalyzing}
              />
            </div>
          )}

          {/* TAB: TRANSACTIONS */}
          {activeTab === 'transactions' && (
            <div className="space-y-6">
              <TransactionFeed
                onTransactionClick={(tx) => {
                  if (tx.isFlagged) {
                    onDisputeClick?.({
                      id: String(tx.id),
                      title: tx.description,
                      description: tx.alertReason || 'Cần kiểm tra',
                      amount: `${tx.amount.toLocaleString('vi-VN')}₫`,
                      sources: [tx.sourceName],
                      severity: 'high',
                      date: tx.date,
                      disputeDeadlineDays: 54,
                    })
                  }
                }}
              />
            </div>
          )}

          {/* TAB: ANOMALIES & DISPUTES */}
          {activeTab === 'anomalies' && (
            <div className="space-y-6">
              <AnomalyAlertBanner
                onDisputeClick={onDisputeClick}
                onAskAIClick={() => setActiveTab('assistant')}
              />
              <TransactionFeed
                onTransactionClick={(tx) => {
                  onDisputeClick?.({
                    id: String(tx.id),
                    title: tx.merchant,
                    description: tx.alertReason || tx.description,
                    amount: `${tx.amount.toLocaleString('vi-VN')}₫`,
                    sources: [tx.sourceName],
                    severity: 'high',
                    date: tx.date,
                    disputeDeadlineDays: 54,
                  })
                }}
              />
            </div>
          )}

          {/* TAB: SUBSCRIPTIONS */}
          {activeTab === 'subscriptions' && (
            <div className="space-y-6">
              <SummaryMetrics
                onAnomaliesClick={() => setActiveTab('anomalies')}
                onSubscriptionsClick={() => setActiveTab('subscriptions')}
              />
              <TransactionFeed />
            </div>
          )}

          {/* TAB: AI ASSISTANT */}
          {activeTab === 'assistant' && (
            <div className="h-[640px] bg-white rounded-2xl border border-neutral-200 shadow-card overflow-hidden">
              <AIChatPanel isOpen={true} className="!fixed-none !h-full !w-full !border-0" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
