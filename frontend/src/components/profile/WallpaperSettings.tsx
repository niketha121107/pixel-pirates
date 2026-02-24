import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Palette, Monitor, Sun, Moon, Gamepad2, ImageIcon } from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';

export interface WallpaperOption {
    id: string;
    name: string;
    category: 'pastel' | 'dark' | 'gaming' | 'aesthetic';
    preview: string;
    gradient: string;
    blobColors: string[];
    /** Optional image URL for aesthetic wallpapers */
    imageUrl?: string;
}

// Helper to build wallpaper entries quickly
const wp = (
    id: string, name: string, category: WallpaperOption['category'],
    preview: string, gradient: string, blobColors: [string, string, string],
    imageUrl?: string
): WallpaperOption => ({ id, name, category, preview, gradient, blobColors, ...(imageUrl ? { imageUrl } : {}) });

const WALLPAPERS: WallpaperOption[] = [
    // ══════════════════════════════════════════════════════════
    // ██  PASTEL  (41 wallpapers)
    // ══════════════════════════════════════════════════════════
    wp('default',           'Peach Blossom',      'pastel', 'bg-[#fdf6f0]', 'linear-gradient(135deg,#fdf6f0,#fff5f5)', ['bg-pink-200/40','bg-orange-200/30','bg-emerald-200/25']),
    wp('ocean-breeze',      'Ocean Breeze',       'pastel', 'bg-gradient-to-br from-blue-50 to-cyan-50', 'linear-gradient(135deg,#eff6ff,#ecfeff)', ['bg-blue-200/40','bg-cyan-200/30','bg-indigo-200/25']),
    wp('lavender-dream',    'Lavender Dream',     'pastel', 'bg-gradient-to-br from-purple-50 to-pink-50', 'linear-gradient(135deg,#faf5ff,#fdf2f8)', ['bg-purple-200/40','bg-pink-200/30','bg-violet-200/25']),
    wp('cotton-candy',      'Cotton Candy',       'pastel', 'bg-gradient-to-br from-pink-50 to-blue-50', 'linear-gradient(135deg,#fdf2f8,#eff6ff)', ['bg-pink-200/40','bg-blue-200/30','bg-violet-200/25']),
    wp('mint-sorbet',       'Mint Sorbet',        'pastel', 'bg-gradient-to-br from-emerald-50 to-teal-50', 'linear-gradient(135deg,#ecfdf5,#f0fdfa)', ['bg-emerald-200/40','bg-teal-200/30','bg-green-200/25']),
    wp('golden-hour',       'Golden Hour',        'pastel', 'bg-gradient-to-br from-yellow-50 to-amber-50', 'linear-gradient(135deg,#fefce8,#fffbeb)', ['bg-yellow-200/40','bg-amber-200/30','bg-orange-100/25']),
    wp('cherry-blossom',    'Cherry Blossom',     'pastel', 'bg-gradient-to-br from-pink-50 to-fuchsia-50', 'linear-gradient(135deg,#fdf2f8,#fdf4ff)', ['bg-pink-300/40','bg-fuchsia-200/30','bg-rose-200/25']),
    wp('sunset-glow',       'Sunset Glow',        'pastel', 'bg-gradient-to-br from-orange-50 to-rose-50', 'linear-gradient(135deg,#fff7ed,#fff1f2)', ['bg-orange-200/40','bg-rose-200/30','bg-amber-200/25']),
    wp('p-baby-blue',       'Baby Blue',          'pastel', 'bg-gradient-to-br from-sky-50 to-blue-50', 'linear-gradient(135deg,#f0f9ff,#eff6ff)', ['bg-sky-200/40','bg-blue-200/30','bg-cyan-100/25']),
    wp('p-rose-quartz',     'Rose Quartz',        'pastel', 'bg-gradient-to-br from-rose-50 to-pink-50', 'linear-gradient(135deg,#fff1f2,#fdf2f8)', ['bg-rose-200/40','bg-pink-200/30','bg-fuchsia-100/25']),
    wp('p-seafoam',         'Seafoam',            'pastel', 'bg-gradient-to-br from-teal-50 to-cyan-50', 'linear-gradient(135deg,#f0fdfa,#ecfeff)', ['bg-teal-200/40','bg-cyan-200/30','bg-emerald-100/25']),
    wp('p-buttercream',     'Buttercream',        'pastel', 'bg-gradient-to-br from-amber-50 to-yellow-50', 'linear-gradient(135deg,#fffbeb,#fefce8)', ['bg-amber-100/40','bg-yellow-100/30','bg-orange-100/25']),
    wp('p-periwinkle',      'Periwinkle',         'pastel', 'bg-gradient-to-br from-indigo-50 to-violet-50', 'linear-gradient(135deg,#eef2ff,#f5f3ff)', ['bg-indigo-200/40','bg-violet-200/30','bg-blue-200/25']),
    wp('p-apricot',         'Apricot Blush',      'pastel', 'bg-gradient-to-br from-orange-50 to-amber-50', 'linear-gradient(135deg,#fff7ed,#fffbeb)', ['bg-orange-200/40','bg-amber-100/30','bg-rose-100/25']),
    wp('p-lilac-haze',      'Lilac Haze',         'pastel', 'bg-gradient-to-br from-fuchsia-50 to-purple-50', 'linear-gradient(135deg,#fdf4ff,#faf5ff)', ['bg-fuchsia-200/40','bg-purple-200/30','bg-pink-200/25']),
    wp('p-pistachio',       'Pistachio',          'pastel', 'bg-gradient-to-br from-lime-50 to-green-50', 'linear-gradient(135deg,#f7fee7,#f0fdf4)', ['bg-lime-200/40','bg-green-200/30','bg-emerald-100/25']),
    wp('p-blush-pink',      'Blush Pink',         'pastel', 'bg-gradient-to-br from-pink-50 to-rose-50', 'linear-gradient(135deg,#fdf2f8,#fff1f2)', ['bg-pink-200/40','bg-rose-200/30','bg-fuchsia-100/25']),
    wp('p-powder-blue',     'Powder Blue',        'pastel', 'bg-gradient-to-br from-blue-50 to-sky-50', 'linear-gradient(135deg,#eff6ff,#f0f9ff)', ['bg-blue-200/40','bg-sky-200/30','bg-indigo-100/25']),
    wp('p-vanilla',         'Vanilla',            'pastel', 'bg-gradient-to-br from-yellow-50 to-stone-50', 'linear-gradient(135deg,#fefce8,#fafaf9)', ['bg-yellow-100/40','bg-stone-200/30','bg-amber-100/25']),
    wp('p-coral-reef',      'Coral Reef',         'pastel', 'bg-gradient-to-br from-red-50 to-orange-50', 'linear-gradient(135deg,#fef2f2,#fff7ed)', ['bg-red-200/35','bg-orange-200/30','bg-pink-100/25']),
    wp('p-melon',           'Melon',              'pastel', 'bg-gradient-to-br from-red-50 to-amber-50', 'linear-gradient(135deg,#fef2f2,#fffbeb)', ['bg-red-200/35','bg-amber-200/30','bg-orange-100/25']),
    wp('p-wisteria',        'Wisteria',           'pastel', 'bg-gradient-to-br from-violet-50 to-indigo-50', 'linear-gradient(135deg,#f5f3ff,#eef2ff)', ['bg-violet-200/40','bg-indigo-200/30','bg-purple-100/25']),
    wp('p-champagne',       'Champagne',          'pastel', 'bg-gradient-to-br from-amber-50 to-rose-50', 'linear-gradient(135deg,#fffbeb,#fff1f2)', ['bg-amber-200/35','bg-rose-200/30','bg-yellow-100/25']),
    wp('p-skylight',        'Skylight',           'pastel', 'bg-gradient-to-br from-cyan-50 to-sky-50', 'linear-gradient(135deg,#ecfeff,#f0f9ff)', ['bg-cyan-200/40','bg-sky-200/30','bg-blue-100/25']),
    wp('p-marshmallow',     'Marshmallow',        'pastel', 'bg-gradient-to-br from-slate-50 to-pink-50', 'linear-gradient(135deg,#f8fafc,#fdf2f8)', ['bg-slate-200/35','bg-pink-200/30','bg-gray-100/25']),
    wp('p-frosted-mint',    'Frosted Mint',       'pastel', 'bg-gradient-to-br from-green-50 to-teal-50', 'linear-gradient(135deg,#f0fdf4,#f0fdfa)', ['bg-green-200/40','bg-teal-200/30','bg-emerald-100/25']),
    wp('p-candy-floss',     'Candy Floss',        'pastel', 'bg-gradient-to-br from-fuchsia-50 to-rose-50', 'linear-gradient(135deg,#fdf4ff,#fff1f2)', ['bg-fuchsia-200/40','bg-rose-200/30','bg-pink-100/25']),
    wp('p-morning-dew',     'Morning Dew',        'pastel', 'bg-gradient-to-br from-emerald-50 to-cyan-50', 'linear-gradient(135deg,#ecfdf5,#ecfeff)', ['bg-emerald-200/40','bg-cyan-200/30','bg-green-100/25']),
    wp('p-mango-cream',     'Mango Cream',        'pastel', 'bg-gradient-to-br from-orange-50 to-yellow-50', 'linear-gradient(135deg,#fff7ed,#fefce8)', ['bg-orange-200/40','bg-yellow-200/30','bg-amber-100/25']),
    wp('p-cloud-puff',      'Cloud Puff',         'pastel', 'bg-gradient-to-br from-gray-50 to-blue-50', 'linear-gradient(135deg,#f9fafb,#eff6ff)', ['bg-gray-200/35','bg-blue-200/30','bg-slate-100/25']),
    wp('p-fairy-dust',      'Fairy Dust',         'pastel', 'bg-gradient-to-br from-violet-50 to-pink-50', 'linear-gradient(135deg,#f5f3ff,#fdf2f8)', ['bg-violet-200/40','bg-pink-200/30','bg-purple-100/25']),
    wp('p-lemon-chiffon',   'Lemon Chiffon',      'pastel', 'bg-gradient-to-br from-yellow-50 to-lime-50', 'linear-gradient(135deg,#fefce8,#f7fee7)', ['bg-yellow-200/40','bg-lime-200/30','bg-green-100/25']),
    wp('p-spring-rain',     'Spring Rain',        'pastel', 'bg-gradient-to-br from-teal-50 to-green-50', 'linear-gradient(135deg,#f0fdfa,#f0fdf4)', ['bg-teal-200/40','bg-green-200/30','bg-emerald-100/25']),
    wp('p-blossom-field',   'Blossom Field',      'pastel', 'bg-gradient-to-br from-rose-50 to-fuchsia-50', 'linear-gradient(135deg,#fff1f2,#fdf4ff)', ['bg-rose-200/40','bg-fuchsia-200/30','bg-pink-100/25']),
    wp('p-sorbet-sky',      'Sorbet Sky',         'pastel', 'bg-gradient-to-br from-pink-50 to-orange-50', 'linear-gradient(135deg,#fdf2f8,#fff7ed)', ['bg-pink-200/40','bg-orange-200/30','bg-rose-100/25']),
    wp('p-pearl-mist',      'Pearl Mist',         'pastel', 'bg-gradient-to-br from-stone-50 to-slate-50', 'linear-gradient(135deg,#fafaf9,#f8fafc)', ['bg-stone-200/35','bg-slate-200/30','bg-gray-100/25']),
    wp('p-tangerine-ice',   'Tangerine Ice',      'pastel', 'bg-gradient-to-br from-orange-50 to-red-50', 'linear-gradient(135deg,#fff7ed,#fef2f2)', ['bg-orange-200/40','bg-red-200/30','bg-amber-100/25']),
    wp('p-jasmine',         'Jasmine',            'pastel', 'bg-gradient-to-br from-yellow-50 to-green-50', 'linear-gradient(135deg,#fefce8,#f0fdf4)', ['bg-yellow-200/40','bg-green-200/30','bg-lime-100/25']),
    wp('p-dewberry',        'Dewberry',           'pastel', 'bg-gradient-to-br from-purple-50 to-blue-50', 'linear-gradient(135deg,#faf5ff,#eff6ff)', ['bg-purple-200/40','bg-blue-200/30','bg-indigo-100/25']),
    wp('p-honey-milk',      'Honey Milk',         'pastel', 'bg-gradient-to-br from-amber-50 to-stone-50', 'linear-gradient(135deg,#fffbeb,#fafaf9)', ['bg-amber-200/40','bg-stone-200/30','bg-yellow-100/25']),
    wp('p-petal-white',     'Petal White',        'pastel', 'bg-gradient-to-br from-white to-pink-50', 'linear-gradient(135deg,#ffffff,#fdf2f8)', ['bg-pink-100/35','bg-rose-100/25','bg-white/20']),

    // ══════════════════════════════════════════════════════════
    // ██  DARK  (41 wallpapers)
    // ══════════════════════════════════════════════════════════
    wp('midnight-abyss',    'Midnight Abyss',     'dark', 'bg-gradient-to-br from-gray-900 to-slate-900', 'linear-gradient(135deg,#111827,#0f172a)', ['bg-blue-900/30','bg-purple-900/25','bg-cyan-900/20']),
    wp('dark-ocean',        'Dark Ocean',         'dark', 'bg-gradient-to-br from-slate-900 to-blue-950', 'linear-gradient(135deg,#0f172a,#172554)', ['bg-blue-800/30','bg-slate-700/25','bg-indigo-900/20']),
    wp('charcoal-mist',     'Charcoal Mist',      'dark', 'bg-gradient-to-br from-zinc-800 to-neutral-900', 'linear-gradient(135deg,#27272a,#171717)', ['bg-zinc-600/25','bg-stone-700/20','bg-gray-600/15']),
    wp('obsidian-rose',     'Obsidian Rose',      'dark', 'bg-gradient-to-br from-gray-900 to-rose-950', 'linear-gradient(135deg,#111827,#4c0519)', ['bg-rose-900/30','bg-pink-900/25','bg-gray-800/20']),
    wp('shadow-forest',     'Shadow Forest',      'dark', 'bg-gradient-to-br from-gray-900 to-emerald-950', 'linear-gradient(135deg,#111827,#022c22)', ['bg-emerald-900/30','bg-green-900/25','bg-teal-900/20']),
    wp('deep-violet',       'Deep Violet',        'dark', 'bg-gradient-to-br from-gray-900 to-violet-950', 'linear-gradient(135deg,#111827,#2e1065)', ['bg-violet-900/30','bg-purple-800/25','bg-indigo-900/20']),
    wp('dark-amber',        'Dark Amber',         'dark', 'bg-gradient-to-br from-stone-900 to-amber-950', 'linear-gradient(135deg,#1c1917,#451a03)', ['bg-amber-900/30','bg-orange-900/25','bg-stone-700/20']),
    wp('d-onyx',            'Onyx',               'dark', 'bg-gradient-to-br from-neutral-900 to-neutral-950', 'linear-gradient(135deg,#171717,#0a0a0a)', ['bg-neutral-700/25','bg-gray-800/20','bg-zinc-900/15']),
    wp('d-raven',           'Raven Wing',         'dark', 'bg-gradient-to-br from-gray-900 to-gray-950', 'linear-gradient(135deg,#111827,#030712)', ['bg-gray-700/25','bg-slate-800/20','bg-zinc-800/15']),
    wp('d-obsidian',        'Obsidian',           'dark', 'bg-gradient-to-br from-zinc-900 to-stone-950', 'linear-gradient(135deg,#18181b,#0c0a09)', ['bg-zinc-700/25','bg-stone-800/20','bg-gray-900/15']),
    wp('d-dark-cherry',     'Dark Cherry',        'dark', 'bg-gradient-to-br from-red-950 to-gray-950', 'linear-gradient(135deg,#450a0a,#030712)', ['bg-red-800/25','bg-rose-900/20','bg-gray-800/15']),
    wp('d-navy-depths',     'Navy Depths',        'dark', 'bg-gradient-to-br from-blue-950 to-indigo-950', 'linear-gradient(135deg,#172554,#1e1b4b)', ['bg-blue-900/25','bg-indigo-900/20','bg-slate-800/15']),
    wp('d-dark-teal',       'Dark Teal',          'dark', 'bg-gradient-to-br from-teal-950 to-cyan-950', 'linear-gradient(135deg,#042f2e,#083344)', ['bg-teal-800/25','bg-cyan-900/20','bg-emerald-900/15']),
    wp('d-wine-cellar',     'Wine Cellar',        'dark', 'bg-gradient-to-br from-rose-950 to-purple-950', 'linear-gradient(135deg,#4c0519,#3b0764)', ['bg-rose-800/25','bg-purple-900/20','bg-pink-900/15']),
    wp('d-graphite',        'Graphite',           'dark', 'bg-gradient-to-br from-gray-800 to-gray-900', 'linear-gradient(135deg,#1f2937,#111827)', ['bg-gray-600/25','bg-slate-700/20','bg-zinc-700/15']),
    wp('d-black-pearl',     'Black Pearl',        'dark', 'bg-gradient-to-br from-slate-950 to-gray-950', 'linear-gradient(135deg,#020617,#030712)', ['bg-slate-700/20','bg-blue-900/15','bg-gray-800/10']),
    wp('d-dark-sage',       'Dark Sage',          'dark', 'bg-gradient-to-br from-green-950 to-gray-900', 'linear-gradient(135deg,#052e16,#111827)', ['bg-green-800/25','bg-emerald-900/20','bg-gray-700/15']),
    wp('d-twilight-noir',   'Twilight Noir',      'dark', 'bg-gradient-to-br from-indigo-950 to-slate-950', 'linear-gradient(135deg,#1e1b4b,#020617)', ['bg-indigo-800/25','bg-slate-800/20','bg-violet-900/15']),
    wp('d-dark-plum',       'Dark Plum',          'dark', 'bg-gradient-to-br from-purple-950 to-fuchsia-950', 'linear-gradient(135deg,#3b0764,#4a044e)', ['bg-purple-800/25','bg-fuchsia-900/20','bg-violet-900/15']),
    wp('d-cocoa',           'Cocoa',              'dark', 'bg-gradient-to-br from-stone-900 to-red-950', 'linear-gradient(135deg,#1c1917,#450a0a)', ['bg-stone-700/25','bg-red-900/20','bg-amber-900/15']),
    wp('d-iron',            'Iron',               'dark', 'bg-gradient-to-br from-gray-800 to-slate-900', 'linear-gradient(135deg,#1f2937,#0f172a)', ['bg-gray-600/25','bg-slate-700/20','bg-blue-900/15']),
    wp('d-void',            'Void',               'dark', 'bg-gradient-to-br from-gray-950 to-black', 'linear-gradient(135deg,#030712,#000000)', ['bg-gray-800/20','bg-slate-900/15','bg-neutral-900/10']),
    wp('d-dark-bronze',     'Dark Bronze',        'dark', 'bg-gradient-to-br from-amber-950 to-stone-900', 'linear-gradient(135deg,#451a03,#1c1917)', ['bg-amber-800/25','bg-stone-700/20','bg-orange-900/15']),
    wp('d-night-sky',       'Night Sky',          'dark', 'bg-gradient-to-br from-indigo-950 to-blue-950', 'linear-gradient(135deg,#1e1b4b,#172554)', ['bg-indigo-800/20','bg-blue-800/15','bg-violet-900/10']),
    wp('d-dark-moss',       'Dark Moss',          'dark', 'bg-gradient-to-br from-emerald-950 to-green-950', 'linear-gradient(135deg,#022c22,#052e16)', ['bg-emerald-800/25','bg-green-900/20','bg-teal-900/15']),
    wp('d-slate-storm',     'Slate Storm',        'dark', 'bg-gradient-to-br from-slate-800 to-gray-900', 'linear-gradient(135deg,#1e293b,#111827)', ['bg-slate-600/25','bg-gray-700/20','bg-blue-900/15']),
    wp('d-volcanic-ash',    'Volcanic Ash',       'dark', 'bg-gradient-to-br from-zinc-900 to-red-950', 'linear-gradient(135deg,#18181b,#450a0a)', ['bg-zinc-700/25','bg-red-900/20','bg-orange-900/15']),
    wp('d-dark-coral',      'Dark Coral',         'dark', 'bg-gradient-to-br from-orange-950 to-red-950', 'linear-gradient(135deg,#431407,#450a0a)', ['bg-orange-900/25','bg-red-900/20','bg-amber-900/15']),
    wp('d-phantom',         'Phantom',            'dark', 'bg-gradient-to-br from-gray-900 to-purple-950', 'linear-gradient(135deg,#111827,#3b0764)', ['bg-gray-700/25','bg-purple-900/20','bg-violet-900/15']),
    wp('d-dark-steel',      'Dark Steel',         'dark', 'bg-gradient-to-br from-slate-800 to-zinc-900', 'linear-gradient(135deg,#1e293b,#18181b)', ['bg-slate-600/25','bg-zinc-700/20','bg-gray-700/15']),
    wp('d-midnight-blue',   'Midnight Blue',      'dark', 'bg-gradient-to-br from-blue-950 to-slate-950', 'linear-gradient(135deg,#172554,#020617)', ['bg-blue-800/25','bg-slate-800/20','bg-indigo-900/15']),
    wp('d-eclipse',         'Eclipse',            'dark', 'bg-gradient-to-br from-gray-950 to-amber-950', 'linear-gradient(135deg,#030712,#451a03)', ['bg-gray-800/20','bg-amber-900/15','bg-stone-800/10']),
    wp('d-ebony',           'Ebony',              'dark', 'bg-gradient-to-br from-neutral-950 to-zinc-900', 'linear-gradient(135deg,#0a0a0a,#18181b)', ['bg-neutral-800/20','bg-zinc-800/15','bg-gray-900/10']),
    wp('d-dark-ocean-2',    'Abyss',              'dark', 'bg-gradient-to-br from-cyan-950 to-blue-950', 'linear-gradient(135deg,#083344,#172554)', ['bg-cyan-800/25','bg-blue-900/20','bg-teal-900/15']),
    wp('d-panther',         'Panther',            'dark', 'bg-gradient-to-br from-gray-900 to-zinc-950', 'linear-gradient(135deg,#111827,#09090b)', ['bg-gray-700/20','bg-zinc-800/15','bg-slate-900/10']),
    wp('d-dark-ruby',       'Dark Ruby',          'dark', 'bg-gradient-to-br from-red-950 to-rose-950', 'linear-gradient(135deg,#450a0a,#4c0519)', ['bg-red-800/25','bg-rose-900/20','bg-pink-900/15']),
    wp('d-charcoal-blue',   'Charcoal Blue',      'dark', 'bg-gradient-to-br from-slate-900 to-sky-950', 'linear-gradient(135deg,#0f172a,#082f49)', ['bg-slate-700/25','bg-sky-900/20','bg-blue-900/15']),
    wp('d-dark-lavender',   'Dark Lavender',      'dark', 'bg-gradient-to-br from-violet-950 to-gray-900', 'linear-gradient(135deg,#2e1065,#111827)', ['bg-violet-800/25','bg-gray-700/20','bg-purple-900/15']),
    wp('d-shadow',          'Shadow',             'dark', 'bg-gradient-to-br from-neutral-900 to-gray-950', 'linear-gradient(135deg,#171717,#030712)', ['bg-neutral-700/20','bg-gray-800/15','bg-zinc-900/10']),
    wp('d-thundercloud',    'Thundercloud',       'dark', 'bg-gradient-to-br from-gray-800 to-indigo-950', 'linear-gradient(135deg,#1f2937,#1e1b4b)', ['bg-gray-600/25','bg-indigo-800/20','bg-slate-700/15']),
    wp('d-dark-mint',       'Dark Mint',          'dark', 'bg-gradient-to-br from-emerald-950 to-teal-950', 'linear-gradient(135deg,#022c22,#042f2e)', ['bg-emerald-800/25','bg-teal-800/20','bg-green-900/15']),

    // ══════════════════════════════════════════════════════════
    // ██  GAMING  (41 wallpapers)
    // ══════════════════════════════════════════════════════════
    wp('neon-cyber',        'Neon Cyber',         'gaming', 'bg-gradient-to-br from-violet-900 to-fuchsia-900', 'linear-gradient(135deg,#4c1d95,#701a75)', ['bg-fuchsia-500/30','bg-cyan-500/25','bg-violet-500/20']),
    wp('toxic-green',       'Toxic Matrix',       'gaming', 'bg-gradient-to-br from-gray-950 to-green-950', 'linear-gradient(135deg,#030712,#052e16)', ['bg-green-500/25','bg-lime-500/20','bg-emerald-500/15']),
    wp('fire-storm',        'Fire Storm',         'gaming', 'bg-gradient-to-br from-red-900 to-orange-900', 'linear-gradient(135deg,#7f1d1d,#7c2d12)', ['bg-red-500/30','bg-orange-500/25','bg-yellow-500/20']),
    wp('electric-blue',     'Electric Blue',      'gaming', 'bg-gradient-to-br from-blue-900 to-cyan-900', 'linear-gradient(135deg,#1e3a8a,#164e63)', ['bg-cyan-400/30','bg-blue-400/25','bg-sky-500/20']),
    wp('arcade-purple',     'Arcade Night',       'gaming', 'bg-gradient-to-br from-purple-900 to-pink-900', 'linear-gradient(135deg,#581c87,#831843)', ['bg-pink-500/30','bg-purple-400/25','bg-fuchsia-500/20']),
    wp('dragon-gold',       'Dragon Gold',        'gaming', 'bg-gradient-to-br from-amber-900 to-red-950', 'linear-gradient(135deg,#78350f,#450a0a)', ['bg-amber-500/30','bg-yellow-400/25','bg-red-500/20']),
    wp('g-plasma',          'Plasma',             'gaming', 'bg-gradient-to-br from-fuchsia-900 to-cyan-900', 'linear-gradient(135deg,#701a75,#164e63)', ['bg-fuchsia-500/30','bg-cyan-400/25','bg-purple-500/20']),
    wp('g-venom',           'Venom',              'gaming', 'bg-gradient-to-br from-green-900 to-gray-950', 'linear-gradient(135deg,#14532d,#030712)', ['bg-green-500/25','bg-lime-400/20','bg-emerald-600/15']),
    wp('g-crimson-tide',    'Crimson Tide',       'gaming', 'bg-gradient-to-br from-red-900 to-rose-950', 'linear-gradient(135deg,#7f1d1d,#4c0519)', ['bg-red-500/30','bg-rose-500/25','bg-pink-500/20']),
    wp('g-thunder',         'Thunder',            'gaming', 'bg-gradient-to-br from-yellow-700 to-gray-900', 'linear-gradient(135deg,#a16207,#111827)', ['bg-yellow-400/30','bg-amber-500/25','bg-gray-700/20']),
    wp('g-ice-shard',       'Ice Shard',          'gaming', 'bg-gradient-to-br from-cyan-800 to-blue-950', 'linear-gradient(135deg,#155e75,#172554)', ['bg-cyan-400/30','bg-blue-400/25','bg-sky-400/20']),
    wp('g-magma',           'Magma',              'gaming', 'bg-gradient-to-br from-orange-900 to-red-900', 'linear-gradient(135deg,#7c2d12,#7f1d1d)', ['bg-orange-500/30','bg-red-500/25','bg-yellow-500/20']),
    wp('g-shadow-blade',    'Shadow Blade',       'gaming', 'bg-gradient-to-br from-gray-950 to-violet-950', 'linear-gradient(135deg,#030712,#2e1065)', ['bg-gray-700/25','bg-violet-500/20','bg-purple-600/15']),
    wp('g-supernova',       'Supernova',          'gaming', 'bg-gradient-to-br from-pink-900 to-orange-900', 'linear-gradient(135deg,#831843,#7c2d12)', ['bg-pink-500/30','bg-orange-400/25','bg-yellow-400/20']),
    wp('g-poison',          'Poison',             'gaming', 'bg-gradient-to-br from-purple-950 to-green-950', 'linear-gradient(135deg,#3b0764,#052e16)', ['bg-purple-500/25','bg-green-500/20','bg-emerald-500/15']),
    wp('g-laser-red',       'Laser Red',          'gaming', 'bg-gradient-to-br from-red-800 to-pink-900', 'linear-gradient(135deg,#991b1b,#831843)', ['bg-red-500/30','bg-pink-400/25','bg-rose-500/20']),
    wp('g-storm-cloud',     'Storm Cloud',        'gaming', 'bg-gradient-to-br from-slate-800 to-blue-900', 'linear-gradient(135deg,#1e293b,#1e3a8a)', ['bg-slate-500/25','bg-blue-500/20','bg-indigo-500/15']),
    wp('g-neon-pink',       'Neon Pink',          'gaming', 'bg-gradient-to-br from-pink-800 to-fuchsia-900', 'linear-gradient(135deg,#9d174d,#701a75)', ['bg-pink-500/30','bg-fuchsia-400/25','bg-rose-500/20']),
    wp('g-dark-knight',     'Dark Knight',        'gaming', 'bg-gradient-to-br from-gray-900 to-blue-900', 'linear-gradient(135deg,#111827,#1e3a8a)', ['bg-gray-700/25','bg-blue-500/20','bg-slate-600/15']),
    wp('g-warzone',         'Warzone',            'gaming', 'bg-gradient-to-br from-stone-800 to-red-900', 'linear-gradient(135deg,#292524,#7f1d1d)', ['bg-stone-600/25','bg-red-500/20','bg-orange-600/15']),
    wp('g-frost-bite',      'Frost Bite',         'gaming', 'bg-gradient-to-br from-blue-800 to-cyan-800', 'linear-gradient(135deg,#1e40af,#155e75)', ['bg-blue-400/30','bg-cyan-400/25','bg-sky-400/20']),
    wp('g-toxic-waste',     'Toxic Waste',        'gaming', 'bg-gradient-to-br from-lime-800 to-green-950', 'linear-gradient(135deg,#3f6212,#052e16)', ['bg-lime-500/25','bg-green-500/20','bg-yellow-400/15']),
    wp('g-inferno',         'Inferno',            'gaming', 'bg-gradient-to-br from-red-800 to-amber-900', 'linear-gradient(135deg,#991b1b,#78350f)', ['bg-red-500/30','bg-amber-500/25','bg-orange-400/20']),
    wp('g-galaxy',          'Galaxy',             'gaming', 'bg-gradient-to-br from-indigo-900 to-purple-900', 'linear-gradient(135deg,#312e81,#581c87)', ['bg-indigo-500/25','bg-purple-500/20','bg-violet-400/15']),
    wp('g-radioactive',     'Radioactive',        'gaming', 'bg-gradient-to-br from-yellow-800 to-green-900', 'linear-gradient(135deg,#854d0e,#14532d)', ['bg-yellow-500/25','bg-green-400/20','bg-lime-500/15']),
    wp('g-phantom-red',     'Phantom Red',        'gaming', 'bg-gradient-to-br from-red-950 to-gray-950', 'linear-gradient(135deg,#450a0a,#030712)', ['bg-red-600/25','bg-gray-700/20','bg-rose-800/15']),
    wp('g-aqua-strike',     'Aqua Strike',        'gaming', 'bg-gradient-to-br from-teal-800 to-cyan-900', 'linear-gradient(135deg,#115e59,#164e63)', ['bg-teal-400/30','bg-cyan-400/25','bg-emerald-400/20']),
    wp('g-molten-core',     'Molten Core',        'gaming', 'bg-gradient-to-br from-amber-800 to-red-900', 'linear-gradient(135deg,#92400e,#7f1d1d)', ['bg-amber-500/30','bg-red-400/25','bg-orange-500/20']),
    wp('g-stealth',         'Stealth',            'gaming', 'bg-gradient-to-br from-gray-900 to-green-900', 'linear-gradient(135deg,#111827,#14532d)', ['bg-gray-700/25','bg-green-600/20','bg-emerald-700/15']),
    wp('g-neon-sunset',     'Neon Sunset',        'gaming', 'bg-gradient-to-br from-orange-800 to-purple-900', 'linear-gradient(135deg,#9a3412,#581c87)', ['bg-orange-500/30','bg-purple-400/25','bg-pink-500/20']),
    wp('g-goblin',          'Goblin',             'gaming', 'bg-gradient-to-br from-green-800 to-lime-900', 'linear-gradient(135deg,#166534,#365314)', ['bg-green-500/25','bg-lime-400/20','bg-emerald-500/15']),
    wp('g-ultraviolet',     'Ultraviolet',        'gaming', 'bg-gradient-to-br from-violet-800 to-indigo-900', 'linear-gradient(135deg,#5b21b6,#312e81)', ['bg-violet-500/30','bg-indigo-400/25','bg-purple-500/20']),
    wp('g-blaze',           'Blaze',              'gaming', 'bg-gradient-to-br from-orange-700 to-yellow-800', 'linear-gradient(135deg,#c2410c,#854d0e)', ['bg-orange-500/30','bg-yellow-400/25','bg-amber-400/20']),
    wp('g-hyperdrive',      'Hyperdrive',         'gaming', 'bg-gradient-to-br from-blue-900 to-violet-900', 'linear-gradient(135deg,#1e3a8a,#4c1d95)', ['bg-blue-500/30','bg-violet-400/25','bg-indigo-500/20']),
    wp('g-bloodmoon',       'Blood Moon',         'gaming', 'bg-gradient-to-br from-red-900 to-gray-900', 'linear-gradient(135deg,#7f1d1d,#111827)', ['bg-red-500/25','bg-gray-600/20','bg-rose-700/15']),
    wp('g-aurora-borealis', 'Aurora Borealis',    'gaming', 'bg-gradient-to-br from-green-800 to-blue-900', 'linear-gradient(135deg,#166534,#1e3a8a)', ['bg-green-500/25','bg-blue-400/20','bg-cyan-400/15']),
    wp('g-pixel-wave',      'Pixel Wave',         'gaming', 'bg-gradient-to-br from-cyan-700 to-purple-800', 'linear-gradient(135deg,#0e7490,#6b21a8)', ['bg-cyan-400/30','bg-purple-500/25','bg-blue-400/20']),
    wp('g-warp-speed',      'Warp Speed',         'gaming', 'bg-gradient-to-br from-indigo-800 to-cyan-900', 'linear-gradient(135deg,#3730a3,#164e63)', ['bg-indigo-400/30','bg-cyan-400/25','bg-blue-500/20']),
    wp('g-rage-quit',       'Rage Quit',          'gaming', 'bg-gradient-to-br from-red-800 to-orange-800', 'linear-gradient(135deg,#991b1b,#9a3412)', ['bg-red-500/30','bg-orange-400/25','bg-amber-500/20']),
    wp('g-ender',           'Ender',              'gaming', 'bg-gradient-to-br from-purple-900 to-gray-950', 'linear-gradient(135deg,#581c87,#030712)', ['bg-purple-500/25','bg-gray-700/20','bg-violet-600/15']),
    wp('g-dark-energy',     'Dark Energy',        'gaming', 'bg-gradient-to-br from-indigo-950 to-fuchsia-950', 'linear-gradient(135deg,#1e1b4b,#4a044e)', ['bg-indigo-500/25','bg-fuchsia-500/20','bg-violet-600/15']),

    // ══════════════════════════════════════════════════════════
    // ██  AESTHETIC  (41 wallpapers) — uses image backgrounds
    // ══════════════════════════════════════════════════════════
    wp('a-soft-glow',       'Soft Glow',          'aesthetic', 'bg-gradient-to-br from-rose-50 to-amber-50', 'linear-gradient(135deg,#fff1f2,#fffbeb)', ['bg-rose-200/40','bg-amber-200/30','bg-pink-200/25'], 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'),
    wp('a-arctic-aurora',   'Arctic Aurora',      'aesthetic', 'bg-gradient-to-br from-cyan-50 to-green-50', 'linear-gradient(135deg,#ecfeff,#f0fdf4)', ['bg-cyan-200/40','bg-green-200/30','bg-teal-200/25'], 'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=400&h=300&fit=crop'),
    wp('a-dreamy-lilac',    'Dreamy Lilac',       'aesthetic', 'bg-gradient-to-br from-violet-100 to-pink-100', 'linear-gradient(135deg,#ede9fe,#fce7f3)', ['bg-violet-300/35','bg-pink-300/30','bg-purple-200/25'], 'https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=400&h=300&fit=crop'),
    wp('a-cloud-nine',      'Cloud Nine',         'aesthetic', 'bg-gradient-to-br from-sky-50 to-indigo-50', 'linear-gradient(135deg,#f0f9ff,#eef2ff)', ['bg-sky-200/40','bg-indigo-200/30','bg-blue-100/25'], 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=400&h=300&fit=crop'),
    wp('a-vintage-rose',    'Vintage Rose',       'aesthetic', 'bg-gradient-to-br from-rose-100 to-stone-100', 'linear-gradient(135deg,#ffe4e6,#f5f5f4)', ['bg-rose-300/35','bg-stone-200/30','bg-pink-200/25'], 'https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=400&h=300&fit=crop&q=80'),
    wp('a-sage-garden',     'Sage Garden',        'aesthetic', 'bg-gradient-to-br from-emerald-50 to-lime-50', 'linear-gradient(135deg,#ecfdf5,#f7fee7)', ['bg-emerald-200/35','bg-lime-200/30','bg-green-200/25'], 'https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400&h=300&fit=crop'),
    wp('a-honey-butter',    'Honey Butter',       'aesthetic', 'bg-gradient-to-br from-amber-50 to-yellow-50', 'linear-gradient(135deg,#fffbeb,#fefce8)', ['bg-amber-200/40','bg-yellow-200/30','bg-orange-100/25'], 'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=400&h=300&fit=crop'),
    wp('a-twilight-mist',   'Twilight Mist',      'aesthetic', 'bg-gradient-to-br from-slate-100 to-violet-100', 'linear-gradient(135deg,#f1f5f9,#ede9fe)', ['bg-slate-200/35','bg-violet-200/30','bg-indigo-200/25'], 'https://images.unsplash.com/photo-1472120435266-95a3675c6041?w=400&h=300&fit=crop'),
    wp('a-cherry-café',     'Cherry Café',        'aesthetic', 'bg-gradient-to-br from-rose-100 to-amber-100', 'linear-gradient(135deg,#ffe4e6,#fef3c7)', ['bg-rose-200/35','bg-amber-200/30','bg-pink-100/25'], 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop'),
    wp('a-beach-sunset',    'Beach Sunset',       'aesthetic', 'bg-gradient-to-br from-orange-100 to-pink-100', 'linear-gradient(135deg,#ffedd5,#fce7f3)', ['bg-orange-200/35','bg-pink-200/30','bg-amber-200/25'], 'https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=400&h=300&fit=crop'),
    wp('a-rainy-window',    'Rainy Window',       'aesthetic', 'bg-gradient-to-br from-slate-100 to-blue-100', 'linear-gradient(135deg,#f1f5f9,#dbeafe)', ['bg-slate-200/35','bg-blue-200/30','bg-gray-200/25'], 'https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=400&h=300&fit=crop'),
    wp('a-pink-sky',        'Pink Sky',           'aesthetic', 'bg-gradient-to-br from-pink-100 to-purple-100', 'linear-gradient(135deg,#fce7f3,#f3e8ff)', ['bg-pink-200/35','bg-purple-200/30','bg-rose-200/25'], 'https://images.unsplash.com/photo-1517483000871-1dbf64a6e1c6?w=400&h=300&fit=crop'),
    wp('a-forest-path',     'Forest Path',        'aesthetic', 'bg-gradient-to-br from-green-100 to-emerald-100', 'linear-gradient(135deg,#dcfce7,#d1fae5)', ['bg-green-200/35','bg-emerald-200/30','bg-teal-100/25'], 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop'),
    wp('a-starry-night',    'Starry Night',       'aesthetic', 'bg-gradient-to-br from-indigo-100 to-blue-100', 'linear-gradient(135deg,#e0e7ff,#dbeafe)', ['bg-indigo-200/35','bg-blue-200/30','bg-violet-100/25'], 'https://images.unsplash.com/photo-1475274047050-1d0c55b4b33e?w=400&h=300&fit=crop'),
    wp('a-ocean-waves',     'Ocean Waves',        'aesthetic', 'bg-gradient-to-br from-cyan-100 to-blue-100', 'linear-gradient(135deg,#cffafe,#dbeafe)', ['bg-cyan-200/35','bg-blue-200/30','bg-sky-100/25'], 'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=400&h=300&fit=crop'),
    wp('a-misty-mountain',  'Misty Mountain',     'aesthetic', 'bg-gradient-to-br from-gray-100 to-blue-100', 'linear-gradient(135deg,#f3f4f6,#dbeafe)', ['bg-gray-200/35','bg-blue-200/30','bg-slate-100/25'], 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop'),
    wp('a-cherry-blossom',  'Cherry Blossom Tree', 'aesthetic', 'bg-gradient-to-br from-pink-100 to-rose-100', 'linear-gradient(135deg,#fce7f3,#ffe4e6)', ['bg-pink-200/35','bg-rose-200/30','bg-fuchsia-100/25'], 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=400&h=300&fit=crop'),
    wp('a-cozy-library',    'Cozy Library',       'aesthetic', 'bg-gradient-to-br from-amber-100 to-stone-100', 'linear-gradient(135deg,#fef3c7,#f5f5f4)', ['bg-amber-200/35','bg-stone-200/30','bg-yellow-100/25'], 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=400&h=300&fit=crop'),
    wp('a-moonlight',       'Moonlight',          'aesthetic', 'bg-gradient-to-br from-slate-100 to-gray-100', 'linear-gradient(135deg,#f1f5f9,#f3f4f6)', ['bg-slate-200/35','bg-gray-200/30','bg-blue-100/25'], 'https://images.unsplash.com/photo-1532767153582-b1a0e5145009?w=400&h=300&fit=crop'),
    wp('a-autumn-leaves',   'Autumn Leaves',      'aesthetic', 'bg-gradient-to-br from-orange-100 to-red-100', 'linear-gradient(135deg,#ffedd5,#fee2e2)', ['bg-orange-200/35','bg-red-200/30','bg-amber-200/25'], 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop'),
    wp('a-flower-field',    'Flower Field',       'aesthetic', 'bg-gradient-to-br from-purple-100 to-pink-100', 'linear-gradient(135deg,#f3e8ff,#fce7f3)', ['bg-purple-200/35','bg-pink-200/30','bg-violet-100/25'], 'https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=400&h=300&fit=crop&sat=-30'),
    wp('a-snow-cabin',      'Snow Cabin',         'aesthetic', 'bg-gradient-to-br from-blue-50 to-slate-100', 'linear-gradient(135deg,#eff6ff,#f1f5f9)', ['bg-blue-200/35','bg-slate-200/30','bg-gray-100/25'], 'https://images.unsplash.com/photo-1482192505345-5655af888cc4?w=400&h=300&fit=crop'),
    wp('a-golden-field',    'Golden Field',       'aesthetic', 'bg-gradient-to-br from-yellow-100 to-amber-100', 'linear-gradient(135deg,#fef9c3,#fef3c7)', ['bg-yellow-200/35','bg-amber-200/30','bg-orange-100/25'], 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop'),
    wp('a-waterlily',       'Water Lily',         'aesthetic', 'bg-gradient-to-br from-green-50 to-cyan-50', 'linear-gradient(135deg,#f0fdf4,#ecfeff)', ['bg-green-200/35','bg-cyan-200/30','bg-teal-100/25'], 'https://images.unsplash.com/photo-1474557157379-8aa74a6ef541?w=400&h=300&fit=crop'),
    wp('a-cottagecore',     'Cottagecore',        'aesthetic', 'bg-gradient-to-br from-amber-50 to-green-50', 'linear-gradient(135deg,#fffbeb,#f0fdf4)', ['bg-amber-200/35','bg-green-200/30','bg-stone-100/25'], 'https://images.unsplash.com/photo-1416339306562-f3d12fefd36f?w=400&h=300&fit=crop'),
    wp('a-fairy-lights',    'Fairy Lights',       'aesthetic', 'bg-gradient-to-br from-amber-100 to-pink-100', 'linear-gradient(135deg,#fef3c7,#fce7f3)', ['bg-amber-200/35','bg-pink-200/30','bg-yellow-100/25'], 'https://images.unsplash.com/photo-1513151233558-d860c5398176?w=400&h=300&fit=crop'),
    wp('a-sunflowers',      'Sunflowers',         'aesthetic', 'bg-gradient-to-br from-yellow-100 to-green-100', 'linear-gradient(135deg,#fef9c3,#dcfce7)', ['bg-yellow-200/35','bg-green-200/30','bg-amber-100/25'], 'https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400&h=300&fit=crop'),
    wp('a-purple-haze',     'Purple Haze',        'aesthetic', 'bg-gradient-to-br from-violet-100 to-fuchsia-100', 'linear-gradient(135deg,#ede9fe,#fae8ff)', ['bg-violet-200/35','bg-fuchsia-200/30','bg-purple-100/25'], 'https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=400&h=300&fit=crop&sat=-10'),
    wp('a-zen-stones',      'Zen Stones',         'aesthetic', 'bg-gradient-to-br from-stone-100 to-gray-100', 'linear-gradient(135deg,#f5f5f4,#f3f4f6)', ['bg-stone-200/35','bg-gray-200/30','bg-slate-100/25'], 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=300&fit=crop'),
    wp('a-palm-trees',      'Palm Trees',         'aesthetic', 'bg-gradient-to-br from-sky-100 to-green-100', 'linear-gradient(135deg,#e0f2fe,#dcfce7)', ['bg-sky-200/35','bg-green-200/30','bg-cyan-100/25'], 'https://images.unsplash.com/photo-1509023464722-18d996393ca8?w=400&h=300&fit=crop'),
    wp('a-candle-glow',     'Candle Glow',        'aesthetic', 'bg-gradient-to-br from-amber-100 to-orange-100', 'linear-gradient(135deg,#fef3c7,#ffedd5)', ['bg-amber-200/35','bg-orange-200/30','bg-yellow-100/25'], 'https://images.unsplash.com/photo-1602523961358-f9f03dd557f4?w=400&h=300&fit=crop'),
    wp('a-coral-reef',      'Coral Reef',         'aesthetic', 'bg-gradient-to-br from-cyan-100 to-teal-100', 'linear-gradient(135deg,#cffafe,#ccfbf1)', ['bg-cyan-200/35','bg-teal-200/30','bg-blue-100/25'], 'https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=400&h=300&fit=crop'),
    wp('a-morning-coffee',  'Morning Coffee',     'aesthetic', 'bg-gradient-to-br from-stone-100 to-amber-100', 'linear-gradient(135deg,#f5f5f4,#fef3c7)', ['bg-stone-200/35','bg-amber-200/30','bg-brown-100/25'], 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=300&fit=crop'),
    wp('a-sakura',          'Sakura',             'aesthetic', 'bg-gradient-to-br from-pink-50 to-white', 'linear-gradient(135deg,#fdf2f8,#ffffff)', ['bg-pink-200/35','bg-rose-100/30','bg-white/25'], 'https://images.unsplash.com/photo-1522383225653-ed111181a951?w=400&h=300&fit=crop&q=90'),
    wp('a-lake-reflection',  'Lake Reflection',   'aesthetic', 'bg-gradient-to-br from-blue-100 to-green-100', 'linear-gradient(135deg,#dbeafe,#dcfce7)', ['bg-blue-200/35','bg-green-200/30','bg-cyan-100/25'], 'https://images.unsplash.com/photo-1439853949127-fa647821eba0?w=400&h=300&fit=crop'),
    wp('a-vintage-film',    'Vintage Film',       'aesthetic', 'bg-gradient-to-br from-amber-100 to-rose-100', 'linear-gradient(135deg,#fef3c7,#ffe4e6)', ['bg-amber-200/35','bg-rose-200/30','bg-stone-100/25'], 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=400&h=300&fit=crop'),
    wp('a-japanese-garden', 'Japanese Garden',    'aesthetic', 'bg-gradient-to-br from-green-100 to-stone-100', 'linear-gradient(135deg,#dcfce7,#f5f5f4)', ['bg-green-200/35','bg-stone-200/30','bg-emerald-100/25'], 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&h=300&fit=crop'),
    wp('a-wildflowers',     'Wildflowers',        'aesthetic', 'bg-gradient-to-br from-pink-100 to-yellow-100', 'linear-gradient(135deg,#fce7f3,#fef9c3)', ['bg-pink-200/35','bg-yellow-200/30','bg-green-100/25'], 'https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=400&h=300&fit=crop&q=70'),
    wp('a-bookshelf',       'Bookshelf',          'aesthetic', 'bg-gradient-to-br from-amber-100 to-stone-100', 'linear-gradient(135deg,#fef3c7,#f5f5f4)', ['bg-amber-200/35','bg-stone-200/30','bg-yellow-100/25'], 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=300&fit=crop'),
    wp('a-neon-city',       'Neon City',          'aesthetic', 'bg-gradient-to-br from-purple-100 to-blue-100', 'linear-gradient(135deg,#f3e8ff,#dbeafe)', ['bg-purple-200/35','bg-blue-200/30','bg-indigo-100/25'], 'https://images.unsplash.com/photo-1514565131-fce0801e5785?w=400&h=300&fit=crop'),
    wp('a-crystal-cave',    'Crystal Cave',       'aesthetic', 'bg-gradient-to-br from-cyan-100 to-violet-100', 'linear-gradient(135deg,#cffafe,#ede9fe)', ['bg-cyan-200/35','bg-violet-200/30','bg-blue-100/25'], 'https://images.unsplash.com/photo-1504198453319-5ce911bafcde?w=400&h=300&fit=crop'),
];

type WallpaperCategory = 'all' | 'pastel' | 'dark' | 'gaming' | 'aesthetic';

const CATEGORY_CONFIG: Record<WallpaperCategory, { label: string; icon: React.ReactNode; color: string }> = {
    all:       { label: 'All',       icon: <Palette   className="w-3.5 h-3.5" />, color: 'bg-gray-800 text-white' },
    pastel:    { label: 'Pastel',    icon: <Sun        className="w-3.5 h-3.5" />, color: 'bg-pink-100 text-pink-700 border border-pink-200' },
    dark:      { label: 'Dark',      icon: <Moon       className="w-3.5 h-3.5" />, color: 'bg-gray-800 text-gray-100 border border-gray-600' },
    gaming:    { label: 'Gaming',    icon: <Gamepad2   className="w-3.5 h-3.5" />, color: 'bg-purple-100 text-purple-700 border border-purple-200' },
    aesthetic: { label: 'Aesthetic', icon: <ImageIcon  className="w-3.5 h-3.5" />, color: 'bg-rose-100 text-rose-700 border border-rose-200' },
};

interface WallpaperSettingsProps {
    currentWallpaper: string;
    onWallpaperChange: (wallpaper: WallpaperOption) => void;
}

export const WallpaperSettings = ({ currentWallpaper, onWallpaperChange }: WallpaperSettingsProps) => {
    const [hovered, setHovered] = useState<string | null>(null);
    const [activeCategory, setActiveCategory] = useState<WallpaperCategory>('all');

    const filtered = activeCategory === 'all'
        ? WALLPAPERS
        : WALLPAPERS.filter(wp => wp.category === activeCategory);

    return (
        <GlassCard className="p-6">
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                    <Palette className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h3 className="font-bold text-gray-800">Wallpaper Theme</h3>
                    <p className="text-xs text-gray-500">Choose your study environment · {WALLPAPERS.length} themes</p>
                </div>
            </div>

            {/* Category tabs */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-1">
                {(Object.keys(CATEGORY_CONFIG) as WallpaperCategory[]).map(cat => {
                    const cfg = CATEGORY_CONFIG[cat];
                    const isActive = activeCategory === cat;
                    return (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                                isActive ? cfg.color : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                            }`}
                        >
                            {cfg.icon}
                            {cfg.label}
                            {cat !== 'all' && (
                                <span className="ml-0.5 opacity-70">
                                    ({WALLPAPERS.filter(w => w.category === cat).length})
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 max-h-[340px] overflow-y-auto pr-1">
                {filtered.map((w) => {
                    const isActive = currentWallpaper === w.id;
                    const isHovered = hovered === w.id;

                    return (
                        <motion.button
                            key={w.id}
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => onWallpaperChange(w)}
                            onMouseEnter={() => setHovered(w.id)}
                            onMouseLeave={() => setHovered(null)}
                            className={`relative rounded-xl overflow-hidden border-2 transition-all aspect-[4/3] ${
                                isActive
                                    ? 'border-brand shadow-glow ring-2 ring-brand/20'
                                    : 'border-gray-200 hover:border-brand/40'
                            }`}
                        >
                            {/* Wallpaper preview — image or gradient */}
                            {w.imageUrl ? (
                                <img
                                    src={w.imageUrl}
                                    alt={w.name}
                                    loading="lazy"
                                    className="absolute inset-0 w-full h-full object-cover"
                                />
                            ) : (
                                <div className={`absolute inset-0 ${w.preview}`}>
                                    {w.blobColors.map((color, i) => (
                                        <div
                                            key={i}
                                            className={`absolute w-8 h-8 rounded-full blur-md ${color}`}
                                            style={{
                                                top: `${20 + i * 25}%`,
                                                left: `${10 + i * 30}%`,
                                            }}
                                        />
                                    ))}
                                </div>
                            )}

                            {/* Selected indicator */}
                            {isActive && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="absolute top-1.5 right-1.5 w-5 h-5 bg-brand rounded-full flex items-center justify-center shadow-sm z-10"
                                >
                                    <Check className="w-3 h-3 text-white" />
                                </motion.div>
                            )}

                            {/* Name label */}
                            <div className={`absolute bottom-0 inset-x-0 bg-white/80 backdrop-blur-sm px-2 py-1 transition-all ${
                                isHovered || isActive ? 'opacity-100' : 'opacity-70'
                            }`}>
                                <span className="text-[10px] font-semibold text-gray-700 flex items-center gap-1">
                                    <Monitor className="w-2.5 h-2.5" />
                                    {w.name}
                                </span>
                            </div>
                        </motion.button>
                    );
                })}
            </div>
        </GlassCard>
    );
};

export { WALLPAPERS };
