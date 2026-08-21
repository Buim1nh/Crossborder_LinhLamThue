'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Badge } from '@/components/common/Badge'
import { Button } from '@/components/common/Button'
import { tokenStorage, authApi } from '@/lib/api'

export interface DashboardHeaderProps {
  onUploadClick?: () => void
  onExportClick?: () => void
  notificationCount?: number
}

export function DashboardHeader({
  onUploadClick,
  onExportClick,
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
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-30 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Identity & Privacy Badge */}
        <div className="flex items-center gap-4 sm:gap-6">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center transition-transform group-hover:scale-105 shadow-sm">
              <span className="text-white font-bold text-lg font-display">W</span>
            </div>
            <div>
              <span className="font-bold text-lg text-neutral-900 tracking-tight block leading-tight">
                Wealify
              </span>
              <span className="text-[10px] text-neutral-500 font-medium tracking-wider uppercase hidden sm:block">
                AI Financial Guardian
              </span>
            </div>
          </Link>

          <div className="hidden md:flex items-center">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-success-light text-success text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              100% Cục bộ & Bảo mật
            </span>
          </div>
        </div>

        {/* Right: Actions & User Profile */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Export Report Action */}
          {onExportClick && (
            <Button
              variant="outline"
              size="sm"
              onClick={onExportClick}
              className="hidden sm:inline-flex items-center gap-1.5"
            >
              <svg className="w-4 h-4 text-neutral-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Xuất báo cáo PDF</span>
            </Button>
          )}

          {/* Upload Trigger CTA */}
          <Button
            variant="primary"
            size="sm"
            onClick={onUploadClick}
            className="flex items-center gap-1.5 font-bold"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            <span className="hidden sm:inline">Tải lên sao kê</span>
            <span className="sm:hidden">Tải file</span>
          </Button>

          {/* Notification Alert Bell */}
          <div className="relative">
            <button
              type="button"
              className="p-2 rounded-lg text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 transition-colors relative"
              aria-label="Thông báo bất thường"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {notificationCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-primary text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {notificationCount}
                </span>
              )}
            </button>
          </div>

          {/* User Profile Avatar & Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              className="flex items-center gap-2 p-1 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
              aria-expanded={userDropdownOpen}
              aria-label="Menu tài khoản"
            >
              <div className="w-8 h-8 rounded-full bg-primary-light border border-primary/30 text-primary font-bold text-sm flex items-center justify-center">
                {userInitial}
              </div>
              <svg className="w-4 h-4 text-neutral-500 hidden sm:block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {userDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-card-hover border border-neutral-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                <div className="px-4 py-2.5 border-b border-neutral-100">
                  <p className="text-sm font-bold text-neutral-900 truncate">{displayName}</p>
                  <p className="text-xs text-neutral-500 truncate">{displayEmail}</p>
                </div>

                <div className="py-1">
                  <Link
                    href="/"
                    className="block px-4 py-2 text-xs text-neutral-700 hover:bg-neutral-50 hover:text-primary transition-colors"
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
                    className="w-full text-left block px-4 py-2 text-xs text-neutral-700 hover:bg-neutral-50 hover:text-primary transition-colors"
                  >
                    Báo cáo tài chính PDF
                  </button>
                </div>

                <div className="pt-1 border-t border-neutral-100">
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full text-left block px-4 py-2 text-xs font-semibold text-danger hover:bg-danger-light transition-colors"
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
