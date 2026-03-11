import { useState, useCallback, useEffect } from 'react';

const LANGUAGES = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
    { code: 'de', name: 'German', flag: '🇩🇪' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
    { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
    { code: 'ko', name: 'Korean', flag: '🇰🇷' },
    { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
    { code: 'pt', name: 'Portuguese', flag: '🇧🇷' },
    { code: 'ru', name: 'Russian', flag: '🇷🇺' },
    { code: 'ta', name: 'Tamil', flag: '🇮🇳' },
    { code: 'te', name: 'Telugu', flag: '🇮🇳' },
    { code: 'bn', name: 'Bengali', flag: '🇮🇳' },
    { code: 'kn', name: 'Kannada', flag: '🇮🇳' },
    { code: 'ml', name: 'Malayalam', flag: '🇮🇳' },
];

export { LANGUAGES };

// Simple client-side translation using the free MyMemory Translated API
async function translateText(text: string, from: string, to: string): Promise<string> {
    if (from === to || !text.trim()) return text;

    try {
        const response = await fetch(
            `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text.slice(0, 500))}&langpair=${from}|${to}`
        );
        const data = await response.json();
        if (data.responseStatus === 200 && data.responseData?.translatedText) {
            return data.responseData.translatedText;
        }
        return text;
    } catch {
        // Fallback: return original text
        return text;
    }
}

export function useTranslation() {
    const [currentLang, setCurrentLang] = useState(() => {
        try {
            const raw = localStorage.getItem('edutwin-user-preferences');
            if (raw) {
                const parsed = JSON.parse(raw);
                return parsed.language || 'en';
            }
        } catch { /* ignore */ }
        return 'en';
    });
    const [isTranslating, setIsTranslating] = useState(false);
    const [cache, setCache] = useState<Record<string, string>>({});

    // Clear cache when language changes
    useEffect(() => {
        setCache({});
    }, [currentLang]);

    const translate = useCallback(async (text: string, targetLang?: string): Promise<string> => {
        const to = targetLang || currentLang;
        if (to === 'en') return text;

        const cacheKey = `${text.slice(0, 100)}_${to}`;
        if (cache[cacheKey]) return cache[cacheKey];

        setIsTranslating(true);
        try {
            const translated = await translateText(text, 'en', to);
            setCache(prev => ({ ...prev, [cacheKey]: translated }));
            return translated;
        } finally {
            setIsTranslating(false);
        }
    }, [currentLang, cache]);

    const translateBatch = useCallback(async (texts: string[], targetLang?: string): Promise<string[]> => {
        const to = targetLang || currentLang;
        if (to === 'en') return texts;

        setIsTranslating(true);
        try {
            const results = await Promise.all(texts.map(t => translate(t, to)));
            return results;
        } finally {
            setIsTranslating(false);
        }
    }, [currentLang, translate]);

    return {
        currentLang,
        setCurrentLang,
        translate,
        translateBatch,
        isTranslating,
        languages: LANGUAGES,
    };
}
