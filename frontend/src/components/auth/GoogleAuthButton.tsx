'use client'

import React, { useState } from 'react'
import { useGoogleLogin } from '@react-oauth/google'
import { authApi, AuthTokenResponse } from '@/lib/api'

export interface GoogleAuthButtonProps {
  isLoading?: boolean
  disabled?: boolean
  onClick?: () => void
  onSuccess?: (data: AuthTokenResponse) => void
  onError?: (error: string) => void
  buttonText?: string
  dividerText?: string
  showDivider?: boolean
  className?: string
}

export function GoogleAuthButton({
  isLoading = false,
  disabled = false,
  onClick,
  onSuccess,
  onError,
  buttonText = 'Tiếp tục với Google',
  dividerText = 'Hoặc tiếp tục bằng email',
  showDivider = true,
  className = '',
}: GoogleAuthButtonProps) {
  const [internalLoading, setInternalLoading] = useState(false)

  // Real Google OAuth 2.0 Token Client Login
  const triggerGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setInternalLoading(true)
      try {
        // Send real Google access_token to backend for userinfo verification
        const authData = await authApi.googleAuth({
          access_token: tokenResponse.access_token,
        })
        onSuccess?.(authData)
      } catch (err: unknown) {
        const errorMsg =
          err instanceof Error
            ? err.message
            : 'Xác thực Google không thành công. Vui lòng thử lại.'
        onError?.(errorMsg)
      } finally {
        setInternalLoading(false)
      }
    },
    onError: (errorResponse) => {
      const errorDetail =
        errorResponse.error_description ||
        'Đăng nhập Google bị hủy hoặc chưa cấu hình Client ID hợp lệ trong .env.'
      onError?.(errorDetail)
    },
  })

  const handleClick = () => {
    if (onClick) {
      onClick()
      return
    }

    try {
      triggerGoogleLogin()
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Không thể khởi tạo popup Google OAuth. Vui lòng kiểm tra NEXT_PUBLIC_GOOGLE_CLIENT_ID.'
      onError?.(msg)
    }
  }

  const activeLoading = isLoading || internalLoading

  return (
    <div className={`w-full ${className}`}>
      {/* Social Button */}
      <div className="mb-6">
        <button
          type="button"
          disabled={activeLoading || disabled}
          onClick={handleClick}
          className="w-full flex items-center justify-center gap-3 py-3.5 px-4 rounded-lg bg-white border border-neutral-200 text-neutral-700 font-semibold text-sm hover:bg-neutral-50 hover:border-neutral-300 active:bg-neutral-100 transition-all shadow-sm min-h-[48px] focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-60"
        >
          {activeLoading ? (
            <span className="flex items-center gap-2.5 text-primary font-medium">
              <svg className="animate-spin w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Đang xác thực với Google...
            </span>
          ) : (
            <>
              <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>{buttonText}</span>
            </>
          )}
        </button>
      </div>

      {/* Divider */}
      {showDivider && (
        <div className="relative flex items-center justify-center mb-6">
          <div className="w-full border-t border-neutral-200" />
          <span className="absolute bg-neutral-50 px-3 text-xs font-semibold uppercase tracking-wider text-neutral-400">
            {dividerText}
          </span>
        </div>
      )}
    </div>
  )
}
