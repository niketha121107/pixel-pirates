import type { Config } from 'tailwindcss';

const config: Config = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    light: '#f9a8d4',
                    DEFAULT: '#ec4899',
                    dark: '#db2777',
                    accent: '#f97316',
                    surface: '#ffffff',
                    bg: '#fdf6f0',
                },
                status: {
                    success: '#34d399',
                    warning: '#fbbf24',
                    error: '#fb7185',
                    info: '#67e8f9',
                },
                candy: {
                    pink: '#fbb6ce',
                    peach: '#fcd5b5',
                    mint: '#a7f3d0',
                    lavender: '#ddd6fe',
                    lemon: '#fef08a',
                    sky: '#bae6fd',
                }
            },
            backgroundImage: {
                'gradient-brand': 'linear-gradient(135deg, #ec4899, #f97316)',
                'gradient-surface': 'linear-gradient(145deg, rgba(253,246,240,0.9) 0%, rgba(255,255,255,0.95) 100%)',
                'gradient-candy': 'linear-gradient(135deg, #fbb6ce, #fcd5b5, #a7f3d0)',
            },
            boxShadow: {
                'glass': '0 8px 32px 0 rgba(236, 72, 153, 0.12)',
                'glass-hover': '0 8px 32px 0 rgba(236, 72, 153, 0.2)',
                'glow': '0 0 20px rgba(236, 72, 153, 0.35)',
                'glow-accent': '0 0 20px rgba(249, 115, 22, 0.3)',
            },
            animation: {
                'blob': 'blob 10s infinite',
                'slide-down': 'slide-down 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                'slide-up': 'slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
                'fade-in': 'fade-in 0.3s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                blob: {
                    '0%': { transform: 'translate(0px, 0px) scale(1)' },
                    '33%': { transform: 'translate(40px, -60px) scale(1.15)' },
                    '66%': { transform: 'translate(-30px, 30px) scale(0.85)' },
                    '100%': { transform: 'translate(0px, 0px) scale(1)' },
                },
                'slide-down': {
                    '0%': { opacity: '0', transform: 'translateY(-20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'slide-up': {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'fade-in': {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                }
            }
        },
    },
    plugins: [],
};

export default config;
