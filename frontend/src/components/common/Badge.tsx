import React from 'react'

export interface BadgeProps {
  children: React.ReactNode
  variant?: 'primary' | 'neutral' | 'success' | 'danger'
  hasDot?: boolean
  className?: string
}

export function Badge({
  children,
  variant = 'primary',
  hasDot = false,
  className = '',
}: BadgeProps) {
  const variantStyles = {
    primary: 'bg-primary-light text-primary',
    neutral: 'bg-neutral-900 text-white',
    success: 'bg-success-light text-success',
    danger: 'bg-danger-light text-danger',
  }

  const dotColor = {
    primary: 'bg-primary',
    neutral: 'bg-white',
    success: 'bg-success',
    danger: 'bg-danger',
  }

  return (
    <div
      className={`inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest px-3.5 py-1.5 rounded-full ${variantStyles[variant]} ${className}`}
    >
      {hasDot && (
        <span className={`w-2 h-2 rounded-full animate-pulse ${dotColor[variant]}`} />
      )}
      {children}
    </div>
  )
}
