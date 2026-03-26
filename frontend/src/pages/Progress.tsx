import { useState, useEffect, useCallback } from 'react';
import { usersAPI, topicsAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { ProgressRing } from '../components/ui/ProgressRing';
import { BookCheck, Trophy, Target, Clock, CheckCircle2, XCircle, Brain, Frown, Meh, Smile, Sparkles, RotateCw } from 'lucide-react';
import { motion } from 'framer-motion';
import { useUnderstanding } from '../context/UnderstandingContext';
import { useAuth } from '../context/AuthContext';
import { LearningProgressGraph } from '../components/charts/LearningProgressGraph';

const formatTimeHHMMSS = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

const getLevelInfo = (val: number) => {
    if (val < 25) return { icon: Frown, color: 'text-red-500', bg: 'bg-red-50', border: 'border-red-200', label: 'Struggling', barColor: 'bg-red-500' };
    if (val < 50) return { icon: Meh, color: 'text-amber-500', bg: 'bg-amber-50', border: 'border-amber-200', label: 'Getting there', barColor: 'bg-amber-500' };
    if (val < 75) return { icon: Smile, color: 'text-pink-500', bg: 'bg-pink-50', border: 'border-pink-200', label: 'Understand it', barColor: 'bg-pink-500' };
    return { icon: Sparkles, color: 'text-green-500', bg: 'bg-green-50', border: 'border-green-200', label: 'Mastered it!', barColor: 'bg-green-500' };
};

export const Progress = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { user } = useAuth();
    const { entries, averageUnderstanding } = useUnderstanding();
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [fetchError, setFetchError] = useState<string | null>(null);
    const [completedTopics, setCompletedTopics] = useState<{ title: string; score: number; total: number; date: string; videoWatched: boolean }[]>([]);
    const [dailyProgressData, setDailyProgressData] = useState<Array<{ day: string; xp: number }>>([]);
    const [overallStats, setOverallStats] = useState({
        totalTopics: 0,
        completedTopics: 0,
        totalQuizzes: 0,
        avgScore: 0,
        totalHoursLearned: 0, // Store total seconds
        streak: 0,
    });

    // Helper function to calculate daily learning engagement for the past 7 days
    const calculateDailyProgress = (completed: Array<{date: string}>, mockResults: Array<{createdAt?: string}>) => {
        const today = new Date();
        const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const dailyMap: Record<string, number> = {};
        
        // Initialize last 7 days
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dayLabel = dayLabels[date.getDay()];
            const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
            dailyMap[dateStr] = 0;
        }

        // Count completed topics (each topic = 1 point)
        completed.forEach(item => {
            if (item.date) {
                try {
                    const dateObj = new Date(item.date);
                    const dateStr = dateObj.toISOString().split('T')[0];
                    if (dailyMap.hasOwnProperty(dateStr)) {
                        dailyMap[dateStr] += 1; // 1 point per topic
                    }
                } catch (e) {
                    // ignore invalid dates
                }
            }
        });

        // Count quiz/mock test completions (each quiz = 0.5 points)
        mockResults.forEach(result => {
            if (result.createdAt) {
                try {
                    const dateObj = new Date(result.createdAt);
                    const dateStr = dateObj.toISOString().split('T')[0];
                    if (dailyMap.hasOwnProperty(dateStr)) {
                        dailyMap[dateStr] += 0.5; // 0.5 points per quiz
                    }
                } catch (e) {
                    // ignore invalid dates
                }
            }
        });

        // Convert to array format for chart
        return Object.entries(dailyMap).map(([dateStr, points]) => {
            const date = new Date(dateStr + 'T00:00:00');
            const dayLabel = dayLabels[date.getDay()];
            return {
                day: dayLabel,
                xp: Math.round(points * 10) / 10, // Round to 1 decimal
            };
        });
    };

    // Main fetch function - extracted for reusability
    const fetchAllData = useCallback(async () => {
        try {
            console.log('🔄 Progress page fetching data...');
            
            // Use user-specific key to isolate test results per user
            const userKey = `edutwin-mock-results_${user?.id || 'guest'}`;
            const localMockRaw = localStorage.getItem(userKey);
            let localMock: Array<{ topic?: string; percentage?: number; score?: number; maxScore?: number; createdAt?: string; timeTakenSec?: number }> = [];
            if (localMockRaw) {
                try {
                    localMock = JSON.parse(localMockRaw);
                    console.log('📦 Local mock results loaded:', localMock.length, 'items');
                } catch {
                    localMock = [];
                }
            }

            const [statsRes, topicsRes] = await Promise.allSettled([
                usersAPI.stats(),
                topicsAPI.getAll(),
            ]);

            // Get topics list first to get accurate total count
            let allTopicsCount = 0;
            let completedTopicsFromAPI: Array<any> = [];
            if (topicsRes.status === 'fulfilled') {
                const allTopics = topicsRes.value.data?.data?.topics || [];
                allTopicsCount = allTopics.length; // Accurate total count
                completedTopicsFromAPI = allTopics.filter((t: any) => t.status === 'completed') || [];
                console.log('📋 Topics API:', { totalTopics: allTopicsCount, completedTopics: completedTopicsFromAPI.length });
            } else if (topicsRes.status === 'rejected') {
                console.error('❌ Topics API failed:', topicsRes.reason);
            }

            if (statsRes.status === 'fulfilled') {
                const s = statsRes.value.data?.data?.stats;
                if (s) {
                    console.log('📊 Stats from API:', s);
                    // Use backend as single source of truth (no Math.max blending)
                    const backendSeconds = (s.totalHours ?? 0) * 3600;
                    
                    setOverallStats({
                        totalTopics: allTopicsCount > 0 ? allTopicsCount : s.totalTopics ?? 0,
                        completedTopics: s.topicsCompleted ?? 0,
                        totalQuizzes: s.quizzesTaken ?? 0,  // Backend value only
                        avgScore: s.avgScore ?? 0,          // Backend value only
                        totalHoursLearned: backendSeconds,   // Backend value only
                        streak: s.streak ?? 0,
                    });
                }
            } else if (statsRes.status === 'rejected') {
                console.error('❌ Stats API failed:', statsRes.reason);
            }

            if (topicsRes.status === 'fulfilled') {
                const topics = completedTopicsFromAPI
                    .map((t: any) => ({
                        title: t.topicName || t.title,
                        score: t.score ?? 0,
                        total: t.total ?? 100,
                        date: t.completedAt || '',
                        videoWatched: true,
                    }));

                const localCompleted = localMock
                    .filter(r => typeof r.percentage === 'number')
                    .slice(0, 20)
                    .map((r) => ({
                        title: r.topic || 'Mock Test',
                        score: Number(r.score || 0),
                        total: Number(r.maxScore || 100),
                        date: r.createdAt ? new Date(r.createdAt).toLocaleDateString() : '',
                        videoWatched: true,
                    }));

                // Calculate and set daily progress data based on actual user performance
                const allCompleted = topics.length > 0 ? topics : localCompleted;
                const dailyData = calculateDailyProgress(allCompleted, localMock);
                setDailyProgressData(dailyData);
                
                setCompletedTopics(allCompleted);
            }
        } catch (error) {
            console.error('Error fetching progress data:', error);
            setFetchError('Failed to load progress data. Please refresh to try again.');
        } finally {
            setFetchError(null);  // Clear error on successful fetch
        }
    }, [user?.id]);

    // Initial load on mount
    useEffect(() => {
        const load = async () => {
            setLoading(true);
            await fetchAllData();
            setLoading(false);
        };
        load();
    }, [fetchAllData]);

    // Smart auto-refresh: Listen for changes and smart polling
    useEffect(() => {
        // Listen for storage changes (when mock test results are saved)
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key?.includes('edutwin-mock-results') || e.key?.includes('edutwin-understanding')) {
                // Immediate refresh when user takes a test
                fetchAllData();
            }
        };

        window.addEventListener('storage', handleStorageChange);

        // Smart polling: Only every 60 seconds to reduce unnecessary API calls
        // (relying primarily on storage change events for real-time updates)
        const pollInterval = setInterval(() => {
            fetchAllData();
        }, 60000); // Reduced from 30s to 60s for efficiency

        return () => {
            window.removeEventListener('storage', handleStorageChange);
            clearInterval(pollInterval);
        };
    }, [fetchAllData]);

    // Manual refresh handler
    const handleRefresh = async () => {
        setIsRefreshing(true);
        await fetchAllData();
        setIsRefreshing(false);
    };

    const completionPercentage = overallStats.totalTopics > 0 ? Math.round((overallStats.completedTopics / overallStats.totalTopics) * 100) : 0;

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-5xl mx-auto space-y-8">

                    {/* Error Banner */}
                    {fetchError && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-red-50 border border-red-300 rounded-xl p-4 flex items-center justify-between"
                        >
                            <div className="flex items-center gap-3">
                                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                                <p className="text-sm text-red-700 font-medium">{fetchError}</p>
                            </div>
                            <button
                                onClick={() => { setFetchError(null); handleRefresh(); }}
                                className="text-sm px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                            >
                                Retry
                            </button>
                        </motion.div>
                    )}

                    {/* Header */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Student Progress</h1>
                            <p className="text-gray-500">Track your learning journey, test scores, and achievements.</p>
                        </div>
                        <button
                            onClick={handleRefresh}
                            disabled={isRefreshing}
                            className="p-2 rounded-lg bg-brand/10 hover:bg-brand/20 text-brand transition-colors disabled:opacity-50"
                            title="Refresh stats"
                        >
                            <RotateCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
                        </button>
                    </motion.div>

                    {/* Stats Overview */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
                    >
                        <GlassCard className="p-5 flex items-center gap-4">
                            <div className="p-3 bg-brand/10 rounded-xl">
                                <BookCheck className="w-6 h-6 text-brand" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Topics Done</p>
                                <p className="text-2xl font-bold text-gray-800">{overallStats.completedTopics}/{overallStats.totalTopics}</p>
                            </div>
                        </GlassCard>

                        <GlassCard className="p-5 flex items-center gap-4">
                            <div className="p-3 bg-candy-mint/40 rounded-xl">
                                <Trophy className="w-6 h-6 text-emerald-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Avg Score</p>
                                <p className="text-2xl font-bold text-gray-800">{overallStats.avgScore}%</p>
                            </div>
                        </GlassCard>

                        <GlassCard className="p-5 flex items-center gap-4">
                            <div className="p-3 bg-candy-peach/40 rounded-xl">
                                <Clock className="w-6 h-6 text-orange-500" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Time Learned</p>
                                <p className="text-2xl font-bold text-gray-800">{formatTimeHHMMSS(overallStats.totalHoursLearned)}</p>
                            </div>
                        </GlassCard>

                        <GlassCard className="p-5 flex items-center gap-4">
                            <div className="p-3 bg-purple-100/60 rounded-xl">
                                <Brain className="w-6 h-6 text-purple-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Avg Understanding</p>
                                <p className="text-2xl font-bold text-gray-800">{averageUnderstanding}%</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Progress Ring + Learning Progress Graph */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
                    >
                        <GlassCard className="p-8 flex flex-col items-center justify-center gap-4">
                            <ProgressRing progress={completionPercentage} size={160} strokeWidth={12}>
                                <div className="flex flex-col items-center">
                                    <span className="text-3xl font-bold text-gray-800">{completionPercentage}%</span>
                                    <span className="text-xs text-gray-500">Complete</span>
                                </div>
                            </ProgressRing>
                            <p className="text-gray-600 text-sm text-center">
                                You've completed {overallStats.completedTopics} out of {overallStats.totalTopics} topics. Keep going!
                            </p>
                        </GlassCard>

                        <div>
                            <LearningProgressGraph data={dailyProgressData} />
                        </div>
                    </motion.div>

                    {/* Completed Topics & Scores */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="space-y-4"
                    >
                        <h2 className="text-xl font-bold text-gray-800">Completed Topics & Scores</h2>
                        <div className="space-y-3">
                            {completedTopics.map((topic, i) => {
                                const scorePercent = Math.round((topic.score / topic.total) * 100);
                                return (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.4 + i * 0.08 }}
                                    >
                                        <GlassCard className="p-4 flex items-center gap-4">
                                            <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                                                scorePercent >= 80 ? 'bg-candy-mint/50' : scorePercent >= 50 ? 'bg-candy-lemon/50' : 'bg-candy-pink/50'
                                            }`}>
                                                {scorePercent >= 80 ? (
                                                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                                                ) : scorePercent >= 50 ? (
                                                    <Target className="w-5 h-5 text-yellow-600" />
                                                ) : (
                                                    <XCircle className="w-5 h-5 text-red-600" />
                                                )}
                                            </div>

                                            <div className="flex-1 min-w-0">
                                                <h3 className="font-semibold text-gray-800 truncate">{topic.title}</h3>
                                                <p className="text-xs text-gray-400">{topic.date}</p>
                                            </div>

                                            <div className="text-right flex-shrink-0">
                                                <span className={`text-lg font-bold ${
                                                    scorePercent >= 80 ? 'text-green-600' : scorePercent >= 50 ? 'text-yellow-600' : 'text-red-600'
                                                }`}>
                                                    {topic.score}/{topic.total}
                                                </span>
                                                <p className="text-xs text-gray-400">Quiz Score</p>
                                            </div>

                                            <div className="hidden sm:block w-24">
                                                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${
                                                            scorePercent >= 80 ? 'bg-green-500' : scorePercent >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                                        }`}
                                                        style={{ width: `${scorePercent}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </GlassCard>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </motion.div>

                    {/* ═══ Understanding Feedback Analysis ═══ */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="space-y-4"
                    >
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-purple-100 rounded-xl">
                                <Brain className="w-5 h-5 text-purple-600" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-gray-800">Understanding Feedback</h2>
                                <p className="text-sm text-gray-500">Self-assessed comprehension from the confidence slider</p>
                            </div>
                        </div>

                        {entries.length === 0 ? (
                            <GlassCard className="p-8 text-center">
                                <Brain className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                                <p className="text-gray-500 text-sm">No understanding feedback saved yet.</p>
                                <p className="text-gray-400 text-xs mt-1">Use the confidence slider on a topic page and click "Save Feedback" to track your comprehension.</p>
                            </GlassCard>
                        ) : (
                            <>
                                {/* Average Understanding Summary Bar */}
                                <GlassCard className="p-5">
                                    <div className="flex items-center justify-between mb-3">
                                        <span className="text-sm font-semibold text-gray-700">Overall Average Understanding</span>
                                        <span className={`text-sm font-bold ${getLevelInfo(averageUnderstanding).color}`}>
                                            {averageUnderstanding}% — {getLevelInfo(averageUnderstanding).label}
                                        </span>
                                    </div>
                                    <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${averageUnderstanding}%` }}
                                            transition={{ duration: 0.8, ease: 'easeOut' }}
                                            className={`h-full rounded-full ${getLevelInfo(averageUnderstanding).barColor}`}
                                        />
                                    </div>
                                </GlassCard>

                                {/* Per-topic breakdown */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                    {entries.map((entry, i) => {
                                        const info = getLevelInfo(entry.value);
                                        const Icon = info.icon;
                                        return (
                                            <motion.div
                                                key={entry.topicId}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: 0.6 + i * 0.06 }}
                                            >
                                                <GlassCard className={`p-4 border-l-4 ${info.border}`}>
                                                    <div className="flex items-start gap-3">
                                                        <div className={`flex-shrink-0 w-9 h-9 rounded-xl ${info.bg} flex items-center justify-center`}>
                                                            <Icon className={`w-4.5 h-4.5 ${info.color}`} />
                                                        </div>
                                                        <div className="flex-1 min-w-0">
                                                            <h4 className="font-semibold text-gray-800 text-sm truncate">{entry.topicTitle}</h4>
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                                                    <div
                                                                        className={`h-full rounded-full ${info.barColor}`}
                                                                        style={{ width: `${entry.value}%` }}
                                                                    />
                                                                </div>
                                                                <span className={`text-xs font-bold ${info.color}`}>{entry.value}%</span>
                                                            </div>
                                                            <p className={`text-xs mt-1 font-medium ${info.color}`}>{entry.label}</p>
                                                        </div>
                                                    </div>
                                                </GlassCard>
                                            </motion.div>
                                        );
                                    })}
                                </div>
                            </>
                        )}
                    </motion.div>

                </div>
            </PageWrapper>
        </>
    );
};
