import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';

export interface UnderstandingEntry {
    topicId: number;
    topicTitle: string;
    value: number;        // 0-100
    label: string;        // 'Struggling' | 'Getting there' | 'Understand it' | 'Mastered it!'
    savedAt: number;      // timestamp
}

interface UnderstandingContextType {
    entries: UnderstandingEntry[];
    saveUnderstanding: (entry: Omit<UnderstandingEntry, 'savedAt'>) => void;
    getByTopic: (topicId: number) => UnderstandingEntry | undefined;
    averageUnderstanding: number;
}

const STORAGE_KEY = 'edutwin-understanding';
const CACHE_VERSION_KEY = 'edutwin-understanding-v';
const CURRENT_VERSION = '2'; // bump to invalidate stale mock data

function load(): UnderstandingEntry[] {
    try {
        // Invalidate stale cached mock data from older versions
        if (localStorage.getItem(CACHE_VERSION_KEY) !== CURRENT_VERSION) {
            localStorage.removeItem(STORAGE_KEY);
            localStorage.setItem(CACHE_VERSION_KEY, CURRENT_VERSION);
            return [];
        }
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
    } catch { /* ignore */ }
    return [];
}

function persist(entries: UnderstandingEntry[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

const UnderstandingContext = createContext<UnderstandingContextType | null>(null);

export const UnderstandingProvider = ({ children }: { children: ReactNode }) => {
    const [entries, setEntries] = useState<UnderstandingEntry[]>(load);

    const saveUnderstanding = useCallback((entry: Omit<UnderstandingEntry, 'savedAt'>) => {
        setEntries(prev => {
            // Upsert by topicId
            const existing = prev.findIndex(e => e.topicId === entry.topicId);
            const full: UnderstandingEntry = { ...entry, savedAt: Date.now() };
            const next = existing >= 0
                ? prev.map((e, i) => i === existing ? full : e)
                : [full, ...prev];
            persist(next);
            return next;
        });
    }, []);

    const getByTopic = useCallback((topicId: number) => {
        return entries.find(e => e.topicId === topicId);
    }, [entries]);

    const averageUnderstanding = entries.length > 0
        ? Math.round(entries.reduce((sum, e) => sum + e.value, 0) / entries.length)
        : 0;

    return (
        <UnderstandingContext.Provider value={{ entries, saveUnderstanding, getByTopic, averageUnderstanding }}>
            {children}
        </UnderstandingContext.Provider>
    );
};

export const useUnderstanding = (): UnderstandingContextType => {
    const ctx = useContext(UnderstandingContext);
    if (!ctx) throw new Error('useUnderstanding must be used within UnderstandingProvider');
    return ctx;
};
