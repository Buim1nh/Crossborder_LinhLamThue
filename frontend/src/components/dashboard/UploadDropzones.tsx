'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'

export type UploadSource = 'bank' | 'wallet' | 'card'

export interface UploadedFileInfo {
  name: string
  size: string
  transactionCount?: number
  uploadedAt: string
}

export interface UploadDropzonesProps {
  files: Partial<Record<UploadSource, UploadedFileInfo>>
  onUpload: (source: UploadSource, file: File) => void
  onRemove: (source: UploadSource) => void
  onAnalyze: () => void
  isAnalyzing?: boolean
  className?: string
}

interface DropzoneCardProps {
  source: UploadSource
  title: string
  subtitle: string
  supportedFormats: string
  icon: React.ReactNode
  accentColor: string
  file?: UploadedFileInfo
  onFileSelect: (file: File) => void
  onRemove: () => void
}

function DropzoneCard({
  title,
  subtitle,
  supportedFormats,
  icon,
  file,
  onFileSelect,
  onRemove,
}: DropzoneCardProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0])
    }
  }

  const inputId = `file-upload-${title.toLowerCase().replace(/\s+/g, '-')}`

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative rounded-xl p-5 border-2 transition-all flex flex-col justify-between ${
        file
          ? 'bg-white border-solid border-success/40 shadow-sm'
          : isDragOver
          ? 'bg-primary-light/40 border-dashed border-primary shadow-md scale-[1.01]'
          : 'bg-white border-dashed border-neutral-300 hover:border-primary/70 hover:bg-neutral-50/50 shadow-card'
      }`}
    >
      <div>
        {/* Card Header & Icon */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-700 shrink-0">
              {icon}
            </div>
            <div>
              <h3 className="text-sm font-bold text-neutral-900 leading-tight">{title}</h3>
              <p className="text-[11px] text-neutral-500">{subtitle}</p>
            </div>
          </div>

          {file && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-success-light text-success text-[10px] font-bold">
              ✓ Đã tải
            </span>
          )}
        </div>

        {/* State: File already uploaded */}
        {file ? (
          <div className="p-3.5 rounded-lg bg-neutral-50 border border-neutral-200/80 mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-neutral-900 truncate max-w-[180px]">
                {file.name}
              </span>
              <button
                type="button"
                onClick={onRemove}
                className="text-neutral-400 hover:text-danger p-1 rounded transition-colors"
                aria-label="Xóa file"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex justify-between items-center text-[11px] text-neutral-500">
              <span>{file.size}</span>
              {file.transactionCount ? (
                <span className="font-semibold text-primary">{file.transactionCount} giao dịch</span>
              ) : null}
            </div>
          </div>
        ) : (
          /* State: Dropzone upload prompt */
          <div className="text-center py-4">
            <input
              id={inputId}
              type="file"
              onChange={handleInputChange}
              accept=".csv,.pdf,.png,.jpg,.jpeg,.xlsx"
              className="hidden"
            />
            <label
              htmlFor={inputId}
              className="cursor-pointer block group"
            >
              <div className="w-8 h-8 rounded-full bg-neutral-100 text-neutral-500 group-hover:bg-primary-light group-hover:text-primary flex items-center justify-center mx-auto mb-2 transition-colors">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <p className="text-xs font-semibold text-neutral-800 group-hover:text-primary transition-colors">
                Kéo thả file hoặc <span className="text-primary underline">chọn file</span>
              </p>
              <p className="text-[10px] text-neutral-400 mt-1">Định dạng: {supportedFormats}</p>
            </label>
          </div>
        )}
      </div>

      {/* Security micro badge */}
      <div className="pt-2.5 border-t border-neutral-100 flex items-center justify-between text-[10px] text-neutral-400">
        <span>Mã hóa AES-256</span>
        <span>Phân tích cục bộ</span>
      </div>
    </div>
  )
}

export function UploadDropzones({
  files,
  onUpload,
  onRemove,
  onAnalyze,
  isAnalyzing = false,
  className = '',
}: UploadDropzonesProps) {
  const uploadedCount = Object.keys(files).length

  return (
    <div className={`bg-white rounded-2xl p-6 shadow-card border border-neutral-200/80 ${className}`}>
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-neutral-900">
              Tải Lên Sao Kê 3 Nguồn
            </h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary-light text-primary">
              {uploadedCount}/3 Nguồn Đã Nạp
            </span>
          </div>
          <p className="text-xs text-neutral-500 mt-0.5">
            Hệ thống AI sẽ tự động đọc, đối chiếu chéo và phát hiện khoản trùng lặp giữa các nguồn.
          </p>
        </div>

        {/* Trigger AI Multi-Source Cross-Reference */}
        <Button
          variant="primary"
          size="md"
          disabled={uploadedCount === 0 || isAnalyzing}
          onClick={onAnalyze}
          className="shrink-0 flex items-center justify-center gap-2 font-bold shadow-[0_2px_8px_rgba(255,107,26,0.25)] min-h-[44px]"
        >
          {isAnalyzing ? (
            <>
              <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>AI Đang Phân Tích & Đối Chiếu...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Đối Chiếu AI Ngay ({uploadedCount} Nguồn)</span>
            </>
          )}
        </Button>
      </div>

      {/* 3 Upload Zones Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DropzoneCard
          source="bank"
          title="Tài Khoản Ngân Hàng"
          subtitle="Vietcombank, Techcombank, MB..."
          supportedFormats=".CSV, .PDF, .XLSX"
          accentColor="#16A34A"
          icon={
            <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
            </svg>
          }
          file={files.bank}
          onFileSelect={(file) => onUpload('bank', file)}
          onRemove={() => onRemove('bank')}
        />

        <DropzoneCard
          source="wallet"
          title="Ví Điện Tử"
          subtitle="MoMo, ZaloPay, ShopeePay..."
          supportedFormats=".PDF, .PNG, .JPG"
          accentColor="#A21CAF"
          icon={
            <svg className="w-5 h-5 text-[#A21CAF]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
          }
          file={files.wallet}
          onFileSelect={(file) => onUpload('wallet', file)}
          onRemove={() => onRemove('wallet')}
        />

        <DropzoneCard
          source="card"
          title="Thẻ Tín Dụng / Ghi Nợ"
          subtitle="Visa, Mastercard, JCB..."
          supportedFormats=".PDF, .CSV"
          accentColor="#DC2626"
          icon={
            <svg className="w-5 h-5 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          }
          file={files.card}
          onFileSelect={(file) => onUpload('card', file)}
          onRemove={() => onRemove('card')}
        />
      </div>
    </div>
  )
}
