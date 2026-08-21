'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Badge'
import { SectionHeading } from '@/components/common/SectionHeading'
import { StatsMarquee } from '@/components/landing/StatsMarquee'
import { FeatureCard } from '@/components/landing/FeatureCard'
import { StepItem } from '@/components/landing/StepItem'
import { PricingCard } from '@/components/landing/PricingCard'
import { HeroIllustration } from '@/components/landing/HeroIllustration'
import { FeatureItem, StepItemData, PricingPlan } from '@/types/landing'

// ─── Landing Data Configurations ─────────────────────────────────────────────
const TRUST_ITEMS = [
  'Đọc file, không đăng nhập ngân hàng',
  'CVV không bao giờ được lưu trữ',
]

const FEATURES: FeatureItem[] = [
  {
    num: '01',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    title: 'Phát hiện bất thường',
    desc: 'AI học thói quen chi tiêu của bạn và gắn cờ ngay lập tức khi có điều bất thường.',
    stat: '94%',
    statLabel: 'Tỷ lệ phát hiện',
  },
  {
    num: '02',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Phân loại thông minh',
    desc: 'Tự động phân loại giao dịch từ tất cả các nguồn: tài khoản, ví, thẻ.',
    stat: '99%',
    statLabel: 'Độ chính xác',
  },
  {
    num: '03',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    title: 'Đối chiếu biên nhận',
    desc: 'Tự động đối chiếu giao dịch với email biên nhận. Không bao giờ bỏ lỡ một khoản mua nào.',
    stat: '87%',
    statLabel: 'Tỷ lệ đối chiếu',
  },
  {
    num: '04',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    title: 'Theo dõi đăng ký',
    desc: 'Tìm tất cả các khoản phí định kỳ. Nhận nhắc trước khi gia hạn. Hủy những gì bạn không cần.',
    stat: '100%',
    statLabel: 'Phạm vi theo dõi',
  },
]

const STEPS: StepItemData[] = [
  {
    num: '01',
    title: 'Tải lên sao kê',
    time: '~2 phút',
    desc: 'Kéo thả sao kê ngân hàng, ví điện tử hoặc thẻ tín dụng. Hỗ trợ CSV và PDF.',
  },
  {
    num: '02',
    title: 'AI phân tích',
    time: '~30 giây',
    desc: 'AI xử lý dữ liệu, học thói quen của bạn và tự động xác định các vấn đề tiềm ẩn.',
  },
  {
    num: '03',
    title: 'Được bảo vệ',
    time: 'Liên tục',
    desc: 'Nhận cảnh báo, báo cáo và insights. Xem lại mọi thứ theo cách của bạn.',
  },
]

const PRICING_PLANS: PricingPlan[] = [
  {
    name: 'Miễn phí',
    price: '0₫',
    period: 'vĩnh viễn',
    desc: 'Trải nghiệm đầy đủ tính năng phân tích sao kê ngoại tuyến.',
    features: [
      'Tải lên 3 nguồn sao kê (Bank / Ví / Thẻ)',
      'Phát hiện bất thường & phí ẩn cơ bản',
      'Bảo mật 100% — Phân tích xử lý cục bộ',
      'Báo cáo tổng kết tài chính cơ bản',
    ],
  },
  {
    name: 'Cá nhân Pro',
    price: '79.000₫',
    period: 'tháng',
    desc: 'Dành cho người quản lý nhiều tài khoản & thẻ tín dụng.',
    highlight: true,
    features: [
      'Mọi tính năng trong gói Miễn phí',
      'Phân tích AI phát hiện trùng lặp nâng cao',
      'Trợ lý AI tư vấn tài chính chuyên sâu',
      'Theo dõi và nhắc hủy đăng ký tự động',
      'Xuất báo cáo PDF tài chính chuẩn CFO',
    ],
  },
  {
    name: 'Gia đình / Nhóm',
    price: '149.000₫',
    period: 'tháng',
    desc: 'Dành cho gia đình hoặc nhóm quản lý tài chính chung.',
    features: [
      'Hỗ trợ tối đa 5 hồ sơ tài chính thành viên',
      'Mọi tính năng trong gói Pro',
      'Bảng điều khiển chi tiêu hợp nhất',
      'Cảnh báo rủi ro tức thì cho cả gia đình',
      'Hỗ trợ kỹ thuật ưu tiên 24/7',
    ],
  },
]

