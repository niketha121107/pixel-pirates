import { motion } from 'framer-motion';
import { Globe, CheckCircle2 } from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';
import { LANGUAGES } from '../../lib/translations';

interface LanguageSettingsProps {
    currentLanguage: string;
    onLanguageChange: (langCode: string) => void;
}

export const LanguageSettings = ({ currentLanguage, onLanguageChange }: LanguageSettingsProps) => {
    return (
        <GlassCard className="p-6 backdrop-blur-md">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-500" />
                Learning Language
            </h3>
            <p className="text-gray-600 text-sm mb-4">
                Select your preferred language for the learning interface
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {LANGUAGES.map((lang) => (
                    <motion.button
                        key={lang.code}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => onLanguageChange(lang.code)}
                        className={`p-3 rounded-lg border-2 transition-all text-center relative ${
                            currentLanguage === lang.code
                                ? 'border-blue-400 bg-blue-50 ring-2 ring-blue-300'
                                : 'border-gray-200 bg-white hover:border-blue-200 hover:bg-gray-50'
                        }`}
                    >
                        {currentLanguage === lang.code && (
                            <CheckCircle2 className="w-4 h-4 text-blue-500 absolute top-1 right-1" />
                        )}
                        <div className="font-semibold text-gray-800 text-sm">{lang.native}</div>
                        <div className="text-xs text-gray-600 mt-1">{lang.name}</div>
                    </motion.button>
                ))}
            </div>
        </GlassCard>
    );
};
