import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Dark theme base colors
        background: 'hsl(0 0% 5%)', // #0D0D0D
        foreground: 'hsl(0 0% 98%)',

        // Aurora palette for glassmorphism
        aurora: {
          blue: '#00D4FF',
          purple: '#B84FFF',
          pink: '#FF4FD1',
          green: '#4FFF88',
          yellow: '#FFD700',
        },

        // Glass morphism colors
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.1)',
          heavy: 'rgba(255, 255, 255, 0.15)',
        },

        // UI component colors
        border: 'rgba(255, 255, 255, 0.1)',
        input: 'rgba(255, 255, 255, 0.05)',
        ring: 'hsl(195 100% 50%)',
        primary: {
          DEFAULT: 'hsl(195 100% 50%)',
          foreground: 'hsl(23 23% 9%)',
        },
        secondary: {
          DEFAULT: 'rgba(255, 255, 255, 0.05)',
          foreground: 'hsl(0 0% 98%)',
        },
        destructive: {
          DEFAULT: 'hsl(0 84% 60%)',
          foreground: 'hsl(0 0% 98%)',
        },
        muted: {
          DEFAULT: 'rgba(255, 255, 255, 0.05)',
          foreground: 'hsl(0 0% 65%)',
        },
        accent: {
          DEFAULT: 'rgba(255, 255, 255, 0.05)',
          foreground: 'hsl(0 0% 98%)',
        },
        popover: {
          DEFAULT: 'hsl(0 0% 5%)',
          foreground: 'hsl(0 0% 98%)',
        },
        card: {
          DEFAULT: 'hsl(0 0% 5%)',
          foreground: 'hsl(0 0% 98%)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        aurora: 'aurora 20s linear infinite',
        float: 'float 3s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif',
        ],
      },
      keyframes: {
        aurora: {
          '0%, 100%': { transform: 'rotate(0deg) scale(1)' },
          '33%': { transform: 'rotate(120deg) scale(1.1)' },
          '66%': { transform: 'rotate(240deg) scale(0.9)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config
