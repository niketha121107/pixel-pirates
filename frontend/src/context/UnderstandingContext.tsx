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

// Pre-populate with some data for completed topics so the Progress page has something to show
function generateDefaults(): UnderstandingEntry[] {
    return [
        { topicId: 1, topicTitle: 'Python Functions & Scope', value: 82, label: 'Mastered it!', savedAt: Date.now() - 4 * 86400_000 },
        { topicId: 2, topicTitle: 'Java OOP Basics', value: 58, label: 'Getting there', savedAt: Date.now() - 6 * 86400_000 },
        { topicId: 3, topicTitle: 'C Pointers Introduction', value: 90, label: 'Mastered it!', savedAt: Date.now() - 9 * 86400_000 },
        { topicId: 4, topicTitle: 'Data Structures Overview', value: 35, label: 'Getting there', savedAt: Date.now() - 12 * 86400_000 },
        { topicId: 5, topicTitle: 'SQL Fundamentals', value: 72, label: 'Understand it', savedAt: Date.now() - 14 * 86400_000 },
    ];
}

function load(): UnderstandingEntry[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
    } catch { /* ignore */ }
    const defaults = generateDefaults();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaults));
    return defaults;
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
