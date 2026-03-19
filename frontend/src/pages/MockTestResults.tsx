import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import {
    Trophy, ArrowLeft, BarChart3, AlertCircle,
    Zap, TrendingUp, Home, RotateCcw, BookOpen, Target
} from 'lucide-react';

interface MockTestResult {
    id: string;
    topic?: string;
    topicId?: string;
    subtopicId?: string;
    score: number;
    maxScore: number;
    percentage: number;
    totalQuestions: number;
    answeredQuestions: number;
    selectedTypes?: string[];
    timeTakenSec: number;
    createdAt: string;
}

export const MockTestResults = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [results, setResults] = useState<MockTestResult[]>([]);
    const [selectedResultId, setSelectedResultId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        totalTests: 0,
        averageScore: 0,
        averagePercentage: 0,
        totalTimeSpent: 0,
        bestScore: 0,
        worstScore: 0,
        topicsAttempted: new Set<string>(),
    });

    useEffect(() => {
        // Use user-specific key to isolate test results per user
        const userKey = `edutwin-mock-results_${user?.id || 'guest'}`;
        const stored = localStorage.getItem(userKey);
        const mockResults = stored ? JSON.parse(stored) : [];
        setResults(mockResults);

        if (mockResults.length > 0) {
            const scores = mockResults.map((r: MockTestResult) => r.score);
            const percentages = mockResults.map((r: MockTestResult) => r.percentage);
            const times = mockResults.map((r: MockTestResult) => r.timeTakenSec);
            const topicsArray = mockResults.map((r: MockTestResult) => String(r.topic || 'General')).filter((t: string) => t && t !== 'General');
            const topics = new Set(topicsArray);

            setStats({
                totalTests: mockResults.length,
                averageScore: Math.round(scores.reduce((a: number, b: number) => a + b, 0) / mockResults.length),
                averagePercentage: Math.round(percentages.reduce((a: number, b: number) => a + b, 0) / mockResults.length),
                totalTimeSpent: times.reduce((a: number, b: number) => a + b, 0),
                bestScore: Math.max(...scores),
                worstScore: Math.min(...scores),
                topicsAttempted: topics as Set<string>,
            });

            if (mockResults.length > 0) {
                setSelectedResultId(mockResults[0].id);
            }
        }

        setLoading(false);
    }, [user?.id]);

    const formatTime = (seconds: number) => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;

        if (h > 0) return `${h}h ${m}m`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
    };

    const selectedResult = results.find(r => r.id === selectedResultId);

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 },
        },
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 },
    };

    if (loading) {
        return (
            <>
                <Navbar onMenuClick={() => setDrawerOpen(true)} />
                <Sidebar />
                <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
                <PageWrapper>
                    <div className="lg:ml-64 py-8 text-center">
                        <div className="animate-pulse text-gray-400">Loading results...</div>
                    </div>
                </PageWrapper>
            </>
        );
    }

    if (results.length === 0) {
        return (
            <>
                <Navbar onMenuClick={() => setDrawerOpen(true)} />
                <Sidebar />
                <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
                <PageWrapper>
                    <div className="lg:ml-64 py-12">
                        <div className="text-center">
                            <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">No Test Results Yet</h2>
                            <p className="text-gray-500 mb-6">Start a mock test to see your results and detailed analytics.</p>
                            <GradientButton onClick={() => navigate('/mock-test')} className="inline-flex items-center gap-2">
                                <Zap className="w-5 h-5" /> Start a Test
                            </GradientButton>
                        </div>
                    </div>
                </PageWrapper>
            </>
        );
    }

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
            <PageWrapper>
                <div className="lg:ml-64">
                    <div className="mb-8">
                        <button onClick={() => navigate('/dashboard')} className="flex items-center gap-2 text-brand hover:underline text-sm mb-4">
                            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                        </button>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Trophy className="w-8 h-8 text-yellow-500" />
                            Mock Test Results
                        </h1>
                        <p className="text-gray-500 mt-1">Review your performance and detailed analytics</p>
                    </div>

                    {/* Overall Statistics */}
                    <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <motion.div variants={item}>
                            <GlassCard className="p-6 text-center">
                                <div className="text-3xl font-bold text-brand mb-1">{stats.totalTests}</div>
                                <p className="text-sm text-gray-500">Tests Completed</p>
                            </GlassCard>
                        </motion.div>

                        <motion.div variants={item}>
                            <GlassCard className="p-6 text-center">
                                <div className="text-3xl font-bold text-green-500 mb-1">{stats.averagePercentage}%</div>
                                <p className="text-sm text-gray-500">Average Score</p>
                            </GlassCard>
                        </motion.div>

                        <motion.div variants={item}>
                            <GlassCard className="p-6 text-center">
                                <div className="text-3xl font-bold text-blue-500 mb-1">{stats.bestScore}</div>
                                <p className="text-sm text-gray-500">Best Score</p>
                            </GlassCard>
                        </motion.div>

                        <motion.div variants={item}>
                            <GlassCard className="p-6 text-center">
                                <div className="text-3xl font-bold text-purple-500 mb-1">{formatTime(stats.totalTimeSpent)}</div>
                                <p className="text-sm text-gray-500">Total Time Spent</p>
                            </GlassCard>
                        </motion.div>
                    </motion.div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Results History */}
                        <div className="lg:col-span-1">
                            <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                                <BarChart3 className="w-5 h-5" /> Recent Tests
                            </h2>
                            <div className="space-y-3 max-h-96 overflow-y-auto">
                                {results.map((result, idx) => (
                                    <motion.button
                                        key={result.id}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => setSelectedResultId(result.id)}
                                        className={`w-full text-left p-4 rounded-xl transition-all ${
                                            selectedResultId === result.id
                                                ? 'bg-brand/10 border-2 border-brand'
                                                : 'bg-gray-50 border-2 border-gray-200 hover:border-gray-300'
                                        }`}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-semibold text-sm text-gray-800">Test {idx + 1}</span>
                                            <span className={`text-xs px-2 py-1 rounded-full font-bold ${
                                                result.percentage >= 70 ? 'bg-green-100 text-green-700' :
                                                result.percentage >= 50 ? 'bg-yellow-100 text-yellow-700' :
                                                'bg-red-100 text-red-700'
                                            }`}>
                                                {result.percentage}%
                                            </span>
                                        </div>
                                        <p className="text-xs text-gray-500 mb-1">{result.topic || 'General'}</p>
                                        <p className="text-xs text-gray-400">{new Date(result.createdAt).toLocaleDateString()}</p>
                                    </motion.button>
                                ))}
                            </div>
                        </div>

                        {/* Detailed Result View */}
                        {selectedResult && (
                            <div className="lg:col-span-2">
                                {/* Result Card */}
                                <GlassCard className="p-8 mb-6 text-center">
                                    <div className="flex justify-center mb-4">
                                        <div className="relative w-32 h-32">
                                            <svg className="transform -rotate-90 w-32 h-32">
                                                <circle cx="64" cy="64" r="55" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                                                <motion.circle
                                                    cx="64"
                                                    cy="64"
                                                    r="55"
                                                    fill="none"
                                                    stroke="url(#gradient)"
                                                    strokeWidth="8"
                                                    strokeDasharray={`${(selectedResult.percentage / 100) * 2 * Math.PI * 55} ${2 * Math.PI * 55}`}
                                                    initial={{ strokeDasharray: `0 ${2 * Math.PI * 55}` }}
                                                    animate={{ strokeDasharray: `${(selectedResult.percentage / 100) * 2 * Math.PI * 55} ${2 * Math.PI * 55}` }}
                                                    transition={{ duration: 1 }}
                                                />
                                                <defs>
                                                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                                        <stop offset="0%" stopColor="#ec4899" />
                                                        <stop offset="100%" stopColor="#f97316" />
                                                    </linearGradient>
                                                </defs>
                                            </svg>
                                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                                <div className="text-3xl font-bold text-gray-900">{selectedResult.percentage}%</div>
                                                <p className="text-xs text-gray-500">Score</p>
                                            </div>
                                        </div>
                                    </div>

                                    <h2 className="text-2xl font-bold text-gray-900 mb-1">
                                        {selectedResult.score}/{selectedResult.maxScore} Points
                                    </h2>
                                    <p className="text-gray-500 mb-6">{selectedResult.topic || 'General Mock Test'}</p>

                                    {/* Performance Message */}
                                    <div className={`p-4 rounded-xl mb-6 ${
                                        selectedResult.percentage >= 70
                                            ? 'bg-green-50 border border-green-200'
                                            : selectedResult.percentage >= 50
                                            ? 'bg-yellow-50 border border-yellow-200'
                                            : 'bg-red-50 border border-red-200'
                                    }`}>
                                        <p className={`text-sm font-medium ${
                                            selectedResult.percentage >= 70
                                                ? 'text-green-800'
                                                : selectedResult.percentage >= 50
                                                ? 'text-yellow-800'
                                                : 'text-red-800'
                                        }`}>
                                            {selectedResult.percentage >= 70
                                                ? '🎉 Excellent! You\'re doing great!'
                                                : selectedResult.percentage >= 50
                                                ? '📚 Good effort! Keep practicing!'
                                                : '💪 Keep working on these topics!'}
                                        </p>
                                    </div>

                                    {/* Stats Grid */}
                                    <div className="grid grid-cols-3 gap-3">
                                        <div className="bg-blue-50 rounded-xl p-3">
                                            <p className="text-sm text-blue-600 font-medium">Answered</p>
                                            <p className="text-2xl font-bold text-blue-700">{selectedResult.answeredQuestions}/{selectedResult.totalQuestions}</p>
                                        </div>
                                        <div className="bg-purple-50 rounded-xl p-3">
                                            <p className="text-sm text-purple-600 font-medium">Time Taken</p>
                                            <p className="text-2xl font-bold text-purple-700">{formatTime(selectedResult.timeTakenSec)}</p>
                                        </div>
                                        <div className="bg-orange-50 rounded-xl p-3">
                                            <p className="text-sm text-orange-600 font-medium">Avg/Question</p>
                                            <p className="text-2xl font-bold text-orange-700">
                                                {Math.round((selectedResult.timeTakenSec / selectedResult.totalQuestions) * 10) / 10}s
                                            </p>
                                        </div>
                                    </div>
                                </GlassCard>

                                {/* Question Types Breakdown */}
                                {selectedResult.selectedTypes && selectedResult.selectedTypes.length > 0 && (
                                    <GlassCard className="p-6 mb-6">
                                        <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                            <Target className="w-5 h-5" /> Question Types
                                        </h3>
                                        <div className="grid grid-cols-3 gap-3">
                                            {selectedResult.selectedTypes.map((type) => {
                                                const icon = type === 'mcq' ? '📋' : type === 'fillup' ? '✏️' : '📝';
                                                const label = type === 'mcq' ? 'MCQ' : type === 'fillup' ? 'Fill-up' : 'Written';
                                                return (
                                                    <div key={type} className="bg-gray-50 rounded-xl p-3 text-center">
                                                        <p className="text-2xl mb-1">{icon}</p>
                                                        <p className="text-xs font-medium text-gray-600">{label}</p>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </GlassCard>
                                )}

                                {/* Unanswered Questions Alert */}
                                {selectedResult.answeredQuestions < selectedResult.totalQuestions && (
                                    <GlassCard className="p-4 mb-6 border-l-4 border-l-amber-400 bg-amber-50/50">
                                        <div className="flex items-center gap-3">
                                            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
                                            <div>
                                                <p className="font-semibold text-sm text-amber-800">
                                                    {selectedResult.totalQuestions - selectedResult.answeredQuestions} Question{selectedResult.totalQuestions - selectedResult.answeredQuestions !== 1 ? 's' : ''} Unanswered
                                                </p>
                                                <p className="text-xs text-amber-700 mt-0.5">
                                                    These questions were not answered and scored as incorrect.
                                                </p>
                                            </div>
                                        </div>
                                    </GlassCard>
                                )}

                                {/* Action Buttons */}
                                <div className="flex gap-3 flex-wrap">
                                    <GradientButton onClick={() => navigate('/mock-test')} className="flex-1 flex items-center justify-center gap-2">
                                        <RotateCcw className="w-4 h-4" /> Take Another Test
                                    </GradientButton>
                                    <button
                                        onClick={() => navigate('/dashboard')}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium transition-colors"
                                    >
                                        <Home className="w-4 h-4" /> Dashboard
                                    </button>
                                    <button
                                        onClick={() => navigate('/videos')}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-50 text-blue-600 hover:bg-blue-100 font-medium transition-colors"
                                    >
                                        <BookOpen className="w-4 h-4" /> Study Topics
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Progress Chart */}
                    {results.length > 1 && (
                        <GlassCard className="p-6 mt-8">
                            <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5" /> Performance Trend
                            </h2>
                            <div className="space-y-4">
                                {results.slice(0, 10).map((result, idx) => {
                                    const maxWidth = Math.max(...results.map(r => r.percentage));
                                    const width = (result.percentage / maxWidth) * 100;
                                    return (
                                        <div key={result.id}>
                                            <div className="flex justify-between mb-1">
                                                <span className="text-sm font-medium text-gray-600">Test {results.length - idx}</span>
                                                <span className="text-sm font-bold text-gray-800">{result.percentage}%</span>
                                            </div>
                                            <motion.div
                                                className="h-2 bg-gray-200 rounded-full overflow-hidden"
                                                initial={{ width: 0 }}
                                                animate={{ width: '100%' }}
                                                transition={{ duration: 0.5, delay: idx * 0.05 }}
                                            >
                                                <motion.div
                                                    className="h-full bg-gradient-to-r from-brand to-purple-500 rounded-full"
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${width}%` }}
                                                    transition={{ duration: 0.8, delay: idx * 0.1 }}
                                                />
                                            </motion.div>
                                        </div>
                                    );
                                })}
                            </div>
                        </GlassCard>
                    )}
                </div>
            </PageWrapper>
        </>
    );
};
