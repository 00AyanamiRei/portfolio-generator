module.exports = {
  darkMode: 'class',
  content: ['./templates/**/*.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        ghbg: '#0D1117',
        ghcard: '#161B22',
        ghborder: '#30363D',
        ghaccent: '#58A6FF',
      },
    },
  },
};
