import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { WatchedVideo, ExplanationStyle, LeaderboardEntry } from '../types';
import { topics, leaderboard as initialLeaderboard } from '../data/mockData';
import { useAuth } from './AuthContext';

interface AppState {
    completedTopics: string[];
    pendingTopics: string[];
    inProgressTopics: string[];
    videosWatched: WatchedVideo[];
    totalScore: number;
    leaderboard: LeaderboardEntry[];
    preferredStyle: ExplanationStyle;
    confusionCount: number;
}

interface AppContextType extends AppState {
    markVideoWatched: (video: WatchedVideo) => void;
    completeTopic: (topicId: string) => void;
    startTopic: (topicId: string) => void;
    updateScore: (points: number) => void;
    setPreferredStyle: (style: ExplanationStyle) => void;
    incrementConfusion: () => void;
    resetConfusion: () => void;
    getTopicStatus: (topicId: string) => 'completed' | 'pending' | 'in-progress';
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
    const { user } = useAuth();

    const [state, setState] = useState<AppState>(() => ({
        completedTopics: user?.completedTopics ?? [],
        pendingTopics: user?.pendingTopics ?? topics.map(t => t.id),
        inProgressTopics: user?.inProgressTopics ?? [],
        videosWatched: user?.videosWatched ?? [],
        totalScore: user?.totalScore ?? 0,
        leaderboard: initialLeaderboard,
        preferredStyle: user?.preferredStyle ?? 'visual',
        confusionCount: user?.confusionCount ?? 0,
    }));

    const markVideoWatched = useCallback((video: WatchedVideo) => {
        setState(prev => {
            if (prev.videosWatched.some(v => v.id === video.id)) return prev;
            return { ...prev, videosWatched: [video, ...prev.videosWatched] };
        });
    }, []);

    const completeTopic = useCallback((topicId: string) => {
        setState(prev => ({
            ...prev,
            completedTopics: prev.completedTopics.includes(topicId) ? prev.completedTopics : [...prev.completedTopics, topicId],
            pendingTopics: prev.pendingTopics.filter(id => id !== topicId),
            inProgressTopics: prev.inProgressTopics.filter(id => id !== topicId),
        }));
    }, []);

    const startTopic = useCallback((topicId: string) => {
        setState(prev => {
            if (prev.completedTopics.includes(topicId) || prev.inProgressTopics.includes(topicId)) return prev;
            return {
                ...prev,
                inProgressTopics: [...prev.inProgressTopics, topicId],
                pendingTopics: prev.pendingTopics.filter(id => id !== topicId),
            };
        });
    }, []);

    const updateScore = useCallback((points: number) => {
        setState(prev => {
            const newScore = prev.totalScore + points;
            const updatedLeaderboard = prev.leaderboard.map(entry =>
                entry.userId === 'user-1'
                    ? { ...entry, score: newScore, topicsCompleted: prev.completedTopics.length }
                    : entry
            ).sort((a, b) => b.score - a.score).map((entry, i) => ({ ...entry, rank: i + 1 }));
            return { ...prev, totalScore: newScore, leaderboard: updatedLeaderboard };
        });
    }, []);

    const setPreferredStyle = useCallback((style: ExplanationStyle) => {
        setState(prev => ({ ...prev, preferredStyle: style }));
    }, []);

    const incrementConfusion = useCallback(() => {
        setState(prev => ({ ...prev, confusionCount: prev.confusionCount + 1 }));
    }, []);

    const resetConfusion = useCallback(() => {
        setState(prev => ({ ...prev, confusionCount: 0 }));
    }, []);

    const getTopicStatus = useCallback((topicId: string): 'completed' | 'pending' | 'in-progress' => {
        if (state.completedTopics.includes(topicId)) return 'completed';
        if (state.inProgressTopics.includes(topicId)) return 'in-progress';
        return 'pending';
    }, [state.completedTopics, state.inProgressTopics]);

    return (
        <AppContext.Provider value={{
            ...state,
            markVideoWatched,
            completeTopic,
            startTopic,
            updateScore,
            setPreferredStyle,
            incrementConfusion,
            resetConfusion,
            getTopicStatus,
        }}>
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const ctx = useContext(AppContext);
    if (!ctx) throw new Error('useApp must be used within AppProvider');
    return ctx;
}
