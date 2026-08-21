'use client'

import React from 'react'
import { useReveal } from '@/hooks/useReveal'
import { FeatureItem } from '@/types/landing'

export interface FeatureCardProps extends FeatureItem {
  className?: string
}

export function FeatureCard({
  icon,
  num,
  title,
  desc,
  stat,
  statLabel,
  className = '',
}: FeatureCardProps) {
  const { ref, visible } = useReveal()

  return (
    <div
      ref={ref}
      className={`bg-white rounded-xl p-6 sm:p-8 shadow-card border border-neutral-100 transition-all duration-700 hover:shadow-card-hover hover:-translate-y-1 group ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${className}`}
    >
      <div className="flex items-start justify-between mb-6">
        <div className="w-12 h-12 bg-primary-light rounded-lg flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
          {icon}
        </div>
        <span className="font-display text-4xl lg:text-5xl text-neutral-300 leading-none font-bold group-hover:text-primary/70 transition-colors duration-300 select-none">
          {num}
        </span>
      </div>
      <h3 className="text-base sm:text-lg font-bold text-neutral-900 mb-2 sm:mb-3">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed mb-6">{desc}</p>
      <div className="border-t border-neutral-100 pt-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-neutral-500">{statLabel}</span>
          <span className="text-sm font-bold text-primary">{stat}</span>
        </div>
        <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-1000"
            style={{ width: visible ? stat : '0%' }}
          />
        </div>
      </div>
    </div>
  )
}
