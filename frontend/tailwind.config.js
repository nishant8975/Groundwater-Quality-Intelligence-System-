/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F172A', // slate-900
        surface: '#1E293B',    // slate-800
        primary: '#38BDF8',    // sky-400
        wawqi: {
          excellent: '#34D399', // emerald-400
          good: '#60A5FA',      // blue-400
          poor: '#FBBF24',      // amber-400
          very_poor: '#F97316', // orange-500
          unsuitable: '#EF4444',// red-500
          unavailable: '#64748B'// slate-500
        }
      }
    },
  },
  plugins: [],
}
