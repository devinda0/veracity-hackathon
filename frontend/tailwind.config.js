/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#f4efe6',
        ink: '#102223',
        accent: '#ff6b35',
        spruce: '#184e43',
        mist: '#d9ede5',
        sand: '#fbf6ef',
      },
      boxShadow: {
        panel: '0 24px 60px rgba(16, 34, 35, 0.14)',
      },
      fontFamily: {
        sans: ['"Space Grotesk"', '"Avenir Next"', '"Segoe UI"', 'sans-serif'],
        display: ['"Fraunces"', '"Iowan Old Style"', 'serif'],
      },
      backgroundImage: {
        'grid-fade':
          'linear-gradient(rgba(16,34,35,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(16,34,35,0.06) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
};

