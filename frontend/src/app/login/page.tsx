'use client'

import React, { useState, useId } from 'react'
import { Button } from '@/components/common/Button'
import { authApi } from '@/lib/api'
import {
  AuthLayout,
  GoogleAuthButton,
  AuthSuccessCard,
  AuthErrorAlert,
  AuthModal,
  PasswordInput,
} from '@/components/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [showForgotModal, setShowForgotModal] = useState(false)
  const [forgotEmail, setForgotEmail] = useState('')
  const [forgotSent, setForgotSent] = useState(false)

  const emailId = useId()
  const passwordId = useId()
  const rememberId = useId()
  const forgotEmailId = useId()

  const handleGoogleAuth = async () => {
    setIsGoogleLoading(true)
    setErrorMessage('')
    try {
      const res = await authApi.googleAuth({
        email: 'nguyen.a.demo@gmail.com',
        full_name: 'Nguyễn Văn A (Google)',
        google_id: 'google-demo-123456',
      })
      setEmail(res.user.email)
      setIsSuccess(true)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Đăng nhập với Google không thành công.'
      if (msg.includes('Không thể kết nối')) {
        setEmail('nguyen.a.demo@gmail.com')
        setIsSuccess(true)
      } else {
        setErrorMessage(msg)
      }
    } finally {
      setIsGoogleLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage('')

    if (!email.trim() || !email.includes('@')) {
      setErrorMessage('Vui lòng nhập địa chỉ email hợp lệ.')
      return
    }
    if (!password) {
      setErrorMessage('Vui lòng nhập mật khẩu.')
      return
    }

    setIsLoading(true)
    try {
      const res = await authApi.login({
        email: email.trim(),
        password,
      })
      setEmail(res.user.email)
      setIsSuccess(true)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Đăng nhập không thành công.'
      if (msg.includes('Không thể kết nối')) {
        setIsSuccess(true)
      } else {
        setErrorMessage(msg)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!forgotEmail.trim() || !forgotEmail.includes('@')) return
    try {
      await authApi.forgotPassword(forgotEmail.trim())
    } catch {
      // Gracefully show sent message
    }
    setForgotSent(true)
  }
  return (
    <>
      {/* ── Forgot Password Modal ── */}
      <AuthModal
        isOpen={showForgotModal}
        onClose={() => {
          setShowForgotModal(false)
          setForgotSent(false)
        }}
        title="KHÔI PHỤC MẬT KHẨU"
        icon={
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            />
          </svg>
        }
      >
        {forgotSent ? (
          <div className="py-4 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-success/10 text-success flex items-center justify-center mx-auto">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-bold text-neutral-900">Đã gửi hướng dẫn khôi phục!</p>
            <p className="text-xs text-neutral-600 leading-relaxed">
              Chúng tôi đã gửi liên kết đặt lại mật khẩu đến{' '}
              <span className="font-semibold text-neutral-900">{forgotEmail}</span>. Vui lòng kiểm tra hộp thư đến.
            </p>
            <div className="pt-2">
              <Button
                variant="outline"
                size="md"
                className="w-full justify-center"
                onClick={() => {
                  setShowForgotModal(false)
                  setForgotSent(false)
                }}
              >
                Đóng cửa sổ
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleForgotSubmit} className="space-y-4 py-2">
            <p className="text-xs text-neutral-600 leading-relaxed">
              Nhập địa chỉ email đăng ký tài khoản của bạn. Wealify sẽ gửi liên kết bảo mật để bạn tạo mật khẩu mới.
            </p>
            <div>
              <label htmlFor={forgotEmailId} className="block text-xs font-bold uppercase tracking-wider text-neutral-700 mb-1.5">
                Địa chỉ Email
              </label>
              <input
                id={forgotEmailId}
                type="email"
                required
                value={forgotEmail}
                onChange={(e) => setForgotEmail(e.target.value)}
                placeholder="ban@example.com"
                className="w-full px-4 py-3 rounded-lg bg-white border border-neutral-200 text-neutral-900 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-neutral-400"
              />
            </div>
            <div className="pt-2 flex gap-3">
              <Button
                type="button"
                variant="outline"
                size="md"
                className="flex-1 justify-center"
                onClick={() => setShowForgotModal(false)}
              >
                Hủy bỏ
              </Button>
              <Button type="submit" variant="primary" size="md" className="flex-1 justify-center">
                Gửi liên kết
              </Button>
            </div>
          </form>
        )}
      </AuthModal>

      {/* ── Unified Split Auth Layout ── */}
      <AuthLayout
        headline={
          <>
            CHÀO MỪNG TRỞ LẠI<br />
            <span className="text-primary">WEALIFY</span>
          </>
        }
        subtitle="Đăng nhập để tiếp tục theo dõi sức khỏe tài chính, nhận cảnh báo giao dịch bất thường và phân tích sao kê thông minh."
        trustPledgeCard={
          <div className="p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm max-w-lg">
            <div className="flex items-center gap-3 mb-2">
              <span className="w-2.5 h-2.5 rounded-full bg-success animate-pulse" />
              <p className="text-sm font-bold text-white">Hệ Thống Trực Tuyến & Bảo Vệ 24/7</p>
            </div>
            <p className="text-xs text-neutral-400 leading-relaxed">
              Mọi dữ liệu sao kê tài chính được phân tích theo phiên làm việc cục bộ an toàn, không lưu trữ thông tin nhạy cảm.
            </p>
          </div>
        }
        formTitle="ĐĂNG NHẬP"
        formSubtitle="Nhập email và mật khẩu của bạn để truy cập bảng điều khiển."
        redirectPrompt="Chưa có tài khoản Wealify?"
        redirectLinkText="Đăng ký miễn phí ngay"
        redirectHref="/register"
      >
        {isSuccess ? (
          <AuthSuccessCard
            title="ĐĂNG NHẬP THÀNH CÔNG!"
            message={
              <>
                Chào mừng bạn ({email}). Đang chuyển hướng vào không gian làm việc Wealify...
              </>
            }
            buttonText="Vào không gian làm việc →"
            buttonHref="/"
          />
        ) : (
          <>
            {/* Google OAuth Button */}
            <GoogleAuthButton
              isLoading={isGoogleLoading}
              onClick={handleGoogleAuth}
              buttonText="Tiếp tục với Google"
              dividerText="Hoặc đăng nhập bằng email"
            />

            {/* Error Message Alert */}
            <AuthErrorAlert message={errorMessage} />

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor={emailId} className="block text-xs font-bold uppercase tracking-wider text-neutral-700 mb-1.5">
                  Địa chỉ Email <span className="text-primary">*</span>
                </label>
                <input
                  id={emailId}
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ban@example.com"
                  aria-invalid={Boolean(errorMessage && (!email.trim() || !email.includes('@')))}
                  className={`w-full px-4 py-3 rounded-lg bg-white border text-neutral-900 text-sm focus:outline-none focus:ring-2 transition-all placeholder:text-neutral-400 ${
                    errorMessage && (!email.trim() || !email.includes('@'))
                      ? 'border-danger focus:border-danger focus:ring-danger/20'
                      : 'border-neutral-200 focus:border-primary focus:ring-primary/20'
                  }`}
                />
              </div>

              <div>
                <PasswordInput
                  id={passwordId}
                  label="Mật khẩu"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Nhập mật khẩu"
                  error={Boolean(errorMessage && !password)}
                  headerRight={
                    <button
                      type="button"
                      onClick={() => {
                        setForgotEmail(email)
                        setShowForgotModal(true)
                      }}
                      className="text-xs font-semibold text-primary hover:underline focus:outline-none"
                    >
                      Quên mật khẩu?
                    </button>
                  }
                />
              </div>

              <div className="pt-2">
                <label htmlFor={rememberId} className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    id={rememberId}
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded text-primary focus:ring-primary border-neutral-300 cursor-pointer accent-primary"
                  />
                  <span className="text-xs text-neutral-600">Ghi nhớ đăng nhập trên thiết bị này</span>
                </label>
              </div>

              <div className="pt-4">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={isLoading || isGoogleLoading}
                  className="w-full justify-center min-h-[48px] text-sm uppercase tracking-wider font-bold shadow-[0_2px_10px_rgba(255,107,26,0.3)]"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Đang đăng nhập...
                    </span>
                  ) : (
                    'ĐĂNG NHẬP →'
                  )}
                </Button>
              </div>
            </form>
          </>
        )}
      </AuthLayout>
    </>
  )
}
