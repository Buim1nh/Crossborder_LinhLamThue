'use client'

import React, { useState } from 'react'
import { Button } from '@/components/common/Button'
import { UploadSource, UploadedFileInfo } from './UploadDropzones'

export interface LinearStatementBarProps {
  files: Partial<Record<UploadSource, UploadedFileInfo>>
  onUpload: (source: UploadSource, file: File) => void
  onRemove: (source: UploadSource) => void
  onAnalyze: () => void
  isAnalyzing?: boolean
  className?: string
}

interface SourceCardProps {
  source: UploadSource
  title: string
  providerLabel: string
  formats: string
  file?: UploadedFileInfo
  onFileSelect: (file: File) => void
  onRemove: () => void
}

function SourceCard({
  source,
  title,
  providerLabel,
  formats,
  file,
  onFileSelect,
  onRemove,
}: SourceCardProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const inputId = `linear-upload-${source}`

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setIsDragOver(true)
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setIsDragOver(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
          onFileSelect(e.dataTransfer.files[0])
        }
      }}
      className={`rounded-xl p-5 border transition-all flex flex-col justify-between ${
        file
          ? 'bg-white border-neutral-200 shadow-xs'
          : isDragOver
          ? 'bg-primary-light/40 border-primary border-dashed shadow-xs'
          : 'bg-neutral-50/70 border-dashed border-neutral-300 hover:border-neutral-400 hover:bg-white'
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
          <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
            {title}
          </span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-neutral-100 text-neutral-700 border border-neutral-200">
            {providerLabel}
          </span>
        </div>

        {file ? (
          <div className="space-y-1.5 py-1">
            <div className="flex items-center justify-between">
              <p className="text-sm sm:text-base font-bold text-neutral-900 truncate max-w-[210px]" title={file.name}>
                {file.name}
              </p>
              <button
                type="button"
                onClick={onRemove}
                className="text-xs text-neutral-400 hover:text-danger p-1 transition-colors font-medium"
                aria-label="Xóa file"
              >
                Xóa
              </button>
            </div>
            <p className="text-xs sm:text-sm text-neutral-500">
              {file.transactionCount ? `${file.transactionCount} giao dịch đã nạp` : file.size}
            </p>
          </div>
        ) : (
          <label htmlFor={inputId} className="cursor-pointer block py-3 text-center group">
            <p className="text-sm font-semibold text-neutral-800 group-hover:text-primary transition-colors">
              + Tải file lên <span className="text-xs text-neutral-500 font-normal">({formats})</span>
            </p>
          </label>
        )}
      </div>

      <div className="pt-3 mt-4 border-t border-neutral-100 flex items-center justify-between text-xs text-neutral-500 font-medium">
        <span>{file ? 'Trạng thái: Đã sẵn sàng' : 'Chưa có file'}</span>
        {file && (
          <label htmlFor={inputId} className="text-primary hover:underline cursor-pointer font-semibold">
            Thay đổi file
          </label>
        )}
      </div>
    </div>
  )
}

export function LinearStatementBar({
  files,
  onUpload,
  onRemove,
  onAnalyze,
  isAnalyzing = false,
  className = '',
}: LinearStatementBarProps) {
  const uploadedCount = Object.keys(files).length

  return (
    <div className={`bg-white rounded-2xl p-6 sm:p-7 border border-neutral-200 shadow-card ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold text-neutral-900 leading-tight">
            Quản Lý 3 Nguồn Dữ Liệu Sao Kê
          </h2>
          <p className="text-xs sm:text-sm text-neutral-500 mt-1">
            Hệ thống AI tự động đọc và chuẩn hóa dữ liệu cục bộ từ 3 tài khoản.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          disabled={uploadedCount === 0 || isAnalyzing}
          onClick={onAnalyze}
          className="shrink-0 font-bold shadow-xs min-h-[46px] px-6 text-sm"
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <SourceCard
          source="bank"
          title="Tài khoản ngân hàng"
          providerLabel="Vietcombank / Techcom..."
          formats=".CSV, .PDF"
          file={files.bank}
          onFileSelect={(f) => onUpload('bank', f)}
          onRemove={() => onRemove('bank')}
        />

        <SourceCard
          source="wallet"
          title="Ví điện tử"
          providerLabel="MoMo / ZaloPay..."
          formats=".PDF, .PNG"
          file={files.wallet}
          onFileSelect={(f) => onUpload('wallet', f)}
          onRemove={() => onRemove('wallet')}
        />

        <SourceCard
          source="card"
          title="Thẻ tín dụng / Ghi nợ"
          providerLabel="Visa / Mastercard..."
          formats=".PDF, .CSV"
          file={files.card}
          onFileSelect={(f) => onUpload('card', f)}
          onRemove={() => onRemove('card')}
        />
      </div>
    </div>
  )
}
