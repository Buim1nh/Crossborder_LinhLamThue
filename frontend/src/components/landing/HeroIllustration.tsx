import React from 'react'

export function HeroIllustration({ className = '' }: { className?: string }) {
  return (
    <div className={`relative w-full max-w-lg mx-auto select-none ${className}`}>
      {/* Background ambient glow */}
      <div className="absolute -inset-4 bg-gradient-to-tr from-primary/10 via-orange-500/5 to-transparent rounded-3xl blur-2xl -z-10" />

      <svg
        viewBox="0 0 520 400"
        className="w-full h-auto drop-shadow-xl"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="Minh họa bảo mật và đối chiếu sao kê tài chính đa nguồn Wealify"
      >
        <defs>
          <linearGradient id="shieldGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF6B1A" />
            <stop offset="100%" stopColor="#E55A0F" />
          </linearGradient>
          <filter id="softShadow" x="-10%" y="-10%" width="130%" height="130%">
            <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#111827" floodOpacity="0.08" />
          </filter>
        </defs>

        {/* ── CARD 1: Vietcombank CSV (Top-Left) ── */}
        <g filter="url(#softShadow)">
          <rect x="20" y="30" width="230" height="110" rx="12" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1.5" />
          {/* Card Header */}
          <rect x="36" y="44" width="8" height="8" rx="2" fill="#16A34A" />
          <text x="50" y="52" fill="#111827" fontFamily="DM Sans, sans-serif" fontSize="12" fontWeight="700">
            Vietcombank
          </text>
          <rect x="180" y="42" width="54" height="18" rx="4" fill="#F3F4F6" />
          <text x="188" y="55" fill="#6B7280" fontFamily="DM Sans, sans-serif" fontSize="10" fontWeight="600">
            .CSV
          </text>

          {/* Row 1 */}
          <text x="36" y="80" fill="#374151" fontFamily="DM Sans, sans-serif" fontSize="11">
            Lương Tháng 02
          </text>
          <text x="175" y="80" fill="#16A34A" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="700">
            +32.000.000₫
          </text>

          {/* Row 2 */}
          <text x="36" y="104" fill="#6B7280" fontFamily="DM Sans, sans-serif" fontSize="11">
            EVN Tiền điện
          </text>
          <text x="180" y="104" fill="#111827" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="600">
            -1.450.000₫
          </text>
          <line x1="36" y1="90" x2="234" y2="90" stroke="#F3F4F6" strokeWidth="1" />
        </g>

        {/* ── CARD 2: Ví MoMo (Bottom-Left) ── */}
        <g filter="url(#softShadow)">
          <rect x="30" y="160" width="230" height="115" rx="12" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1.5" />
          {/* Card Header */}
          <rect x="46" y="174" width="8" height="8" rx="2" fill="#A21CAF" />
          <text x="60" y="182" fill="#111827" fontFamily="DM Sans, sans-serif" fontSize="12" fontWeight="700">
            Ví MoMo
          </text>
          <rect x="190" y="172" width="54" height="18" rx="4" fill="#F3F4F6" />
          <text x="198" y="185" fill="#6B7280" fontFamily="DM Sans, sans-serif" fontSize="10" fontWeight="600">
            .PDF
          </text>

          {/* Row 1 */}
          <text x="46" y="210" fill="#374151" fontFamily="DM Sans, sans-serif" fontSize="11">
            GrabFood HN
          </text>
          <text x="195" y="210" fill="#111827" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="600">
            -125.000₫
          </text>

          {/* Row 2: Anomaly Row */}
          <rect x="38" y="222" width="214" height="38" rx="6" fill="#FFFBEB" stroke="#FDE68A" strokeWidth="1" />
          <text x="48" y="238" fill="#D97706" fontFamily="DM Sans, sans-serif" fontSize="10" fontWeight="700">
            ⚠️ Netflix (Trừ 2 lần)
          </text>
          <text x="190" y="238" fill="#DC2626" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="700">
            -260.000₫
          </text>
          <text x="48" y="252" fill="#92400E" fontFamily="DM Sans, sans-serif" fontSize="9">
            Phát hiện trùng lặp với thẻ Visa
          </text>
        </g>

        {/* ── CARD 3: Techcombank Visa (Bottom) ── */}
        <g filter="url(#softShadow)">
          <rect x="50" y="295" width="220" height="85" rx="12" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1.5" />
          <rect x="66" y="309" width="8" height="8" rx="2" fill="#DC2626" />
          <text x="80" y="317" fill="#111827" fontFamily="DM Sans, sans-serif" fontSize="12" fontWeight="700">
            Techcombank Visa
          </text>
          <text x="66" y="342" fill="#6B7280" fontFamily="DM Sans, sans-serif" fontSize="11">
            Phí thường niên thẻ
          </text>
          <text x="200" y="342" fill="#DC2626" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="600">
            -350.000₫
          </text>
          <text x="66" y="362" fill="#9CA3AF" fontFamily="DM Sans, sans-serif" fontSize="10">
            **** **** **** 8829
          </text>
        </g>

        {/* ── CONNECTING DATA STREAMS ── */}
        <path
          d="M 250 85 C 310 85, 320 180, 360 180"
          stroke="#FF6B1A"
          strokeWidth="2"
          strokeDasharray="5 4"
          fill="none"
          opacity="0.7"
        />
        <path
          d="M 260 215 C 300 215, 320 200, 360 200"
          stroke="#FF6B1A"
          strokeWidth="2.5"
          strokeDasharray="5 4"
          fill="none"
          opacity="0.9"
        />
        <path
          d="M 270 335 C 320 335, 330 220, 360 220"
          stroke="#FF6B1A"
          strokeWidth="2"
          strokeDasharray="5 4"
          fill="none"
          opacity="0.7"
        />

        {/* ── AI GUARDIAN CORE ENGINE (Right) ── */}
        <g filter="url(#softShadow)">
          {/* Outer Pulse Rings */}
          <circle cx="410" cy="200" r="75" fill="#FFF1E8" opacity="0.6" />
          <circle cx="410" cy="200" r="58" fill="#FFE5D4" opacity="0.8" />
          <circle cx="410" cy="200" r="44" fill="url(#shieldGlow)" />

          {/* AI Guardian Shield Icon */}
          <path
            d="M410 178 L428 186 V202 C428 214 420 224 410 228 C400 224 392 214 392 202 V186 L410 178 Z"
            fill="white"
          />
          <path
            d="M405 202 L409 206 L417 196"
            stroke="#FF6B1A"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>

        {/* ── FLOATING GUARDIAN INSIGHT BADGE ── */}
        <g filter="url(#softShadow)">
          <rect x="310" y="60" width="190" height="60" rx="10" fill="#111827" />
          <circle cx="330" cy="90" r="8" fill="#16A34A" />
          <path d="M327 90 L329 92 L333 88" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
          <text x="345" y="82" fill="#FFFFFF" fontFamily="DM Sans, sans-serif" fontSize="11" fontWeight="700">
            ĐỐI CHIẾU 3 NGUỒN
          </text>
          <text x="345" y="98" fill="#D1D5DB" fontFamily="DM Sans, sans-serif" fontSize="9">
            Phát hiện 1 trùng lặp & 1 phí ẩn
          </text>
        </g>

        {/* ── FLOATING LOCAL PRIVACY BADGE ── */}
        <g filter="url(#softShadow)">
          <rect x="320" y="300" width="180" height="46" rx="8" fill="#FFFFFF" stroke="#DCFCE7" strokeWidth="1.5" />
          <text x="336" y="320" fill="#16A34A" fontFamily="DM Sans, sans-serif" fontSize="10" fontWeight="700">
            🔒 100% XỬ LÝ CỤC BỘ
          </text>
          <text x="336" y="334" fill="#6B7280" fontFamily="DM Sans, sans-serif" fontSize="9">
            Không lưu mật khẩu ngân hàng
          </text>
        </g>
      </svg>
    </div>
  )
}
