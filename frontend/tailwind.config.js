/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'system-ui', 'sans-serif'],
        sans:    ['DM Sans', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand:  '#1DB954',
        fire:   '#ff4d00',
        purple: '#a855f7',
        amber:  '#f59e0b',
        coral:  '#f87171',
      },
      animation: {
        'float':     'float 3s ease-in-out infinite',
        'glow-pulse':'glow-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        float:       { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-8px)' } },
        'glow-pulse': { '0%,100%': { boxShadow: '0 0 20px #1DB95440' }, '50%': { boxShadow: '0 0 40px #1DB95480' } },
      },
    },
  },
  plugins: [],
}
