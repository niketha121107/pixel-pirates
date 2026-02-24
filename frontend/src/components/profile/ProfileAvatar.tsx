import { useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Check, X } from 'lucide-react';

const AVATAR_SEEDS = [
    'Felix', 'Aneka', 'Midnight', 'Bubbles', 'Coco',
    'Lucky', 'Shadow', 'Pepper', 'Gizmo', 'Daisy',
    'Boo', 'Tigger', 'Sasha', 'Zoe', 'Milo',
    'Simba', 'Loki', 'Nala', 'Luna', 'Oscar',
];

const AVATAR_STYLES = [
    'avataaars', 'bottts', 'fun-emoji', 'lorelei', 'notionists',
    'open-peeps', 'personas', 'pixel-art', 'thumbs', 'big-smile',
];

interface ProfileAvatarProps {
    currentAvatar: string;
    onAvatarChange: (url: string) => void;
}

export const ProfileAvatar = ({ currentAvatar, onAvatarChange }: ProfileAvatarProps) => {
    const [showPicker, setShowPicker] = useState(false);
    const [selectedStyle, setSelectedStyle] = useState('avataaars');
    const [hoveredAvatar, setHoveredAvatar] = useState<string | null>(null);

    const generateAvatarUrl = (style: string, seed: string) =>
        `https://api.dicebear.com/7.x/${style}/svg?seed=${seed}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf`;

    return (
        <div className="relative">
            {/* Current Avatar Display - Snap-style */}
            <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowPicker(!showPicker)}
                className="relative cursor-pointer group"
            >
                <div className="w-28 h-28 rounded-full bg-gradient-brand p-[3px] shadow-glow">
                    <div className="w-full h-full rounded-full bg-white overflow-hidden border-2 border-white">
                        <img src={currentAvatar} alt="Profile" className="w-full h-full object-cover" />
                    </div>
                </div>
                {/* Camera overlay - like Snap */}
                <div className="absolute inset-0 rounded-full bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                    <Camera className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                {/* Online indicator dot */}
                <div className="absolute bottom-1 right-1 w-5 h-5 bg-status-success rounded-full border-[3px] border-white shadow-sm" />
            </motion.div>

            {/* Avatar Picker — rendered via portal so no parent overflow clips it */}
            {createPortal(
                <AnimatePresence>
                    {showPicker && (
                        <>
                            {/* Backdrop */}
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                onClick={() => setShowPicker(false)}
                                className="fixed inset-0 bg-black/25 backdrop-blur-sm z-[100]"
                            />

                            {/* Modal */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                                transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                                className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-[101] w-[90vw] max-w-[380px]"
                            >
                                <div className="bg-white border border-pink-100 rounded-2xl shadow-2xl p-5">
                                    {/* Header */}
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="font-bold text-gray-800 text-base">Choose Your Avatar</h3>
                                        <button
                                            onClick={() => setShowPicker(false)}
                                            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors"
                                        >
                                            <X className="w-4 h-4 text-gray-400" />
                                        </button>
                                    </div>

                                    {/* Style selector */}
                                    <div className="flex gap-1.5 mb-4 overflow-x-auto pb-2">
                                        {AVATAR_STYLES.map(style => (
                                            <button
                                                key={style}
                                                onClick={() => setSelectedStyle(style)}
                                                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                                                    selectedStyle === style
                                                        ? 'bg-brand text-white shadow-sm'
                                                        : 'bg-pink-50 text-gray-600 hover:bg-pink-100'
                                                }`}
                                            >
                                                {style.replace('-', ' ')}
                                            </button>
                                        ))}
                                    </div>

                                    {/* Avatar grid — shows 3 rows (15 avatars), scroll for rest */}
                                    <div
                                        className="grid grid-cols-5 gap-3 overflow-y-auto pr-1"
                                        style={{ maxHeight: '210px' }}
                                    >
                                        {AVATAR_SEEDS.map(seed => {
                                            const url = generateAvatarUrl(selectedStyle, seed);
                                            const isSelected = currentAvatar === url;
                                            return (
                                                <motion.button
                                                    key={`${selectedStyle}-${seed}`}
                                                    whileHover={{ scale: 1.08 }}
                                                    whileTap={{ scale: 0.92 }}
                                                    onClick={() => {
                                                        onAvatarChange(url);
                                                        setShowPicker(false);
                                                    }}
                                                    onMouseEnter={() => setHoveredAvatar(url)}
                                                    onMouseLeave={() => setHoveredAvatar(null)}
                                                    className={`relative aspect-square rounded-full border-2 transition-all bg-gray-50 ${
                                                        isSelected
                                                            ? 'border-brand shadow-glow'
                                                            : 'border-gray-200 hover:border-brand/50'
                                                    }`}
                                                >
                                                    <img
                                                        src={url}
                                                        alt={seed}
                                                        width={56}
                                                        height={56}
                                                        className="w-full h-full rounded-full object-contain"
                                                        loading="lazy"
                                                    />
                                                    {isSelected && (
                                                        <div className="absolute inset-0 rounded-full bg-brand/20 flex items-center justify-center">
                                                            <Check className="w-4 h-4 text-white drop-shadow" />
                                                        </div>
                                                    )}
                                                </motion.button>
                                            );
                                        })}
                                    </div>

                                    {/* Scroll hint */}
                                    <p className="text-[10px] text-gray-400 text-center mt-2">Scroll down for more avatars</p>

                                    {/* Preview */}
                                    {hoveredAvatar && (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="mt-3 flex items-center gap-3 p-2 bg-pink-50/50 rounded-xl"
                                        >
                                            <img src={hoveredAvatar} alt="Preview" className="w-10 h-10 rounded-full bg-gray-50 object-contain" />
                                            <span className="text-xs text-gray-500">Preview</span>
                                        </motion.div>
                                    )}
                                </div>
                            </motion.div>
                        </>
                    )}
                </AnimatePresence>,
                document.body
            )}
        </div>
    );
};
