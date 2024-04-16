/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    // TODO: add theming of edutap
    themes: [
      {
        edutap: {
          "primary": "#165793",
          "secondary": "#3E99C0",
          "accent": "#d86626",
          "neutral": "#24343D",
          "base-100": "#FFFFFF",
          "info": "#A4D1E5",
          "success": "#12684A",
          "warning": "#EBC505",
          "error": "#E84330",
        },
      },
    ],
  },
  plugins: [require("daisyui")],
}