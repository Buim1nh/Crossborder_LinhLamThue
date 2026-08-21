'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/common/Button'
import { tokenStorage, authApi } from '@/lib/api'

export interface SidebarTopHeaderProps {
  title: string
  breadcrumb?: string
  onUploadClick?: () => void
  onExportClick?: () => void
  notificationCount?: number
  onSearchChange?: (val: string) => void
  searchValue?: string
  className?: string
}

export function SidebarTopHeader({
  title,
  breadcrumb = 'Bảng Điều Khiển',
  onUploadClick,
  onExportClick,
  notificationCount = 3,
  onSearchChange,
  searchValue = '',
  className = '',
}: SidebarTopHeaderProps) {
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
    <header className={`bg-white border-b border-neutral-200 h-16 px-6 lg:px-8 flex items-center justify-between sticky top-0 z-10 shadow-xs ${className}`}>
      {/* Left: Page Title & Breadcrumb */}
      <div>
        <div className="flex items-center gap-2 text-xs text-neutral-400">
          <span>{breadcrumb}</span>
          <span>/</span>
          <span className="text-neutral-700 font-medium">{title}</span>
        </div>
        <h1 className="text-lg font-bold text-neutral-900 leading-none mt-0.5">
          {title}
        </h1>
      </div>

      {/* Right: Search, Upload CTA, Notifications & Profile */}
      <div className="flex items-center gap-4">
        {/* Search input */}
        <div className="relative hidden md:block w-64">
          <input
            type="text"
            value={searchValue}
            onChange={(e) => onSearchChange?.(e.target.value)}
            placeholder="Tìm kiếm giao dịch (/)..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-neutral-50 border border-neutral-200 text-xs text-neutral-900 focus:outline-none focus:border-primary focus:bg-white transition-all placeholder:text-neutral-400"
          />
          <svg
            className="w-4 h-4 text-neutral-400 absolute left-3 top-1/2 -translate-y-1/2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Upload Action */}
        <Button
          variant="primary"
          size="sm"
          onClick={onUploadClick}
          className="flex items-center gap-1.5 font-semibold text-xs"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          <span className="hidden sm:inline">Tải sao kê</span>
        </Button>

        {/* Notification Bell */}
        <button
          type="button"
          className="p-2 rounded-lg text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 transition-colors relative"
          aria-label="Thông báo"
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

        {/* User Profile Avatar & Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setUserDropdownOpen(!userDropdownOpen)}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-neutral-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20"
            aria-expanded={userDropdownOpen}
            aria-label="Menu tài khoản"
          >
            <div className="w-8 h-8 rounded-full bg-primary text-white font-bold text-xs flex items-center justify-center shadow-xs">
              {userInitial}
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-bold text-neutral-900 leading-tight truncate max-w-[120px]">
                {displayName}
              </p>
              <p className="text-[11px] text-neutral-500 truncate max-w-[120px]">
                {displayEmail}
              </p>
            </div>
            <svg className="w-4 h-4 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
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
                {onExportClick && (
                  <button
                    type="button"
                    onClick={() => {
                      setUserDropdownOpen(false)
                      onExportClick()
                    }}
                    className="w-full text-left block px-4 py-2.5 text-xs text-neutral-700 hover:bg-neutral-50 hover:text-primary transition-colors"
                  >
                    Xuất báo cáo PDF
                  </button>
                )}
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
    </header>
  )
}
