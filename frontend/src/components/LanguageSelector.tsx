import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { LANGUAGES } from '../lib/translations';

interface LanguageSelectorProps {
    isOpen: boolean;
    onClose: () => void;
    currentLanguage: string;
    onSelectLanguage: (langCode: string) => void;
}

export const LanguageSelector = ({ isOpen, onClose, currentLanguage, onSelectLanguage }: LanguageSelectorProps) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                >
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.95, opacity: 0 }}
                        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-white rounded-2xl shadow-2xl p-6 max-w-md w-full"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-bold text-gray-900">Select Language</h2>
                            <button
                                onClick={onClose}
                                className="text-gray-500 hover:text-gray-700 transition-colors p-1 hover:bg-gray-100 rounded-lg"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <p className="text-gray-600 text-sm mb-6">Choose your preferred learning language</p>

                        <div className="grid grid-cols-2 gap-3">
                            {LANGUAGES.map((lang: typeof LANGUAGES[0]) => (
                                <motion.button
                                    key={lang.code}
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => {
                                        onSelectLanguage(lang.code);
                                        onClose();
                                    }}
                                    className={`p-4 rounded-xl border-2 transition-all text-center ${
                                        currentLanguage === lang.code
                                            ? 'border-brand bg-brand/10 ring-2 ring-brand'
                                            : 'border-gray-200 bg-white hover:border-brand/50 hover:bg-gray-50'
                                    }`}
                                >
                                    <div className="font-bold text-gray-900">{lang.native}</div>
                                    <div className="text-xs text-gray-600 mt-1">{lang.name}</div>
                                </motion.button>
                            ))}
                        </div>

                        <div className="mt-6 pt-6 border-t border-gray-200">
                            <p className="text-xs text-gray-500 text-center">
                                Your language preference will be saved to your profile
                            </p>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
