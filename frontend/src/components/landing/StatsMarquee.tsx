import React from 'react'
import { StatItem } from '@/types/landing'

const DEFAULT_STATS: StatItem[] = [
  { value: '50K+', label: 'Người dùng được bảo vệ' },
  { value: '55 Tỷ+', label: 'Gian lận & phí ẩn phát hiện' },
  { value: '99.9%', label: 'Độ chính xác AI' },
  { value: '847', label: 'Mối đe dọa bị chặn' },
  { value: '< 0.2s', label: 'Thời gian phát hiện' },
  { value: '24/7', label: 'Bảo vệ thời gian thực' },
]

export interface StatsMarqueeProps {
  stats?: StatItem[]
  className?: string
}

export function StatsMarquee({ stats = DEFAULT_STATS, className = '' }: StatsMarqueeProps) {
  const marqueeList = [...stats, ...stats]

  return (
    <section
      className={`bg-primary relative overflow-hidden py-6 lg:py-8 border-y border-white/15 shadow-inner select-none ${className}`}
    >
      {/* Background ambient gradient glow */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary via-[#FF7A2F] to-primary pointer-events-none" />

      <div className="relative z-10 w-full overflow-hidden marquee-mask">
        <div className="animate-marquee flex items-center gap-6 sm:gap-10 lg:gap-14">
          {marqueeList.map((stat, i) => (
            <div
              key={i}
              className="flex items-center gap-6 sm:gap-10 lg:gap-14 flex-shrink-0 group cursor-default"
            >
              <div className="flex items-center gap-3 sm:gap-4">
                <span className="font-display text-3xl sm:text-4xl lg:text-5xl text-white leading-none font-bold tracking-wide drop-shadow-sm group-hover:scale-105 transition-transform duration-300">
                  {stat.value}
                </span>
                <span className="text-[11px] sm:text-xs lg:text-sm font-semibold text-white/90 uppercase tracking-wider leading-tight whitespace-nowrap max-w-[150px]">
                  {stat.label}
                </span>
              </div>

              {/* Separator indicator */}
              <div className="text-white/40 group-hover:text-white/80 transition-colors flex items-center justify-center">
                <svg className="w-4 h-4 sm:w-5 sm:h-5 animate-pulse" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0L14.5 9.5L24 12L14.5 14.5L12 24L9.5 14.5L0 12L9.5 9.5L12 0Z" />
                </svg>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
