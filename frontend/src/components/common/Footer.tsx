import React from 'react'

export interface FooterLinkGroup {
  label: string
  links: { title: string; href?: string }[]
}

const DEFAULT_FOOTER_GROUPS: FooterLinkGroup[] = [
  {
    label: 'Sản phẩm',
    links: [
      { title: 'Tính năng', href: '#features' },
      { title: 'Bảng giá', href: '#pricing' },
      { title: 'Bảo mật', href: '#' },
    ],
  },
  {
    label: 'Công ty',
    links: [
      { title: 'Giới thiệu', href: '#' },
      { title: 'Blog', href: '#' },
      { title: 'Liên hệ', href: '#' },
    ],
  },
  {
    label: 'Pháp lý',
    links: [
      { title: 'Quyền riêng tư', href: '#' },
      { title: 'Điều khoản', href: '#' },
      { title: 'Cookies', href: '#' },
    ],
  },
]

const SOCIAL_LINKS = [
  { name: 'Twitter', href: '#' },
  { name: 'GitHub', href: '#' },
  { name: 'LinkedIn', href: '#' },
]

export function Footer() {
  return (
    <footer className="bg-neutral-900 text-white pb-[max(2rem,env(safe-area-inset-bottom))]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 py-12 sm:py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-8 sm:gap-12 mb-12 sm:mb-16">
          {/* Brand Info */}
          <div className="col-span-1 sm:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg font-display">W</span>
              </div>
              <span className="font-bold text-xl tracking-tight">Wealify</span>
            </div>
            <p className="text-sm text-neutral-400 leading-relaxed max-w-xs">
              AI Financial Guardian. Đọc sao kê, phát hiện gian lận, theo dõi chi tiêu — tất cả trong một công cụ.
            </p>
          </div>

          {/* Navigation link groups */}
          {DEFAULT_FOOTER_GROUPS.map((group) => (
            <div key={group.label}>
              <p className="text-xs font-semibold text-neutral-300 uppercase tracking-widest mb-4">
                {group.label}
              </p>
              <ul className="space-y-3">
                {group.links.map((link) => (
                  <li key={link.title}>
                    <a
                      href={link.href || '#'}
                      className="text-sm text-neutral-400 hover:text-white transition-colors"
                    >
                      {link.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="border-t border-neutral-700 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-neutral-400">
            2026 Wealify. Cross-Border AI Innovation Hackathon WLF-01.
          </p>
          <div className="flex gap-6">
            {SOCIAL_LINKS.map((s) => (
              <a
                key={s.name}
                href={s.href}
                className="text-sm text-neutral-400 hover:text-white transition-colors"
              >
                {s.name}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
