'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/common/Button'
import { tokenStorage, authApi } from '@/lib/api'

export interface DashboardHeaderProps {
  onUploadClick?: () => void
  onExportClick?: () => void
  onAIChatClick?: () => void
  isChatOpen?: boolean
  notificationCount?: number
}

export function DashboardHeader({
  onUploadClick,
  onExportClick,
  onAIChatClick,
  isChatOpen = false,
  notificationCount = 2,
}: DashboardHeaderProps) {
  const [userDropdownOpen, setUserDropdownOpen] = useState(false)
  const user = tokenStorage.getUser()

  const handleLogout = async () => {
    await authApi.logout()
    window.location.href = '/login'
  }

  const userInitial = user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'
  const displayName = user?.full_name || 'Người dùng Wealify'
  const displayEmail = user?.email || 'demo@wealify.vn'

  return (
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Identity & Privacy Badge */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center transition-transform group-hover:scale-105 shadow-xs">
              <span className="text-white font-bold text-lg font-display">W</span>
            </div>
            <div>
              <span className="font-bold text-lg text-neutral-900 tracking-tight block leading-tight">
                Wealify
              </span>
              <span className="text-xs text-neutral-500 font-medium tracking-wide hidden sm:block">
                AI Financial Guardian
              </span>
            </div>
          </Link>

          <div className="hidden md:flex items-center">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-100 text-neutral-700 text-xs font-medium border border-neutral-200">
              <span className="w-2 h-2 rounded-full bg-success" />
              Bảo mật cục bộ (Local Analysis)
            </span>
          </div>
        </div>

        {/* Right: Actions & User Profile */}
        <div className="flex items-center gap-3">
          {/* AI Chat Drawer Toggle */}
          <button
            type="button"
            onClick={onAIChatClick}
            className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all border ${
              isChatOpen
                ? 'bg-neutral-900 text-white border-neutral-900 shadow-xs'
                : 'bg-white text-neutral-800 border-neutral-200 hover:border-primary hover:text-primary'
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <span className="hidden sm:inline">Trợ lý AI</span>
            {notificationCount > 0 && !isChatOpen && (
              <span className="w-2 h-2 rounded-full bg-primary" />
            )}
          </button>

          {/* Export Report Action */}
          {onExportClick && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportClick}
              className="hidden lg:inline-flex items-center gap-1.5 text-xs text-neutral-700"
            >
              <svg className="w-4 h-4 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Xuất PDF</span>
            </Button>
          )}

          {/* Upload Trigger CTA */}
          <Button
            variant="primary"
            size="sm"
            onClick={onUploadClick}
            className="flex items-center gap-1.5 font-semibold text-xs sm:text-sm"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            <span>Tải sao kê</span>
          </Button>

          {/* User Profile Avatar & Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
              aria-expanded={userDropdownOpen}
              aria-label="Menu tài khoản"
            >
              <div className="w-8 h-8 rounded-full bg-primary text-white font-bold text-sm flex items-center justify-center shadow-xs">
                {userInitial}
              </div>
              <svg className="w-4 h-4 text-neutral-500 hidden sm:block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {userDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-card-hover border border-neutral-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                <div className="px-4 py-3 border-b border-neutral-100">
                  <p className="text-sm font-bold text-neutral-900 truncate">{displayName}</p>
                  <p className="text-xs text-neutral-500 truncate">{displayEmail}</p>
                </div>

                <div className="py-1">
                  <Link
                    href="/"
                    className="block px-4 py-2.5 text-xs text-neutral-700 hover:bg-neutral-50 hover:text-primary transition-colors"
                    onClick={() => setUserDropdownOpen(false)}
                  >
                    Trang chủ Wealify
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setUserDropdownOpen(false)
                      onExportClick?.()
                    }}
                    className="w-full text-left block px-4 py-2.5 text-xs text-neutral-700 hover:bg-neutral-50 hover:text-primary transition-colors"
                  >
                    Báo cáo tài chính PDF
                  </button>
                </div>

                <div className="pt-1 border-t border-neutral-100">
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full text-left block px-4 py-2.5 text-xs font-semibold text-danger hover:bg-danger-light transition-colors"
                  >
                    Đăng xuất
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
