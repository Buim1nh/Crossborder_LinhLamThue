import { ReactNode } from 'react'

export interface NavItem {
  label: string
  href: string
}

export interface StatItem {
  value: string
  label: string
}

export interface FeatureItem {
  num: string
  icon: ReactNode
  title: string
  desc: string
  stat: string
  statLabel: string
}

export interface StepItemData {
  num: string
  title: string
  time: string
  desc: string
}

export interface PricingPlan {
  name: string
  price: string
  period: string
  desc: string
  features: string[]
  highlight?: boolean
}
