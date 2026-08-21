import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          hover: 'var(--color-primary-hover)',
          light: 'var(--color-primary-light)',
        },
        danger: {
          DEFAULT: 'var(--color-danger)',
          light: 'var(--color-danger-light)',
        },
        success: {
          DEFAULT: 'var(--color-success)',
          light: 'var(--color-success-light)',
        },
        neutral: {
          900: 'var(--color-neutral-900)',
          700: 'var(--color-neutral-700)',
          500: 'var(--color-neutral-500)',
          300: 'var(--color-neutral-300)',
          200: 'var(--color-neutral-200)',
          100: 'var(--color-neutral-100)',
          50: 'var(--color-neutral-50)',
        },
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.75rem',
        md: '0.5rem',
        sm: '0.375rem',
      },
      boxShadow: {
        card: 'var(--shadow-card)',
        'card-hover': 'var(--shadow-card-hover)',
      },
      fontFamily: {
        sans: ['var(--font-dm-sans)', 'DM Sans', 'system-ui', 'sans-serif'],
        display: ['var(--font-oswald)', 'Oswald', 'Impact', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
