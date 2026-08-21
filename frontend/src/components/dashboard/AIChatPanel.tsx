'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/common/Button'

export interface ChatMessage {
  id: string
  role: 'assistant' | 'user'
  content: React.ReactNode
  timestamp: string
}

export interface AIChatPanelProps {
  initialMessages?: ChatMessage[]
  onSendMessage?: (text: string) => void
  isCollapsed?: boolean
  onToggleCollapse?: () => void
  className?: string
}

const DEFAULT_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'assistant',
    content: (
      <div className="space-y-2">
        <p>
          Chào bạn! Tôi là <strong>Wealify AI Guardian</strong> — trợ lý phân tích sao kê tài chính của bạn.
        </p>
        <p>
          Sau khi đối chiếu chéo giữa <strong>Vietcombank</strong>, <strong>Ví MoMo</strong> và <strong>Techcombank Visa</strong>, tôi phát hiện:
        </p>
        <ul className="list-disc pl-4 space-y-1 text-xs">
          <li><strong>1 khoản trùng lặp:</strong> Netflix 260.000₫ bị trừ trên cả Ví MoMo và thẻ Visa ngày 15/02.</li>
          <li><strong>1 khoản phí ẩn:</strong> Phí thường niên thẻ 350.000₫.</li>
          <li><strong>Tổng tiềm năng tối ưu:</strong> Tiết kiệm đến <strong>610.000₫ / tháng</strong>.</li>
        </ul>
        <p className="text-xs text-neutral-500">
          Bạn muốn tôi giải thích chi tiết khoản nào hoặc tạo mẫu tra soát ngân hàng?
        </p>
      </div>
    ),
    timestamp: '09:30',
  },
]

const QUICK_PROMPTS = [
  'Tóm tắt chi tiêu 3 nguồn tháng này',
  'Kiểm tra phí ngân hàng & phí ẩn',
  'Gợi ý hủy các gói subscription',
  'Tạo mẫu tra soát khoản Netflix',
]

export function AIChatPanel({
  initialMessages = DEFAULT_MESSAGES,
  onSendMessage,
  isCollapsed = false,
  onToggleCollapse,
  className = '',
}: AIChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSend = (textToSend?: string) => {
    const text = textToSend || inputValue
    if (!text.trim()) return

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setInputValue('')
    onSendMessage?.(text)

    // Simulate AI Analyst response
    setIsTyping(true)
    setTimeout(() => {
      let botResponseText: React.ReactNode = ''
      if (text.includes('Netflix') || text.includes('tra soát')) {
        botResponseText = (
          <div className="space-y-2">
            <p>
              Đối với khoản <strong>Netflix 260.000₫</strong> bị trừ 2 lần:
            </p>
            <p className="text-xs">
              1. Giao dịch 1: Ví MoMo lúc 02:15 AM (Mã: MM-9921)<br />
              2. Giao dịch 2: Techcombank Visa **** 8829 lúc 02:16 AM.
            </p>
            <p className="text-xs text-success font-semibold">
              ✓ Thời hạn tra soát ngân hàng còn 54 ngày. Bạn có thể nhấn nút "Tạo Mẫu Tra Soát" ở banner để gửi khiếu nại hoàn tiền ngay.
            </p>
          </div>
        )
      } else if (text.includes('subscription') || text.includes('định kỳ')) {
        botResponseText = (
          <div className="space-y-2">
            <p>
              Danh sách 4 dịch vụ định kỳ đang hoạt động:
            </p>
            <ul className="list-disc pl-4 space-y-1 text-xs">
              <li><strong>Netflix:</strong> 260.000₫ / tháng (MoMo & Visa)</li>
              <li><strong>Spotify:</strong> 59.000₫ / tháng (Visa)</li>
              <li><strong>ChatGPT Plus:</strong> 500.000₫ / tháng (MoMo)</li>
              <li><strong>Cloud Storage:</strong> 301.000₫ / tháng (Visa)</li>
            </ul>
            <p className="text-xs text-primary font-bold">
              Tổng tiêu hao: 1.120.000₫ / tháng.
            </p>
          </div>
        )
      } else {
        botResponseText = (
          <div className="space-y-1">
            <p>
              Dựa trên phân tích 3 nguồn sao kê, bạn đã tiết kiệm được <strong>17.150.000₫</strong> trong tháng này (tỷ lệ tiết kiệm 53.6%).
            </p>
            <p className="text-xs text-neutral-600">
              Chi tiêu lớn nhất thuộc về nhóm <strong>Hóa đơn tiện ích (1.450.000₫)</strong> và <strong>Dịch vụ trực tuyến (1.120.000₫)</strong>.
            </p>
          </div>
        )
      }

      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        content: botResponseText,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, botMsg])
      setIsTyping(false)
    }, 1000)
  }

  return (
    <div
      className={`bg-white rounded-2xl shadow-card border border-neutral-200/80 flex flex-col h-full overflow-hidden ${className}`}
    >
      {/* Panel Header */}
      <div className="p-4 sm:px-6 border-b border-neutral-100 flex items-center justify-between shrink-0 bg-neutral-50/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-sm shadow-sm">
            AI
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-900 leading-tight">
              Trợ Lý Tài Chính Wealify
            </h3>
            <span className="flex items-center gap-1.5 text-[10px] text-success font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              Sẵn sàng phân tích cục bộ
            </span>
          </div>
        </div>

        {onToggleCollapse && (
          <button
            type="button"
            onClick={onToggleCollapse}
            className="text-neutral-400 hover:text-neutral-600 p-1.5 rounded-lg hover:bg-neutral-100 transition-colors"
            aria-label="Thu gọn cửa sổ chat"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        )}
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 min-h-[320px] max-h-[460px]">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-4 rounded-2xl max-w-[90%] text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-primary text-white rounded-br-none shadow-sm'
                  : 'bg-neutral-100 text-neutral-900 rounded-bl-none border border-neutral-200/60'
              }`}
            >
              {msg.content}
            </div>
            <span className="text-[10px] text-neutral-400 mt-1 px-1">{msg.timestamp}</span>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 p-3.5 rounded-2xl bg-neutral-100 text-neutral-500 text-xs w-fit">
            <span className="flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse [animation-delay:300ms]" />
            </span>
            <span>AI đang tính toán phân tích...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Pills */}
      <div className="px-4 py-2 bg-neutral-50/70 border-t border-neutral-100 flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleSend(prompt)}
            className="px-2.5 py-1 rounded-full bg-white border border-neutral-200 hover:border-primary text-neutral-700 hover:text-primary whitespace-nowrap transition-colors shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-3 sm:p-4 border-t border-neutral-100 bg-white shrink-0">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Hỏi AI về bất kỳ khoản chi tiêu nào..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-xs sm:text-sm text-neutral-900 focus:outline-none focus:border-primary focus:bg-white transition-all placeholder:text-neutral-400"
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            disabled={!inputValue.trim() || isTyping}
            className="px-4 py-2.5 rounded-xl font-bold shrink-0 min-h-[40px]"
          >
            Gửi →
          </Button>
        </form>
      </div>
    </div>
  )
}
