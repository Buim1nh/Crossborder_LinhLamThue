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

interface StreamCardProps {
  source: UploadSource
  title: string
  badgeLabel: string
  formats: string
  file?: UploadedFileInfo
  onFileSelect: (file: File) => void
  onRemove: () => void
}

function StreamCard({
  source,
  title,
  badgeLabel,
  formats,
  file,
  onFileSelect,
  onRemove,
}: StreamCardProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const inputId = `upload-stream-${source}`

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragOver(true)
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      className={`rounded-xl p-4 border transition-all flex flex-col justify-between ${
        file
          ? 'bg-white border-neutral-200 shadow-xs'
          : isDragOver
          ? 'bg-primary-light/50 border-primary border-dashed shadow-xs'
          : 'bg-neutral-50 border-dashed border-neutral-300 hover:border-neutral-400 hover:bg-white'
      }`}
    >
      <input
        id={inputId}
        type="file"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            onFileSelect(e.target.files[0])
          }
        }}
        accept=".csv,.pdf,.png,.jpg,.jpeg,.xlsx"
        className="hidden"
      />

      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-neutral-600">
            {title}
          </span>
          <span className="text-xs font-medium px-2 py-0.5 rounded bg-neutral-100 text-neutral-600 border border-neutral-200">
            {badgeLabel}
          </span>
        </div>

        {file ? (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-neutral-900 truncate max-w-[200px]" title={file.name}>
                {file.name}
              </p>
              <button
                type="button"
                onClick={onRemove}
                className="text-xs text-neutral-400 hover:text-danger p-1 transition-colors"
                aria-label="Xóa file này"
              >
                Xóa
              </button>
            </div>
            <p className="text-xs text-neutral-500">
              {file.transactionCount ? `${file.transactionCount} giao dịch` : file.size} • Đã sẵn sàng
            </p>
          </div>
        ) : (
          <label htmlFor={inputId} className="cursor-pointer block py-2 text-center group">
            <p className="text-sm font-medium text-neutral-700 group-hover:text-primary transition-colors">
              + Tải file lên <span className="text-xs text-neutral-400">({formats})</span>
            </p>
          </label>
        )}
      </div>

      <div className="pt-3 mt-3 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-500">
        <span>{file ? 'Trạng thái: Hoạt động' : 'Chưa nạp file'}</span>
        {file && (
          <label htmlFor={inputId} className="text-primary hover:underline cursor-pointer font-medium">
            Đổi file
          </label>
        )}
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
    <div className={`bg-white rounded-2xl p-6 border border-neutral-200 shadow-card ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-base font-bold text-neutral-900">
            Quản Lý 3 Nguồn Sao Kê
          </h2>
          <p className="text-xs text-neutral-500 mt-0.5">
            Hệ thống tự động đồng bộ và phân tích dữ liệu cục bộ giữa các nguồn.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          disabled={uploadedCount === 0 || isAnalyzing}
          onClick={onAnalyze}
          className="shrink-0 font-bold shadow-xs text-xs sm:text-sm"
        >
          {isAnalyzing ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Đang đối chiếu AI...
            </span>
          ) : (
            `Phân tích & đối chiếu chéo (${uploadedCount}/3 nguồn)`
          )}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StreamCard
          source="bank"
          title="Tài khoản ngân hàng"
          badgeLabel="Vietcombank / Techcom..."
          formats=".CSV, .PDF"
          file={files.bank}
          onFileSelect={(f) => onUpload('bank', f)}
          onRemove={() => onRemove('bank')}
        />

        <StreamCard
          source="wallet"
          title="Ví điện tử"
          badgeLabel="MoMo / ZaloPay..."
          formats=".PDF, .PNG"
          file={files.wallet}
          onFileSelect={(f) => onUpload('wallet', f)}
          onRemove={() => onRemove('wallet')}
        />

        <StreamCard
          source="card"
          title="Thẻ tín dụng / Ghi nợ"
          badgeLabel="Visa / Mastercard..."
          formats=".PDF, .CSV"
          file={files.card}
          onFileSelect={(f) => onUpload('card', f)}
          onRemove={() => onRemove('card')}
        />
      </div>
    </div>
  )
}
