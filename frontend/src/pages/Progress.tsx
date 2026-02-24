import { useState } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { ProgressRing } from '../components/ui/ProgressRing';
import { BookCheck, Trophy, Target, Clock, CheckCircle2, XCircle, Brain, Frown, Meh, Smile, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { useUnderstanding } from '../context/UnderstandingContext';

const completedTopics = [
    { title: 'Python Functions & Scope', score: 4, total: 5, date: '2026-02-20', videoWatched: true },
    { title: 'Java OOP Basics', score: 3, total: 5, date: '2026-02-18', videoWatched: true },
    { title: 'C Pointers Introduction', score: 5, total: 5, date: '2026-02-15', videoWatched: true },
    { title: 'Data Structures Overview', score: 2, total: 5, date: '2026-02-12', videoWatched: true },
    { title: 'SQL Fundamentals', score: 4, total: 5, date: '2026-02-10', videoWatched: true },
];

const overallStats = {
    totalTopics: 12,
    completedTopics: 5,
    totalQuizzes: 5,
    avgScore: 72,
    totalHoursLearned: 18,
    streak: 12,
};

const getLevelInfo = (val: number) => {
    if (val < 25) return { icon: Frown, color: 'text-red-500', bg: 'bg-red-50', border: 'border-red-200', label: 'Struggling', barColor: 'bg-red-500' };
    if (val < 50) return { icon: Meh, color: 'text-amber-500', bg: 'bg-amber-50', border: 'border-amber-200', label: 'Getting there', barColor: 'bg-amber-500' };
    if (val < 75) return { icon: Smile, color: 'text-pink-500', bg: 'bg-pink-50', border: 'border-pink-200', label: 'Understand it', barColor: 'bg-pink-500' };
    return { icon: Sparkles, color: 'text-green-500', bg: 'bg-green-50', border: 'border-green-200', label: 'Mastered it!', barColor: 'bg-green-500' };
};

export const Progress = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { entries, averageUnderstanding } = useUnderstanding();

    const completionPercentage = Math.round((overallStats.completedTopics / overallStats.totalTopics) * 100);

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-5xl mx-auto space-y-8">

                    {/* Header */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Student Progress</h1>
                        <p className="text-gray-500">Track your learning journey, test scores, and achievements.</p>
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
                                <p className="text-sm text-gray-500">Hours Learned</p>
                                <p className="text-2xl font-bold text-gray-800">{overallStats.totalHoursLearned}h</p>
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

                    {/* Progress Ring + Summary */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
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

                        <div className="lg:col-span-2 space-y-4">
                            <h2 className="text-xl font-bold text-gray-800">Completed Topics & Scores</h2>
                            <div className="space-y-3">
                                {completedTopics.map((topic, i) => {
                                    const scorePercent = Math.round((topic.score / topic.total) * 100);
                                    return (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.3 + i * 0.08 }}
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
                        </div>
                    </motion.div>

                    {/* ═══ Understanding Feedback Analysis ═══ */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
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
                                                transition={{ delay: 0.5 + i * 0.06 }}
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
