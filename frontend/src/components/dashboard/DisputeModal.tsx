'use client'

import React, { useState } from 'react'
import { AuthModal } from '@/components/auth/AuthModal'
import { Button } from '@/components/common/Button'
import { AnomalyItem } from './AnomalyAlertBanner'

export interface DisputeModalProps {
  isOpen: boolean
  onClose: () => void
  anomaly?: AnomalyItem | null
}

export function DisputeModal({ isOpen, onClose, anomaly }: DisputeModalProps) {
  const [copied, setCopied] = useState(false)

  if (!anomaly) return null

  const disputeText = `CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc

GIẤY ĐỀ NGHỊ TRA SOÁT / KHIẾU NẠI GIAO DỊCH THẺ & VÍ

Kính gửi: Trung tâm Dịch vụ Khách hàng Ngân hàng / Tổ chức phát hành thẻ
Tôi tên là: Nguyễn Văn A
Số điện thoại: 0988 776 655
Số tài khoản / Thẻ ghi nợ: **** **** **** 8829

NỘI DUNG YÊU CẦU TRA SOÁT:
- Ngày giao dịch: ${anomaly.date}
- Đơn vị thụ hưởng: Netflix Vietnam
- Số tiền giao dịch: ${anomaly.amount}
- Lý do tra soát: Giao dịch bị trừ tiền trùng lặp 2 lần (xuất hiện đồng thời trên Ví MoMo và Thẻ Visa).

Căn cứ theo quy định thời hạn tra soát 60 ngày, tôi đề nghị Quý Ngân hàng tiến hành hoàn trả khoản tiền trừ sai quy định vào tài khoản thanh toán của tôi trong thời gian sớm nhất.

Trân trọng cảm ơn!`

  const handleCopy = () => {
    navigator.clipboard.writeText(disputeText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <AuthModal
      isOpen={isOpen}
      onClose={onClose}
      title="MẪU ĐƠN TRA SOÁT NGÂN HÀNG"
      maxWidthClass="max-w-lg"
      icon={
        <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      }
      footer={
        <div className="flex gap-3 justify-end">
          <Button variant="outline" size="sm" onClick={onClose}>
            Đóng
          </Button>
          <Button variant="primary" size="sm" onClick={handleCopy} className="font-bold">
            {copied ? '✓ Đã sao chép vào bộ nhớ tạm' : 'Sao chép văn bản tra soát'}
          </Button>
        </div>
      }
    >
      <div className="space-y-4 py-2">
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-[#92400E]">
          <p className="font-bold mb-1">Thời hạn gửi khiếu nại quy định: 60 ngày</p>
          <p>
            Mẫu đơn này đã được AI trích xuất thông tin đối chiếu giữa các nguồn sao kê và định dạng chuẩn văn bản khiếu nại của các ngân hàng thương mại Việt Nam.
          </p>
        </div>

        <div className="relative">
          <pre className="p-4 rounded-xl bg-neutral-900 text-neutral-200 text-[11px] font-mono whitespace-pre-wrap leading-relaxed overflow-y-auto max-h-[260px] border border-neutral-800">
            {disputeText}
          </pre>
        </div>
      </div>
    </AuthModal>
  )
}
