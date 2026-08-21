import React from 'react'

export interface AuthErrorAlertProps {
  message?: string
  className?: string
}

export function AuthErrorAlert({ message, className = '' }: AuthErrorAlertProps) {
  if (!message) return null

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`mb-6 p-4 rounded-lg bg-danger-light border border-danger/20 text-danger text-sm flex items-center gap-3 animate-in fade-in duration-150 ${className}`}
    >
      <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span className="font-medium">{message}</span>
    </div>
  )
}
