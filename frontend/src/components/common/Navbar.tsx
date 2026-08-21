'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { NavItem } from '@/types/landing'
import { Button } from './Button'

export interface NavbarProps {
  navLinks?: NavItem[]
  onLoginClick?: () => void
  onCtaClick?: () => void
}

const DEFAULT_NAV_LINKS: NavItem[] = [
  { label: 'Tính năng', href: '#features' },
  { label: 'Cách hoạt động', href: '#how' },
  { label: 'Bảng giá', href: '#pricing' },
]

export function Navbar({
  navLinks = DEFAULT_NAV_LINKS,
  onLoginClick,
  onCtaClick,
}: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled || open
          ? 'bg-white/95 border-b border-neutral-200 shadow-card backdrop-blur-md'
          : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center transition-transform group-hover:scale-105">
            <span className="text-white font-bold text-lg font-display">W</span>
          </div>
          <span className="font-bold text-xl text-neutral-900 tracking-tight">Wealify</span>
        </a>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-neutral-500 hover:text-primary transition-colors"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* Desktop CTA actions */}
        <div className="hidden md:flex items-center gap-3">
          <Link href="/login">
            <Button variant="outline" size="md" onClick={onLoginClick}>
              Đăng nhập
            </Button>
          </Link>
          <Link href="/register">
            <Button variant="primary" size="md" onClick={onCtaClick}>
              Dùng thử miễn phí
            </Button>
          </Link>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden min-w-[44px] min-h-[44px] flex items-center justify-center p-2 text-neutral-900 rounded-lg hover:bg-neutral-100 active:bg-neutral-200 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/30"
          onClick={() => setOpen(!open)}
          aria-label={open ? 'Đóng menu' : 'Mở menu'}
          aria-expanded={open}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {open ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </nav>

      {/* Mobile drawer */}
      {open && (
        <div className="md:hidden bg-white/98 backdrop-blur-lg border-t border-neutral-200 px-6 py-6 flex flex-col gap-4 shadow-xl animate-in slide-in-from-top-2 duration-200 max-h-[calc(100vh-4rem)] overflow-y-auto">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-base font-semibold text-neutral-900 hover:text-primary active:bg-primary-light/50 py-3 px-3 rounded-lg transition-colors"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <div className="flex flex-col gap-3 pt-4 border-t border-neutral-100">
            <Link href="/login" onClick={() => setOpen(false)}>
              <Button variant="outline" size="md" className="w-full justify-center min-h-[44px]" onClick={onLoginClick}>
                Đăng nhập
              </Button>
            </Link>
            <Link href="/register" onClick={() => setOpen(false)}>
              <Button variant="primary" size="md" className="w-full justify-center min-h-[44px]" onClick={onCtaClick}>
                Dùng thử miễn phí
              </Button>
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}
