import type { Metadata, Viewport } from 'next'
import { DM_Sans, Oswald } from 'next/font/google'
import './globals.css'

const dmSans = DM_Sans({
  subsets: ['latin', 'latin-ext'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-dm-sans',
  display: 'swap',
})

const oswald = Oswald({
  subsets: ['latin', 'vietnamese'],
  weight: ['500', '600', '700'],
  variable: '--font-oswald',
  display: 'swap',
})

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  viewportFit: 'cover',
  themeColor: '#FF6B1A',
}

export const metadata: Metadata = {
  title: 'Wealify — AI Financial Guardian',
  description:
    'AI phân tích sao kê, phát hiện gian lận, theo dõi chi tiêu. Bảo vệ tài chính của bạn với AI.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className={`${dmSans.variable} ${oswald.variable}`}>
      <body>{children}</body>
    </html>
  )
}
