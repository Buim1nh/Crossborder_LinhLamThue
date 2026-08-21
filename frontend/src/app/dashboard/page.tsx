'use client'

import React, { useState } from 'react'
import {
  DashboardHeader,
  AIChatPanel,
  DisputeModal,
  VariantSwitcher,
  VariantLinear,
  VariantBento,
  VariantTerminal,
  DashboardVariantId,
  AnomalyItem,
} from '@/components/dashboard'

export default function DashboardPage() {
  const [currentVariant, setCurrentVariant] = useState<DashboardVariantId>('linear')
  const [isAIChatOpen, setIsAIChatOpen] = useState(false)
  const [activeAnomaly, setActiveAnomaly] = useState<AnomalyItem | null>(null)
  const [isDisputeModalOpen, setIsDisputeModalOpen] = useState(false)

  const handleDisputeClick = (anomaly: AnomalyItem) => {
    setActiveAnomaly(anomaly)
    setIsDisputeModalOpen(true)
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col font-sans">
      {/* ── Global Shell Header ── */}
      <DashboardHeader
        onUploadClick={() => {
          alert('Tính năng tải sao kê đang sẵn sàng trên cả 3 giao diện.')
        }}
        onExportClick={() => {
          alert('Tính năng xuất báo cáo PDF tài chính chuẩn CFO đang khởi tạo...')
        }}
        onAIChatClick={() => setIsAIChatOpen(!isAIChatOpen)}
        isChatOpen={isAIChatOpen}
        notificationCount={2}
      />

      {/* ── Main Workspace ── */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Interactive 3-Variant Switcher Bar */}
        <VariantSwitcher
          currentVariant={currentVariant}
          onSelectVariant={setCurrentVariant}
        />

        {/* ── Render Active Variant ── */}
        {currentVariant === 'linear' && (
          <VariantLinear
            onDisputeClick={handleDisputeClick}
            onAIChatOpen={() => setIsAIChatOpen(true)}
          />
        )}

        {currentVariant === 'bento' && (
          <VariantBento
            onDisputeClick={handleDisputeClick}
            onAIChatOpen={() => setIsAIChatOpen(true)}
          />
        )}

        {currentVariant === 'terminal' && (
          <VariantTerminal
            onDisputeClick={handleDisputeClick}
            onAIChatOpen={() => setIsAIChatOpen(true)}
          />
        )}
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
