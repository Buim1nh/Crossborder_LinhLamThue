import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  className?: string
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center font-bold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/20 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none'

  const sizeStyles = {
    sm: 'px-4 py-2 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'px-8 py-4 text-sm tracking-wide',
  }

  const variantStyles = {
    primary:
      'bg-primary text-white hover:bg-primary-hover shadow-[0_2px_8px_rgba(255,107,26,0.3)] hover:shadow-[0_4px_12px_rgba(255,107,26,0.4)]',
    secondary:
      'bg-neutral-900 text-white hover:bg-neutral-800 shadow-sm',
    outline:
      'bg-white text-neutral-900 border border-neutral-200 hover:border-primary hover:text-primary',
    ghost:
      'bg-transparent text-neutral-600 hover:text-primary hover:bg-neutral-50',
  }

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
