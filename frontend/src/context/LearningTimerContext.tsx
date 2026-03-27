import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import { progressAPI } from '../services/api';

interface TimingRecord {
    topicId: string;
    topicName: string;
    startTime: number;
    endTime?: number;
    duration: number; // in seconds
}

interface MindsetInsight {
    pace: 'fast' | 'moderate' | 'slow' | 'struggling';
    message: string;
    recommendation: string;
    avgTimePerTopic: number;
}

interface LearningTimerContextType {
    startTracking: (topicId: string, topicName: string, resumeIfActive?: boolean) => void;
    stopTracking: () => void;
    currentTopic: string | null;
    elapsedTime: number;
    records: TimingRecord[];
    getInsight: () => MindsetInsight;
    getTopicTime: (topicId: string) => number;
    getTotalLearningHours: () => number;
}

const LearningTimerContext = createContext<LearningTimerContextType | undefined>(undefined);

export function LearningTimerProvider({ children }: { children: ReactNode }) {
    const [records, setRecords] = useState<TimingRecord[]>(() => {
        const stored = localStorage.getItem('learning_timer_records');
        return stored ? JSON.parse(stored) : [];
    });
    
    // Restore active session from localStorage on mount
    const [currentTopic, setCurrentTopic] = useState<string | null>(() => {
        try {
            const session = localStorage.getItem('learning_timer_active_session');
            return session ? JSON.parse(session).currentTopic : null;
        } catch {
            return null;
        }
    });
    const [currentTopicName, setCurrentTopicName] = useState<string>(() => {
        try {
            const session = localStorage.getItem('learning_timer_active_session');
            return session ? JSON.parse(session).currentTopicName : '';
        } catch {
            return '';
        }
    });
    const [startTime, setStartTime] = useState<number | null>(() => {
        try {
            const session = localStorage.getItem('learning_timer_active_session');
            return session ? JSON.parse(session).startTime : null;
        } catch {
            return null;
        }
    });
    const [elapsedTime, setElapsedTime] = useState(0);

    // Use ref to always have access to current tracking values
    const trackingRef = useRef({ currentTopic: null as string | null, currentTopicName: '', startTime: null as number | null });
    
    // Keep ref in sync with state
    useEffect(() => {
        trackingRef.current = { currentTopic, currentTopicName, startTime };
    }, [currentTopic, currentTopicName, startTime]);
    
    // Persist active session to localStorage whenever it changes
    useEffect(() => {
        if (currentTopic && startTime) {
            localStorage.setItem('learning_timer_active_session', JSON.stringify({
                currentTopic,
                currentTopicName,
                startTime,
            }));
        } else {
            localStorage.removeItem('learning_timer_active_session');
        }
    }, [currentTopic, currentTopicName, startTime]);

    // Persist records
    useEffect(() => {
        localStorage.setItem('learning_timer_records', JSON.stringify(records));
    }, [records]);

    // Tick timer continuously (no pause logic - timer always runs during topic session)
    // Calculate elapsed time from original startTime to ensure accuracy across remounts
    useEffect(() => {
        if (!startTime) return;
        
        // Immediately show the current elapsed time on mount
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        
        // Then update every second
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime]);

    // Auto-save time to database every 30 seconds (continuous, no pause logic)
    useEffect(() => {
        if (!currentTopic || !startTime) return;
        
        const autoSaveInterval = setInterval(() => {
            const totalTime = Math.round(elapsedTime);
            progressAPI.saveTopic({
                topic_id: currentTopic,
                time_spent: totalTime,
                status: 'in-progress',
            }).catch(err => {
                console.log('[Timer Context] Auto-save failed, will retry next interval:', err);
            });
        }, 30000); // Auto-save every 30 seconds
        
        return () => clearInterval(autoSaveInterval);
    }, [currentTopic, elapsedTime, startTime]);

    const startTracking = useCallback((topicId: string, topicName: string, resumeIfActive?: boolean) => {
        // Check if we're trying to resume the same topic
        if (resumeIfActive && trackingRef.current.currentTopic === topicId && trackingRef.current.startTime) {
            // Same topic is already tracking - just resume without resetting
            console.log(`[Timer] Resuming existing tracking for topic: ${topicId}`);
            return;
        }
        
        // If already tracking a different topic, save it first
        if (trackingRef.current.currentTopic && trackingRef.current.startTime) {
            const duration = Math.floor((Date.now() - trackingRef.current.startTime) / 1000);
            setRecords(prev => [...prev, {
                topicId: trackingRef.current.currentTopic!,
                topicName: trackingRef.current.currentTopicName,
                startTime: trackingRef.current.startTime!,
                endTime: Date.now(),
                duration,
            }]);
        }
        
        // Start fresh tracking for this topic
        console.log(`[Timer] Starting fresh tracking for topic: ${topicId}`);
        setCurrentTopic(topicId);
        setCurrentTopicName(topicName);
        const now = Date.now();
        setStartTime(now);
        setElapsedTime(0);
    }, []);

    const stopTracking = useCallback(() => {
        // Use ref to get current values at time of stop
        if (trackingRef.current.currentTopic && trackingRef.current.startTime) {
            const duration = Math.floor((Date.now() - trackingRef.current.startTime) / 1000);
            setRecords(prev => [...prev, {
                topicId: trackingRef.current.currentTopic!,
                topicName: trackingRef.current.currentTopicName,
                startTime: trackingRef.current.startTime!,
                endTime: Date.now(),
                duration,
            }]);
        }
        setCurrentTopic(null);
        setCurrentTopicName('');
        setStartTime(null);
        setElapsedTime(0);
    }, []);

    const getTopicTime = useCallback((topicId: string) => {
        return records
            .filter(r => r.topicId === topicId)
            .reduce((sum, r) => sum + r.duration, 0);
    }, [records]);

    const getTotalLearningHours = useCallback(() => {
        const totalSeconds = records.reduce((sum, r) => sum + r.duration, 0);
        return totalSeconds / 3600; // Convert seconds to hours
    }, [records]);

    const getInsight = useCallback((): MindsetInsight => {
        if (records.length === 0) {
            return {
                pace: 'moderate',
                message: 'Start learning to get insights about your pace!',
                recommendation: 'Begin with a topic to track your learning style.',
                avgTimePerTopic: 0,
            };
        }

        const avgTime = records.reduce((sum, r) => sum + r.duration, 0) / records.length;
        const avgMinutes = avgTime / 60;

        if (avgMinutes < 2) {
            return {
                pace: 'fast',
                message: '⚡ You\'re blazing through topics! Are you confident with the material?',
                recommendation: 'Consider taking quizzes to validate your understanding. You might benefit from harder difficulty levels.',
                avgTimePerTopic: avgTime,
            };
        } else if (avgMinutes < 8) {
            return {
                pace: 'moderate',
                message: '📚 Great pace! You\'re taking time to understand concepts well.',
                recommendation: 'Keep up the balanced approach. Try explaining concepts to solidify your understanding.',
                avgTimePerTopic: avgTime,
            };
        } else if (avgMinutes < 20) {
            return {
                pace: 'slow',
                message: '🐢 You\'re being thorough! Taking time is perfectly fine for complex topics.',
                recommendation: 'Try breaking down complex topics into smaller parts. Use the flowchart explanations for better visualization.',
                avgTimePerTopic: avgTime,
            };
        } else {
            return {
                pace: 'struggling',
                message: '🤔 It seems you might be finding this challenging. That\'s okay!',
                recommendation: 'Consider switching to "Easy" difficulty, watching recommended videos, or chatting with the AI tutor for help.',
                avgTimePerTopic: avgTime,
            };
        }
    }, [records]);

    return (
        <LearningTimerContext.Provider value={{
            startTracking,
            stopTracking,
            currentTopic,
            elapsedTime,
            records,
            getInsight,
            getTopicTime,
            getTotalLearningHours,
        }}>
            {children}
        </LearningTimerContext.Provider>
    );
}

export function useLearningTimer() {
    const ctx = useContext(LearningTimerContext);
    if (!ctx) throw new Error('useLearningTimer must be used within LearningTimerProvider');
    return ctx;
}
