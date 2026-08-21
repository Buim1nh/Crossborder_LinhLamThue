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
  isOpen?: boolean
  onClose?: () => void
  initialMessages?: ChatMessage[]
  onSendMessage?: (text: string) => void
  className?: string
}

const DEFAULT_MESSAGES: ChatMessage[] = [
  {
    id: 'msg-1',
    role: 'assistant',
    content: (
      <div className="space-y-2 text-sm text-neutral-800 leading-relaxed">
        <p>
          Xin chào! Tôi là <strong>Trợ lý Tài chính Wealify</strong>.
        </p>
        <p>
          Sau khi đối chiếu chéo 3 nguồn sao kê (Vietcombank, Ví MoMo, Techcombank Visa), tôi nhận thấy:
        </p>
        <ul className="list-disc pl-4 space-y-1 text-xs text-neutral-700">
          <li><strong>Giao dịch trùng lặp:</strong> Netflix 260.000₫ bị trừ đồng thời trên Ví MoMo và Thẻ Visa ngày 15/02.</li>
          <li><strong>Phí phát sinh:</strong> Phí thường niên thẻ tín dụng 350.000₫.</li>
          <li><strong>Tổng khả năng tiết kiệm:</strong> Khoảng <strong>610.000₫ / tháng</strong>.</li>
        </ul>
        <p className="text-xs text-neutral-500">
          Bạn có thể bấm vào gợi ý bên dưới hoặc hỏi tôi bất kỳ khoản chi tiêu nào.
        </p>
      </div>
    ),
    timestamp: '09:30',
  },
]

const QUICK_PROMPTS = [
  'Tóm tắt chi tiêu 3 nguồn tháng này',
  'Kiểm tra các khoản phí ngân hàng ẩn',
  'Danh sách dịch vụ đang tự động gia hạn',
  'Hướng dẫn tra soát khoản Netflix trùng lặp',
]

export function AIChatPanel({
  isOpen = true,
  onClose,
  initialMessages = DEFAULT_MESSAGES,
  onSendMessage,
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
    if (isOpen) {
      scrollToBottom()
    }
  }, [messages, isTyping, isOpen])

  if (!isOpen) return null

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

    setIsTyping(true)
    setTimeout(() => {
      let botResponseText: React.ReactNode = ''
      if (text.includes('Netflix') || text.includes('tra soát')) {
        botResponseText = (
          <div className="space-y-2 text-sm text-neutral-800 leading-relaxed">
            <p>
              Đối với khoản <strong>Netflix 260.000₫</strong> bị trừ 2 lần:
            </p>
            <p className="text-xs text-neutral-700">
              1. Giao dịch 1: Ví MoMo lúc 02:15 ngày 15/02.<br />
              2. Giao dịch 2: Techcombank Visa **** 8829 lúc 02:16 ngày 15/02.
            </p>
            <p className="text-xs text-success font-semibold">
              Thời hạn tra soát còn 54 ngày. Bạn có thể nhấn nút "Tạo mẫu tra soát" ở bảng cảnh báo để sao chép văn bản khiếu nại ngân hàng.
            </p>
          </div>
        )
      } else if (text.includes('gia hạn') || text.includes('định kỳ') || text.includes('subscription')) {
        botResponseText = (
          <div className="space-y-2 text-sm text-neutral-800 leading-relaxed">
            <p>
              Danh sách 4 gói dịch vụ tự động gia hạn:
            </p>
            <ul className="list-disc pl-4 space-y-1 text-xs text-neutral-700">
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
          <div className="space-y-1.5 text-sm text-neutral-800 leading-relaxed">
            <p>
              Tổng kết 3 nguồn tháng này: Bạn đã tiết kiệm được <strong>17.150.000₫</strong> (đạt tỷ lệ tiết kiệm 53.6%).
            </p>
            <p className="text-xs text-neutral-600">
              Nhóm chi tiêu lớn nhất gồm: <strong>Hóa đơn tiện ích (1.450.000₫)</strong> và <strong>Dịch vụ trực tuyến (1.120.000₫)</strong>.
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
    }, 900)
  }

  return (
    <div
      className={`fixed inset-y-0 right-0 w-full sm:w-[460px] bg-white border-l border-neutral-200 shadow-2xl z-40 flex flex-col animate-in slide-in-from-right duration-300 ${className}`}
    >
      {/* Header */}
      <div className="p-4 sm:px-6 border-b border-neutral-100 flex items-center justify-between bg-neutral-50/70 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-sm shadow-xs">
            AI
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-900 leading-tight">
              Trợ Lý Tài Chính Wealify
            </h3>
            <span className="flex items-center gap-1.5 text-xs text-success font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-success" />
              Phân tích dữ liệu cục bộ
            </span>
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-neutral-400 hover:text-neutral-600 p-1.5 rounded-lg hover:bg-neutral-100 transition-colors"
            aria-label="Đóng trợ lý AI"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Messages Stream */}
      <div
        role="log"
        aria-live="polite"
        className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-4 rounded-2xl max-w-[92%] text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-primary text-white rounded-br-none shadow-xs'
                  : 'bg-neutral-100 text-neutral-900 rounded-bl-none border border-neutral-200/70'
              }`}
            >
              {msg.content}
            </div>
            <span className="text-xs text-neutral-400 mt-1 px-1">{msg.timestamp}</span>
          </div>
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 p-3.5 rounded-2xl bg-neutral-100 text-neutral-500 text-xs w-fit">
            <span className="flex gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse [animation-delay:300ms]" />
            </span>
            <span>AI đang phân tích dữ liệu sao kê...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Suggestions */}
      <div className="p-3 bg-neutral-50 border-t border-neutral-100 flex items-center gap-2 overflow-x-auto text-xs">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleSend(prompt)}
            className="px-3 py-1.5 rounded-lg bg-white border border-neutral-200 hover:border-primary text-neutral-700 hover:text-primary whitespace-nowrap transition-colors shadow-2xs font-medium"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-neutral-100 bg-white shrink-0">
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
            placeholder="Hỏi trợ lý AI về thu chi, phí ẩn..."
            className="flex-1 px-4 py-2.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm text-neutral-900 focus:outline-none focus:border-primary focus:bg-white transition-all placeholder:text-neutral-400"
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            disabled={!inputValue.trim() || isTyping}
            className="px-4 py-2.5 rounded-xl font-bold shrink-0 min-h-[42px]"
          >
            Gửi
          </Button>
        </form>
      </div>
    </div>
  )
}
