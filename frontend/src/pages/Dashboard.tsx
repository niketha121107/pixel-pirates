import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { topicsAPI, searchAPI, videosAPI, analyticsAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { GlassCard } from '../components/ui/GlassCard';
import { ProgressRing } from '../components/ui/ProgressRing';
import {
    Search, BookOpen, ChevronRight, CheckCircle2, Clock, Play,
    Target, Trophy, Flame, BookCheck, Eye, XCircle, Filter, Code2, ChevronDown, ChevronUp
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';

// Language icons/colors for visual distinction
const LANG_COLORS: Record<string, { bg: string; text: string; border: string }> = {
    'Python': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
    'JavaScript': { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
    'TypeScript': { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200' },
    'Java': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
    'Kotlin': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
    'C': { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200' },
    'C++': { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
    'C#': { bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200' },
    'Go': { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200' },
    'Rust': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
    'Ruby': { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
    'Swift': { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200' },
    'PHP': { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
    'R': { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
    'SQL': { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
    'HTML/CSS': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
    'Dart': { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
    'Bash': { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' },
    'Perl': { bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-300' },
    'MATLAB': { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};

const DEFAULT_LANG_COLOR = { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' };

export const Dashboard = () => {
    const { user } = useAuth();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'pending'>('all');
    const [languageFilter, setLanguageFilter] = useState<string>('all');
    const [expandedLangs, setExpandedLangs] = useState<Set<string>>(new Set());
    const [allTopics, setAllTopics] = useState<{ id: string | number; title: string; lang: string; status: 'completed' | 'pending'; score: number; total: number; videoWatched: boolean; date: string }[]>([]);
    const [recentSearches, setRecentSearches] = useState<{ query: string; time: string }[]>([]);
    const [watchedVideos, setWatchedVideos] = useState<{ title: string; duration: string; topic: string; date: string }[]>([]);
    const [streak, setStreak] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAll = async () => {
            setLoading(true);
            try {
                const [topicsRes, searchRes, videosRes, streakRes] = await Promise.allSettled([
                    topicsAPI.getAll(),
                    searchAPI.recent(),
                    videosAPI.watched(),
                    analyticsAPI.streaks(),
                ]);

                if (topicsRes.status === 'fulfilled') {
                    const topics = (topicsRes.value.data?.data?.topics || []).map((t: any, i: number) => ({
                        id: t.id || i + 1,
                        title: t.topicName || t.title,
                        lang: t.language,
                        status: (t.status || 'pending') as 'completed' | 'pending',
                        score: t.score ?? 0,
                        total: t.total ?? 100,
                        videoWatched: t.status === 'completed',
                        date: t.completedAt || '',
                    }));
                    setAllTopics(topics);
                }

                if (searchRes.status === 'fulfilled') {
                    const searches = (searchRes.value.data?.data?.searches || []).map((s: any) => ({
                        query: s.query,
                        time: s.time || 'Recently',
                    }));
                    setRecentSearches(searches);
                }

                if (videosRes.status === 'fulfilled') {
                    const videos = (videosRes.value.data?.data?.watchedVideos || []).map((v: any) => ({
                        title: v.title,
                        duration: v.duration || v.timeWatched || '',
                        topic: v.language || 'Programming',
                        date: v.watchedAt || '',
                    }));
                    setWatchedVideos(videos);
                }

                if (streakRes.status === 'fulfilled') {
                    const s = streakRes.value.data?.data?.streaks?.currentStreak;
                    if (typeof s === 'number') setStreak(s);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    const completedCount = allTopics.filter(t => t.status === 'completed').length;
    const pendingCount = allTopics.filter(t => t.status === 'pending').length;
    const totalScore = allTopics.filter(t => t.status === 'completed').reduce((acc, t) => acc + t.score, 0);
    const totalPossible = allTopics.filter(t => t.status === 'completed').reduce((acc, t) => acc + t.total, 0);
    const avgPercent = totalPossible > 0 ? Math.round((totalScore / totalPossible) * 100) : 0;
    const completionPercent = allTopics.length > 0 ? Math.round((completedCount / allTopics.length) * 100) : 0;

    const filteredTopics = allTopics.filter(topic => {
        const matchesSearch = topic.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            topic.lang.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStatus = statusFilter === 'all' || topic.status === statusFilter;
        const matchesLang = languageFilter === 'all' || topic.lang === languageFilter;
        return matchesSearch && matchesStatus && matchesLang;
    });

    // Get unique languages sorted by topic count (descending)
    const availableLanguages = useMemo(() => {
        const langCount: Record<string, number> = {};
        allTopics.forEach(t => { langCount[t.lang] = (langCount[t.lang] || 0) + 1; });
        return Object.entries(langCount)
            .sort((a, b) => b[1] - a[1])
            .map(([lang, count]) => ({ lang, count }));
    }, [allTopics]);

    // Group filtered topics by language for the "all" view
    const groupedTopics = useMemo(() => {
        const groups: Record<string, typeof filteredTopics> = {};
        filteredTopics.forEach(t => {
            if (!groups[t.lang]) groups[t.lang] = [];
            groups[t.lang].push(t);
        });
        // Sort groups: languages with more topics first
        return Object.entries(groups).sort((a, b) => b[1].length - a[1].length);
    }, [filteredTopics]);

    const toggleLangExpand = (lang: string) => {
        setExpandedLangs(prev => {
            const next = new Set(prev);
            if (next.has(lang)) next.delete(lang);
            else next.add(lang);
            return next;
        });
    };

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64" withPadding={false}>
                <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 w-full max-w-6xl mx-auto space-y-8">

                    {/* ═══ Header ═══ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col md:flex-row md:items-end justify-between gap-4">
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold mb-1">Welcome back, <span className="text-gradient">{user?.name?.split(' ')[0] || 'Alex'}</span></h1>
                            <p className="text-gray-500">Your learning hub — everything in one place.</p>
                        </div>
                        <div className="flex items-center gap-2 px-4 py-2 bg-candy-peach/40 border border-orange-200 rounded-xl text-orange-700 font-bold text-sm w-fit">
                            <Flame className="w-5 h-5" />
                            {streak} Day Streak
                        </div>
                    </motion.div>

                    {/* ═══ Student Progress Stats ═══ */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                        <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5 text-brand" /> Student Progress
                        </h2>
                        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                            <GlassCard className="p-5 flex flex-col items-center text-center">
                                <ProgressRing progress={completionPercent} size={80} strokeWidth={7}>
                                    <span className="text-lg font-bold text-gray-800">{completionPercent}%</span>
                                </ProgressRing>
                                <p className="text-xs text-gray-500 mt-2 font-medium">Overall</p>
                            </GlassCard>

                            <GlassCard className="p-5 flex items-center gap-3">
                                <div className="p-2.5 bg-candy-mint/40 rounded-xl"><CheckCircle2 className="w-5 h-5 text-emerald-600" /></div>
                                <div>
                                    <p className="text-2xl font-bold text-gray-800">{completedCount}</p>
                                    <p className="text-xs text-gray-500">Completed</p>
                                </div>
                            </GlassCard>

                            <GlassCard className="p-5 flex items-center gap-3">
                                <div className="p-2.5 bg-candy-peach/40 rounded-xl"><Clock className="w-5 h-5 text-orange-600" /></div>
                                <div>
                                    <p className="text-2xl font-bold text-gray-800">{pendingCount}</p>
                                    <p className="text-xs text-gray-500">Pending</p>
                                </div>
                            </GlassCard>

                            <GlassCard className="p-5 flex items-center gap-3">
                                <div className="p-2.5 bg-brand/10 rounded-xl"><Trophy className="w-5 h-5 text-brand" /></div>
                                <div>
                                    <p className="text-2xl font-bold text-gray-800">{avgPercent}%</p>
                                    <p className="text-xs text-gray-500">Avg Score</p>
                                </div>
                            </GlassCard>

                            <GlassCard className="p-5 flex items-center gap-3">
                                <div className="p-2.5 bg-candy-sky/50 rounded-xl"><Eye className="w-5 h-5 text-cyan-600" /></div>
                                <div>
                                    <p className="text-2xl font-bold text-gray-800">{watchedVideos.length}</p>
                                    <p className="text-xs text-gray-500">Videos Watched</p>
                                </div>
                            </GlassCard>
                        </div>
                    </motion.div>

                    {/* ═══ Search Bar + Filters ═══ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
                        <div className="flex flex-col sm:flex-row gap-3">
                            <div className="relative flex-1">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search topics, languages..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full bg-white border border-pink-100 rounded-2xl py-3.5 pl-12 pr-4 text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand/50 transition-all placeholder:text-gray-400 shadow-sm"
                                />
                            </div>
                            <div className="flex gap-2">
                                {(['all', 'completed', 'pending'] as const).map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setStatusFilter(f)}
                                        className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5 ${
                                            statusFilter === f
                                                ? f === 'completed' ? 'bg-candy-mint/50 text-emerald-700 border border-emerald-300'
                                                : f === 'pending' ? 'bg-candy-peach/50 text-orange-700 border border-orange-300'
                                                : 'bg-brand/10 text-brand border border-brand/20'
                                                : 'bg-pink-50/30 text-gray-500 border border-pink-100 hover:bg-pink-50'
                                        }`}
                                    >
                                        {f === 'all' && <Filter className="w-3.5 h-3.5" />}
                                        {f === 'completed' && <CheckCircle2 className="w-3.5 h-3.5" />}
                                        {f === 'pending' && <Clock className="w-3.5 h-3.5" />}
                                        {f.charAt(0).toUpperCase() + f.slice(1)}
                                    </button>
                                ))}
                            </div>
                        </div>


                    </motion.div>

                    {/* ═══ Topics — Grouped by Language ═══ */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                                <BookCheck className="w-5 h-5 text-brand" />
                                {languageFilter === 'all' ? 'All Topics' : `${languageFilter} Topics`}
                                <span className="text-sm font-normal text-gray-400 ml-1">({filteredTopics.length})</span>
                            </h2>
                        </div>

                        {groupedTopics.map(([lang, topics]) => {
                            const colors = LANG_COLORS[lang] || DEFAULT_LANG_COLOR;
                            const isCollapsed = !expandedLangs.has(lang);
                            const completedInLang = topics.filter(t => t.status === 'completed').length;
                            return (
                                <div key={lang} className="space-y-3">
                                    {/* Language Group Header — only show when viewing all languages */}
                                    {languageFilter === 'all' && (
                                        <button
                                            onClick={() => toggleLangExpand(lang)}
                                            className={`w-full flex items-center justify-between px-4 py-3 rounded-2xl ${colors.bg} border ${colors.border} transition-all hover:shadow-sm`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Code2 className={`w-4.5 h-4.5 ${colors.text}`} />
                                                <span className={`text-sm font-bold ${colors.text}`}>{lang}</span>
                                                <span className="text-xs text-gray-400 font-medium">{topics.length} topics</span>
                                                {completedInLang > 0 && (
                                                    <span className="text-[10px] font-bold bg-candy-mint/50 text-emerald-700 px-2 py-0.5 rounded-full">
                                                        {completedInLang} done
                                                    </span>
                                                )}
                                            </div>
                                            {isCollapsed ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronUp className="w-4 h-4 text-gray-400" />}
                                        </button>
                                    )}

                                    <AnimatePresence mode="popLayout">
                                        {!isCollapsed && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: 'auto' }}
                                                exit={{ opacity: 0, height: 0 }}
                                                className="grid grid-cols-1 md:grid-cols-2 gap-3"
                                            >
                                                {topics.map((topic) => {
                                                    const scorePercent = topic.total > 0 && topic.status === 'completed' ? Math.round((topic.score / topic.total) * 100) : 0;
                                                    return (
                                                        <motion.div
                                                            key={topic.id}
                                                            layout
                                                            initial={{ opacity: 0, scale: 0.95 }}
                                                            animate={{ opacity: 1, scale: 1 }}
                                                            exit={{ opacity: 0, scale: 0.95 }}
                                                        >
                                                            <Link to={`/topic?id=${topic.id}`}>
                                                                <GlassCard interactive className="p-4 flex items-center gap-4">
                                                                    {/* Status Icon */}
                                                                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                                                                        topic.status === 'completed'
                                                                            ? scorePercent >= 80 ? 'bg-candy-mint/50' : scorePercent >= 50 ? 'bg-candy-lemon/50' : 'bg-candy-pink/50'
                                                                            : 'bg-pink-50'
                                                                    }`}>
                                                                        {topic.status === 'completed' ? (
                                                                            scorePercent >= 80 ? <CheckCircle2 className="w-5 h-5 text-green-600" />
                                                                            : scorePercent >= 50 ? <Target className="w-5 h-5 text-yellow-600" />
                                                                            : <XCircle className="w-5 h-5 text-red-500" />
                                                                        ) : (
                                                                            <Clock className="w-5 h-5 text-gray-400" />
                                                                        )}
                                                                    </div>

                                                                    {/* Info */}
                                                                    <div className="flex-1 min-w-0">
                                                                        <div className="flex items-center gap-2 mb-0.5">
                                                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${colors.text} ${colors.bg}`}>{topic.lang}</span>
                                                                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                                                                                topic.status === 'completed'
                                                                                    ? 'bg-candy-mint/50 text-emerald-700'
                                                                                    : 'bg-candy-peach/50 text-orange-700'
                                                                            }`}>
                                                                                {topic.status}
                                                                            </span>
                                                                        </div>
                                                                        <h3 className="font-semibold text-gray-800 truncate text-sm">{topic.title}</h3>
                                                                        {topic.status === 'completed' && (
                                                                            <p className="text-xs text-gray-400 mt-0.5">Score: {topic.score}/{topic.total} · {topic.date}</p>
                                                                        )}
                                                                    </div>

                                                                    {/* Score or Action */}
                                                                    <div className="flex-shrink-0 flex items-center gap-2">
                                                                        {topic.status === 'completed' ? (
                                                                            <div className={`text-lg font-bold ${
                                                                                scorePercent >= 80 ? 'text-green-600' : scorePercent >= 50 ? 'text-yellow-600' : 'text-red-500'
                                                                            }`}>
                                                                                {scorePercent}%
                                                                            </div>
                                                                        ) : (
                                                                            <ChevronRight className="w-5 h-5 text-gray-300" />
                                                                        )}
                                                                    </div>
                                                                </GlassCard>
                                                            </Link>
                                                        </motion.div>
                                                    );
                                                })}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            );
                        })}

                        {filteredTopics.length === 0 && (
                            <div className="text-center py-12 text-gray-400">
                                <Search className="w-10 h-10 mx-auto mb-3 opacity-40" />
                                <p className="font-medium">No topics found{searchQuery ? ` for "${searchQuery}"` : ''}</p>
                            </div>
                        )}
                    </motion.div>

                    {/* ═══ Bottom Row: Search History + Watched Videos ═══ */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                        {/* Recent Searches */}
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                            <GlassCard className="p-6">
                                <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                                    <Search className="w-5 h-5 text-brand" /> Recent Searches
                                </h2>
                                <div className="space-y-2">
                                    {recentSearches.map((item, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.35 + i * 0.05 }}
                                        >
                                            <Link to={`/topic?q=${encodeURIComponent(item.query)}`}>
                                                <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-pink-50/50 hover:bg-pink-50 transition-colors group">
                                                    <div className="flex items-center gap-3">
                                                        <BookOpen className="w-4 h-4 text-gray-400" />
                                                        <span className="text-sm font-medium text-gray-700 group-hover:text-brand transition-colors">{item.query}</span>
                                                    </div>
                                                    <span className="text-xs text-gray-400">{item.time}</span>
                                                </div>
                                            </Link>
                                        </motion.div>
                                    ))}
                                </div>
                            </GlassCard>
                        </motion.div>

                        {/* Watched Videos */}
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
                            <GlassCard className="p-6">
                                <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                                    <Play className="w-5 h-5 text-brand" /> Watched Videos
                                </h2>
                                <div className="space-y-2">
                                    {watchedVideos.map((video, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.4 + i * 0.05 }}
                                        >
                                            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-pink-50/50 hover:bg-pink-50 transition-colors">
                                                <div className="flex-shrink-0 w-9 h-9 bg-brand/10 rounded-lg flex items-center justify-center">
                                                    <Play className="w-4 h-4 text-brand" />
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <h4 className="text-sm font-medium text-gray-700 truncate">{video.title}</h4>
                                                    <p className="text-xs text-gray-400">{video.topic}</p>
                                                </div>
                                                <div className="text-right flex-shrink-0">
                                                    <p className="text-xs font-semibold text-gray-600">{video.duration}</p>
                                                    <p className="text-[10px] text-gray-400">{video.date}</p>
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </GlassCard>
                        </motion.div>

                    </div>

                </div>
            </PageWrapper>
        </>
    );
};