// ─── Main Landing Page ────────────────────────────────────────────────────────
export default function LandingPage() {
  const [heroVisible, setHeroVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setHeroVisible(true), 100)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="min-h-screen bg-white text-neutral-900 overflow-x-hidden">
      <Navbar />

      {/* ── Hero Section ─────────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center pt-16 bg-neutral-50">
        {/* Background glow & subtle technical grid */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 right-0 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-primary/10 rounded-full blur-3xl" />
          <svg className="absolute inset-0 w-full h-full opacity-[0.03]" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#111827" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-12 py-16 sm:py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
            {/* Hero Left Content */}
            <div
              className={`transition-all duration-1000 ${
                heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'
              }`}
            >
              <div className="mb-6 sm:mb-8">
                <Badge variant="primary" hasDot>
                  AI Financial Guardian
                </Badge>
              </div>

              <h1 className="font-display text-5xl sm:text-6xl md:text-7xl lg:text-[7vw] xl:text-8xl leading-[0.95] tracking-wide mb-6 font-semibold">
                BẢO VỆ<br />
                <span className="text-primary">TIỀN CỦA</span><br />
                BẠN
              </h1>

              <p className="text-base sm:text-lg text-neutral-500 leading-relaxed max-w-md mb-8 sm:mb-10">
                Tải lên sao kê ngân hàng, ví điện tử, thẻ tín dụng. AI phân tích, phát hiện gian lận và theo dõi chi tiêu — trước khi bạn nhận ra.
              </p>

              <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                <Link href="/register" className="w-full sm:w-auto">
                  <Button size="lg" variant="primary" className="w-full sm:w-auto min-h-[48px]">
                    Dùng thử miễn phí →
                  </Button>
                </Link>
                <a href="#how" className="w-full sm:w-auto">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto min-h-[48px]">
                    Xem cách hoạt động
                  </Button>
                </a>
              </div>

              {/* Trust Badges */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-6 mt-8 sm:mt-12 pt-8 sm:pt-12 border-t border-neutral-200">
                {TRUST_ITEMS.map((text) => (
                  <div key={text} className="flex items-center gap-2">
                    <svg
                      className="w-5 h-5 text-success shrink-0"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-xs sm:text-sm text-neutral-500 leading-snug">{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Hero Right Graphic - Visible across all screen sizes with responsive scaling */}
            <div
              className={`flex items-center justify-center transition-all duration-1000 delay-300 w-full mt-6 lg:mt-0 ${
                heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'
              }`}
            >
              <HeroIllustration />
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Marquee Ribbon ────────────────────────────────────────── */}
      <StatsMarquee />

      {/* ── Features Section ─────────────────────────────────────────────── */}
      <section id="features" className="py-16 sm:py-24 lg:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12">
          <SectionHeading
            tag="Tính năng"
            title={
              <>
                MỌI THỨ BẠN CẦN<br />ĐỂ ĐƯỢC BẢO VỆ
              </>
            }
            subtitle="Không chỉ là ứng dụng ghi chép. Wealify hoạt động như một chuyên gia tài chính — phân tích sâu, phát hiện thông minh, báo cáo rõ ràng."
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {FEATURES.map((feat) => (
              <FeatureCard key={feat.num} {...feat} />
            ))}
          </div>
        </div>
      </section>
      {/* ── How it works Section ────────────────────────────────────────── */}
      <section id="how" className="py-16 sm:py-24 lg:py-32 bg-neutral-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12">
          <div className="mb-10 sm:mb-16">
            <p className="text-xs font-bold text-primary uppercase tracking-widest mb-3 sm:mb-4">Quy trình</p>
            <h2 className="font-display text-4xl sm:text-5xl lg:text-7xl tracking-wide font-semibold">
              CÁCH HOẠT ĐỘNG
            </h2>
          </div>

          <div className="flex flex-col lg:flex-row gap-8 lg:gap-0 border-t border-neutral-200 pt-10 sm:pt-16">
            {STEPS.map((step, idx) => (
              <div key={step.num} className="contents">
                <StepItem {...step} />
                {idx < STEPS.length - 1 && (
                  <div className="hidden lg:block w-px bg-neutral-200 mx-8 xl:mx-12 self-stretch" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing Section ─────────────────────────────────────────────── */}
      <section id="pricing" className="py-16 sm:py-24 lg:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12">
          <SectionHeading
            centered
            tag="Bảng giá"
            title="ĐƠN GIẢN, MINH BẠCH"
            subtitle="Không có chi phí ẩn. Không có bẫy. Bắt đầu miễn phí."
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto items-stretch">
            {PRICING_PLANS.map((plan) => (
              <PricingCard key={plan.name} {...plan} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA Section ───────────────────────────────────────────── */}
      <section className="py-16 sm:py-24 lg:py-32 bg-neutral-900 text-white relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
          <span className="font-display text-[20vw] text-white/[0.02] leading-none select-none whitespace-nowrap font-semibold">
            WLF WLF WLF WLF
          </span>
        </div>
        <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-12 text-center">
          <h2 className="font-display text-4xl sm:text-6xl lg:text-[7vw] tracking-wide leading-[0.95] mb-6 sm:mb-8 font-semibold">
            SẴN SÀNG<br />
            <span className="text-primary">BẢO VỆ?</span>
          </h2>
          <p className="text-base sm:text-lg text-neutral-300 leading-relaxed max-w-xl mx-auto mb-8 sm:mb-12">
            Tham gia cùng hơn 50.000 người dùng tin tưởng Wealify bảo vệ cuộc sống tài chính của họ.
          </p>
          <Link href="/register" className="inline-block w-full sm:w-auto">
            <Button size="lg" variant="primary" className="w-full sm:w-auto text-sm sm:text-base px-8 sm:px-12 py-4 sm:py-5 uppercase font-bold tracking-wider min-h-[48px]">
              BẮT ĐẦU MIỄN PHÍ
            </Button>
          </Link>
        </div>
      </section>
      <Footer />
    </div>
  )
}
