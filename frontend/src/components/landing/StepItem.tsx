'use client'

import React from 'react'
import { useReveal } from '@/hooks/useReveal'
import { StepItemData } from '@/types/landing'

export interface StepItemProps extends StepItemData {
  className?: string
}

export function StepItem({
  num,
  title,
  time,
  desc,
  className = '',
}: StepItemProps) {
  const { ref, visible } = useReveal()

  return (
    <div
      ref={ref}
      className={`flex-1 transition-all duration-700 bg-white sm:bg-transparent p-6 sm:p-0 rounded-xl sm:rounded-none border border-neutral-200/60 sm:border-0 shadow-sm sm:shadow-none ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${className}`}
    >
      <p className="font-display text-5xl sm:text-6xl lg:text-7xl xl:text-8xl text-primary leading-none mb-3 sm:mb-4 font-bold select-none">
        {num}
      </p>
      <div className="inline-block bg-primary-light text-primary px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full mb-3 sm:mb-4">
        {time}
      </div>
      <h3 className="text-lg sm:text-xl font-bold text-neutral-900 mb-2 sm:mb-3">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed">{desc}</p>
    </div>
  )
}
