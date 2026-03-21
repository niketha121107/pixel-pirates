import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';

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
    startTracking: (topicId: string, topicName: string) => void;
    stopTracking: () => void;
    pauseTracking: () => void;
    resumeTracking: () => void;
    currentTopic: string | null;
    elapsedTime: number;
    isPaused: boolean;
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
    const [currentTopic, setCurrentTopic] = useState<string | null>(null);
    const [currentTopicName, setCurrentTopicName] = useState<string>('');
    const [startTime, setStartTime] = useState<number | null>(null);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [isPaused, setIsPaused] = useState(false);

    // Use ref to always have access to current tracking values
    const trackingRef = useRef({ currentTopic: null as string | null, currentTopicName: '', startTime: null as number | null, pausedAt: 0, isPaused: false });
    
    // Keep ref in sync with state
    useEffect(() => {
        trackingRef.current = { currentTopic, currentTopicName, startTime, pausedAt: trackingRef.current.pausedAt, isPaused };
    }, [currentTopic, currentTopicName, startTime, isPaused]);

    // Persist records
    useEffect(() => {
        localStorage.setItem('learning_timer_records', JSON.stringify(records));
    }, [records]);

    // Tick timer (but not when paused)
    useEffect(() => {
        if (!startTime || isPaused) return;
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime, isPaused]);

    const startTracking = useCallback((topicId: string, topicName: string) => {
        // If already tracking, stop and save previous session first
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
        setCurrentTopic(topicId);
        setCurrentTopicName(topicName);
        setStartTime(Date.now());
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
        setIsPaused(false);
    }, []);

    const pauseTracking = useCallback(() => {
        // Freeze the timer without stopping it
        if (trackingRef.current.currentTopic && trackingRef.current.startTime && !trackingRef.current.isPaused) {
            trackingRef.current.pausedAt = elapsedTime; // Save current elapsed time
            // Persist pause state to localStorage so it survives navigation
            localStorage.setItem(`timer_pause_${trackingRef.current.currentTopic}`, JSON.stringify({
                pausedAt: elapsedTime,
                pausedTime: Date.now(),
            }));
            setIsPaused(true);
        }
    }, [elapsedTime]);

    const resumeTracking = useCallback(() => {
        // Resume the timer from where it was paused
        if (trackingRef.current.currentTopic && trackingRef.current.isPaused) {
            // Get the saved pause state from localStorage
            const savedPauseKey = `timer_pause_${trackingRef.current.currentTopic}`;
            const savedPause = localStorage.getItem(savedPauseKey);
            
            let resumeFromTime = trackingRef.current.pausedAt;
            if (savedPause) {
                try {
                    const pauseData = JSON.parse(savedPause);
                    resumeFromTime = pauseData.pausedAt;
                } catch (e) {
                    // Use current pausedAt if parsing fails
                }
            }
            
            // Adjust start time so elapsedTime continues from where it was paused
            const adjustedStartTime = Date.now() - resumeFromTime * 1000;
            setStartTime(adjustedStartTime);
            setIsPaused(false);
            // Clear the saved pause state
            localStorage.removeItem(savedPauseKey);
        }
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
            pauseTracking,
            resumeTracking,
            currentTopic,
            elapsedTime,
            isPaused,
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
