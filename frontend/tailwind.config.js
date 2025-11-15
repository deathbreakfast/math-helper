/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 20px 45px -25px rgba(15, 23, 42, 0.35)',
        floating: '0 25px 60px -30px rgba(15, 23, 42, 0.3)',
        glass: '0 30px 80px -40px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
}

