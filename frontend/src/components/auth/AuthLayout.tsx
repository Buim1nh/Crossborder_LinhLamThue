import React from 'react'
import Link from 'next/link'
import { Badge } from '@/components/common/Badge'

export interface AuthFeatureItem {
  icon: React.ReactNode
  title: string
  desc: string
  iconBgClass?: string
  iconColorClass?: string
}

export interface AuthLayoutProps {
  headline: React.ReactNode
  subtitle: string
  leftBadgeText?: string
  features?: AuthFeatureItem[]
  trustPledgeCard?: React.ReactNode
  formTitle: string
  formSubtitle: string
  redirectPrompt?: string
  redirectLinkText?: string
  redirectHref?: string
  children: React.ReactNode
}

const DEFAULT_AUTH_FEATURES: AuthFeatureItem[] = [
  {
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
        />
      </svg>
    ),
    title: '100% Cục Bộ & Bảo Mật',
    desc: 'Không bao giờ yêu cầu mật khẩu đăng nhập ngân hàng hay thông tin CVV.',
    iconBgClass: 'bg-success/20',
    iconColorClass: 'text-success',
  },
  {
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: 'Phân Tích Đa Nguồn Siêu Tốc',
    desc: 'Tải lên file sao kê CSV/PDF và nhận báo cáo đối chiếu thông minh ngay tức thì.',
    iconBgClass: 'bg-primary/20',
    iconColorClass: 'text-primary',
  },
]

export function AuthLayout({
  headline,
  subtitle,
  leftBadgeText = 'AI Financial Guardian',
  features = DEFAULT_AUTH_FEATURES,
  trustPledgeCard,
  formTitle,
  formSubtitle,
  redirectPrompt,
  redirectLinkText,
  redirectHref,
  children,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 flex flex-col lg:flex-row relative">
      {/* ── Left Column: Brand & Security Showcase (Desktop/Tablet) ── */}
      <div className="lg:w-5/12 xl:w-1/2 bg-neutral-900 text-white p-8 lg:p-16 flex flex-col justify-between relative overflow-hidden">
        {/* Background decorative ambient glow & subtle watermark */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-primary/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden select-none opacity-5">
          <span className="font-display text-[18vw] font-bold text-white tracking-widest">
            WEALIFY
          </span>
        </div>

        {/* Top bar with logo */}
        <div className="relative z-10">
          <Link href="/" className="inline-flex items-center gap-3 group">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center transition-transform group-hover:scale-105 shadow-md">
              <span className="text-white font-bold text-xl font-display">W</span>
            </div>
            <span className="font-bold text-2xl tracking-tight text-white">Wealify</span>
          </Link>
          <div className="mt-4">
            <Badge variant="primary" hasDot>
              {leftBadgeText}
            </Badge>
          </div>
        </div>

        {/* Center narrative visual */}
        <div className="relative z-10 my-12 lg:my-0">
          <h1 className="font-display text-4xl sm:text-5xl xl:text-6xl font-semibold tracking-wide leading-[1.05] mb-6">
            {headline}
          </h1>
          <p className="text-neutral-300 text-base lg:text-lg leading-relaxed max-w-lg mb-8">
            {subtitle}
          </p>

          {/* Feature highlights or custom pledge card */}
          {trustPledgeCard || (
            <div className="space-y-4 max-w-lg">
              {features.map((feat, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm"
                >
                  <div
                    className={`w-8 h-8 rounded-lg ${feat.iconBgClass || 'bg-primary/20'} ${
                      feat.iconColorClass || 'text-primary'
                    } flex items-center justify-center shrink-0 mt-0.5`}
                  >
                    {feat.icon}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white mb-0.5">{feat.title}</p>
                    <p className="text-xs text-neutral-400">{feat.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bottom trust footer */}
        <div className="relative z-10 pt-6 border-t border-neutral-800 flex items-center justify-between text-xs text-neutral-400">
          <span>Cross-Border AI Hackathon 2026</span>
          <span className="flex items-center gap-1.5 text-neutral-300">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            Bảo vệ hoạt động 24/7
          </span>
        </div>
      </div>

      {/* ── Right Column: Interactive Form Container ── */}
      <div className="lg:w-7/12 xl:w-1/2 p-6 sm:p-12 lg:p-16 xl:p-20 flex items-center justify-center">
        <div className="w-full max-w-md mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h2 className="font-display text-3xl sm:text-4xl font-semibold tracking-wide text-neutral-900 mb-2">
              {formTitle}
            </h2>
            <p className="text-sm text-neutral-500">{formSubtitle}</p>
          </div>

          {/* Form Content */}
          {children}

          {/* Redirect link footer */}
          {redirectPrompt && redirectLinkText && redirectHref && (
            <div className="mt-8 pt-6 border-t border-neutral-200 text-center">
              <p className="text-sm text-neutral-600">
                {redirectPrompt}{' '}
                <Link
                  href={redirectHref}
                  className="font-bold text-primary hover:text-primary-hover hover:underline"
                >
                  {redirectLinkText}
                </Link>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
