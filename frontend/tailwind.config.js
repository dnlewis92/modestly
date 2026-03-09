/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        blush: {
          50: "#fdf4f3",
          100: "#fce8e6",
          200: "#f9d0cc",
          300: "#f4a8a1",
          400: "#ec7069",
          500: "#e04e45",
          600: "#cc3329",
          700: "#ab2720",
          800: "#8d231f",
          900: "#761f1e",
        },
      },
    },
  },
  plugins: [],
};
