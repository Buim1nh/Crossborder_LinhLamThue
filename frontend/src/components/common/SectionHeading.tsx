import React from 'react'

export interface SectionHeadingProps {
  tag?: string
  title: React.ReactNode
  subtitle?: string
  centered?: boolean
  className?: string
}

export function SectionHeading({
  tag,
  title,
  subtitle,
  centered = false,
  className = '',
}: SectionHeadingProps) {
  return (
    <div
      className={`mb-10 sm:mb-16 ${centered ? 'text-center max-w-3xl mx-auto' : 'max-w-2xl'} ${className}`}
    >
      {tag && (
        <p className="text-xs font-bold text-primary uppercase tracking-widest mb-3 sm:mb-4">
          {tag}
        </p>
      )}
      <h2 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl tracking-wide leading-[1.05] mb-3 sm:mb-4 font-semibold">
        {title}
      </h2>
      {subtitle && (
        <p className="text-sm sm:text-base text-neutral-500 leading-relaxed max-w-xl mx-auto">
          {subtitle}
        </p>
      )}
    </div>
  )
}
