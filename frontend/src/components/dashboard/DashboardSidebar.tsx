'use client'

import React from 'react'
import Link from 'next/link'

export type DashboardNavTab =
  | 'overview'
  | 'statements'
  | 'transactions'
  | 'anomalies'
  | 'subscriptions'
  | 'assistant'

export interface DashboardSidebarProps {
  activeTab: DashboardNavTab
  onTabChange: (tab: DashboardNavTab) => void
  isCollapsed?: boolean
  onToggleCollapse?: () => void
  notificationCount?: number
  subscriptionCount?: number
  className?: string
}

export function DashboardSidebar({
  activeTab,
  onTabChange,
  isCollapsed = false,
  onToggleCollapse,
  notificationCount = 3,
  subscriptionCount = 4,
  className = '',
}: DashboardSidebarProps) {
  const navItems = [
    {
      id: 'overview' as DashboardNavTab,
      label: 'Tổng quan',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      ),
    },
    {
      id: 'statements' as DashboardNavTab,
      label: 'Nguồn sao kê',
      badge: '3/3',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      id: 'transactions' as DashboardNavTab,
      label: 'Lịch sử giao dịch',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
    },
    {
      id: 'anomalies' as DashboardNavTab,
      label: 'Cảnh báo chi tiêu',
      badge: notificationCount > 0 ? `${notificationCount}` : undefined,
      badgeColor: 'bg-warning-light text-[#B45309]',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    {
      id: 'subscriptions' as DashboardNavTab,
      label: 'Dịch vụ định kỳ',
      badge: subscriptionCount > 0 ? `${subscriptionCount}` : undefined,
      badgeColor: 'bg-primary-light text-primary',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
    },
    {
      id: 'assistant' as DashboardNavTab,
      label: 'Trợ lý AI Guardian',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
    },
  ]

  return (
    <aside
      className={`bg-white border-r border-neutral-200 flex flex-col justify-between h-screen sticky top-0 transition-all duration-200 z-20 ${
        isCollapsed ? 'w-20' : 'w-64'
      } ${className}`}
    >
      <div>
        {/* Top Logo & App Title */}
        <div className="h-16 px-5 border-b border-neutral-100 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center transition-transform group-hover:scale-105 shadow-xs shrink-0">
              <span className="text-white font-bold text-lg font-display">W</span>
            </div>
            {!isCollapsed && (
              <div className="overflow-hidden">
                <span className="font-bold text-lg text-neutral-900 tracking-tight block leading-tight truncate">
                  Wealify
                </span>
                <span className="text-[11px] text-neutral-500 font-medium tracking-wide block truncate">
                  AI Financial Guardian
                </span>
              </div>
            )}
          </Link>

          {onToggleCollapse && (
            <button
              type="button"
              onClick={onToggleCollapse}
              className="text-neutral-400 hover:text-neutral-600 p-1.5 rounded-lg hover:bg-neutral-100 transition-colors"
              aria-label={isCollapsed ? 'Mở rộng sidebar' : 'Thu gọn sidebar'}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                {isCollapsed ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                )}
              </svg>
            </button>
          )}
        </div>

        {/* Navigation List */}
        <div className="p-3 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-neutral-900 text-white shadow-xs'
                    : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'
                }`}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`shrink-0 ${isActive ? 'text-white' : 'text-neutral-500'}`}>
                    {item.icon}
                  </span>
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </div>

                {!isCollapsed && item.badge && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      item.badgeColor || (isActive ? 'bg-white/20 text-white' : 'bg-neutral-200 text-neutral-700')
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Bottom Privacy & Security Status */}
      <div className="p-4 border-t border-neutral-100 bg-neutral-50/50">
        {!isCollapsed ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="text-xs font-bold text-neutral-800">Bảo Mật Cục Bộ</span>
            </div>
            <p className="text-xs text-neutral-500 leading-relaxed">
              Dữ liệu sao kê phân tích trực tiếp trên thiết bị của bạn.
            </p>
          </div>
        ) : (
          <div className="flex justify-center" title="Bảo mật cục bộ">
            <span className="w-2.5 h-2.5 rounded-full bg-success" />
          </div>
        )}
      </div>
    </aside>
  )
}
