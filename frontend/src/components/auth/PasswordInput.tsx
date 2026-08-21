import React, { useState } from 'react'

export interface PasswordInputProps {
  id: string
  label: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder?: string
  required?: boolean
  error?: boolean
  headerRight?: React.ReactNode
  className?: string
  inputClassName?: string
  ariaInvalid?: boolean
  name?: string
  autoComplete?: string
}

export function PasswordInput({
  id,
  label,
  value,
  onChange,
  placeholder = 'Nhập mật khẩu',
  required = true,
  error = false,
  headerRight,
  className = '',
  inputClassName = '',
  ariaInvalid,
  name = 'password',
  autoComplete = 'current-password',
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-1.5">
        <label htmlFor={id} className="block text-xs font-bold uppercase tracking-wider text-neutral-700">
          {label} {required && <span className="text-primary">*</span>}
        </label>
        {headerRight}
      </div>

      <div className="relative">
        <input
          id={id}
          name={name}
          type={showPassword ? 'text' : 'password'}
          required={required}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          aria-invalid={ariaInvalid ?? error}
          className={`w-full pl-4 pr-12 py-3 rounded-lg bg-white border text-neutral-900 text-sm focus:outline-none focus:ring-2 transition-all placeholder:text-neutral-400 ${
            error
              ? 'border-danger focus:border-danger focus:ring-danger/20'
              : 'border-neutral-200 focus:border-primary focus:ring-primary/20'
          } ${inputClassName}`}
        />

        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 p-1"
          aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
        >
          {showPassword ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"
              />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}
