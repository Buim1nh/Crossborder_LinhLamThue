import React from 'react'
import Link from 'next/link'
import { Button } from '@/components/common/Button'

export interface AuthSuccessCardProps {
  title: string
  message: React.ReactNode
  buttonText?: string
  buttonHref?: string
  onButtonClick?: () => void
  className?: string
}

export function AuthSuccessCard({
  title,
  message,
  buttonText = 'Vào không gian làm việc →',
  buttonHref = '/dashboard',
  onButtonClick,
  className = '',
}: AuthSuccessCardProps) {
  return (
    <div
      className={`p-8 rounded-2xl bg-white border border-success/30 shadow-card text-center animate-in fade-in zoom-in-95 duration-300 ${className}`}
    >
      <div className="w-16 h-16 rounded-full bg-success/10 text-success flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h3 className="font-display text-2xl font-bold text-neutral-900 mb-2">
        {title}
      </h3>

      <div className="text-sm text-neutral-600 mb-6 leading-relaxed">
        {message}
      </div>

      {buttonHref ? (
        <Link href={buttonHref}>
          <Button
            variant="primary"
            size="lg"
            className="w-full justify-center min-h-[48px]"
            onClick={onButtonClick}
          >
            {buttonText}
          </Button>
        </Link>
      ) : (
        <Button
          variant="primary"
          size="lg"
          className="w-full justify-center min-h-[48px]"
          onClick={onButtonClick}
        >
          {buttonText}
        </Button>
      )}
    </div>
  )
}
