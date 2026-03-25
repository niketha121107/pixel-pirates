import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import { progressAPI } from '../services/api';
import { formatTimeHHMMSS } from '../utils/timeFormatter';

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
    getFormattedElapsedTime: () => string; // HH:MM:SS format
    getFormattedTopicTime: (topicId: string) => string; // HH:MM:SS format
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

    // Auto-save time to database every 30 seconds
    useEffect(() => {
        if (!currentTopic || isPaused || !startTime) return;
        
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
    }, [currentTopic, elapsedTime, isPaused, startTime]);

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
                    console.log(`[Timer Context] Resuming from: ${resumeFromTime}s`);
                } catch (e) {
                    console.log(`[Timer Context] Failed to parse pause data, using pausedAt: ${trackingRef.current.pausedAt}s`);
                }
            }
            
            // Adjust start time so elapsedTime continues from where it was paused
            const adjustedStartTime = Date.now() - resumeFromTime * 1000;
            setStartTime(adjustedStartTime);
            setIsPaused(false);
            // Do NOT clear localStorage here - let TopicView clear it after successful resume
            console.log(`[Timer Context] Timer resumed. Will continue from ${resumeFromTime}s`);
        }
    }, []);

    // Handle tab visibility changes - pause when user switches tabs, resume when they come back
    // This must come AFTER pauseTracking and resumeTracking are defined
    useEffect(() => {
        const handleVisibilityChange = () => {
            if (document.hidden) {
                // Tab is now hidden - pause the timer
                pauseTracking();
            } else {
                // Tab is now visible - resume the timer
                if (currentTopic && isPaused) {
                    resumeTracking();
                }
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, [currentTopic, isPaused, pauseTracking, resumeTracking]);

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

    const getFormattedElapsedTime = useCallback(() => {
        return formatTimeHHMMSS(elapsedTime);
    }, [elapsedTime]);

    const getFormattedTopicTime = useCallback((topicId: string) => {
        const totalSeconds = getTopicTime(topicId);
        return formatTimeHHMMSS(totalSeconds);
    }, [getTopicTime]);

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
            getFormattedElapsedTime,
            getFormattedTopicTime,
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
