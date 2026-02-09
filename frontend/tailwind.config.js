/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#f6faff',
        foreground: '#0f1724',
        card: {
          DEFAULT: '#ffffff',
          foreground: '#0f1724',
        },
        primary: {
          DEFAULT: '#2b8af6',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#e8f4ff',
          foreground: '#0f1724',
        },
        muted: {
          DEFAULT: '#f3f4f6',
          foreground: '#6b7280',
        },
        accent: {
          DEFAULT: '#e0f2fe',
          foreground: '#0369a1',
        },
        destructive: {
          DEFAULT: '#ffe6e6',
          foreground: '#7a1e1e',
        },
        success: {
          DEFAULT: '#d1f5e0',
          foreground: '#07543b',
        },
        warning: {
          DEFAULT: '#fff4de',
          foreground: '#6b4a00',
        },
        border: 'rgba(0, 0, 0, 0.08)',
        input: '#ffffff',
        ring: '#2b8af6',
        sidebar: {
          DEFAULT: '#f0f7ff',
          foreground: '#0f1724',
        },
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '12px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
