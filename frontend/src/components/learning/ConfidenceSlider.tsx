
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../lib/utils';
import { Frown, Meh, Smile, Sparkles, Save, CheckCircle2 } from 'lucide-react';

interface ConfidenceSliderProps {
    value: number;
    onChange: (val: number) => void;
    topicId?: number;
    topicTitle?: string;
    onSave?: (value: number, label: string) => void;
}

const getEmoticonInfo = (val: number) => {
    if (val < 25) return { icon: Frown, color: 'text-status-error', text: 'Struggling' };
    if (val < 50) return { icon: Meh, color: 'text-status-warning', text: 'Getting there' };
    if (val < 75) return { icon: Smile, color: 'text-brand-light', text: 'Understand it' };
    return { icon: Sparkles, color: 'text-status-success', text: 'Mastered it!' };
};

export const ConfidenceSlider = ({ value, onChange, onSave }: ConfidenceSliderProps) => {
    const [saved, setSaved] = useState(false);

    const { icon: Emoticon, color, text } = getEmoticonInfo(value);

    const handleSave = () => {
        onSave?.(value, text);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="w-full bg-white border border-gray-200 rounded-2xl p-6 relative overflow-hidden">

            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-bold text-gray-800">Understanding Level</h3>
                    <p className="text-sm text-gray-500">How well do you grasp this concept?</p>
                </div>
                <motion.div
                    key={text}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className={cn("flex flex-col items-center", color)}
                >
                    <Emoticon className="w-8 h-8 mb-1" />
                    <span className="text-xs font-bold uppercase tracking-wider">{text}</span>
                </motion.div>
            </div>

            <div className="relative pt-4 pb-2">
                <input
                    type="range"
                    min="0"
                    max="100"
                    value={value}
                    onChange={(e) => { onChange(parseInt(e.target.value)); setSaved(false); }}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-brand/50 z-10 relative"
                    style={{
                        background: `linear-gradient(to right, #ec4899 0%, #f97316 ${value}%, rgba(255,255,255,0.1) ${value}%)`
                    }}
                />

                {/* Animated thumb glow element (decorative overlay) */}
                {/* <div
                    className="absolute top-1.5 w-6 h-6 bg-white rounded-full pointer-events-none shadow-[0_0_15px_rgba(236,72,153,0.7)] border-[4px] border-brand transform -translate-x-1/2 transition-all duration-75"
                    style={{ left: `${value}%` }}
                /> */}
            </div>

            {/* Save Feedback Button */}
            <div className="mt-4 flex items-center justify-between">
                <p className="text-xs text-gray-400">
                    Slide to rate your understanding, then save your feedback.
                </p>
                <AnimatePresence mode="wait">
                    {saved ? (
                        <motion.div
                            key="saved"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-green-50 text-green-600 border border-green-200 text-sm font-semibold"
                        >
                            <CheckCircle2 className="w-4 h-4" />
                            Saved!
                        </motion.div>
                    ) : (
                        <motion.button
                            key="save"
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={handleSave}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand/10 text-brand hover:bg-brand/20 border border-brand/20 text-sm font-semibold transition-colors"
                        >
                            <Save className="w-4 h-4" />
                            Save Feedback
                        </motion.button>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};
