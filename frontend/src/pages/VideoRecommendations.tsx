import { useState, useEffect, useCallback, useMemo } from 'react';
import { topicsAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, CheckCircle2, Clock, ChevronRight, Target, XCircle, Filter, Loader2, Search, Mic, MicOff, Code2, ChevronDown, ChevronUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useVoiceSearch } from '../hooks/useVoiceSearch';

// Language colors for visual distinction
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

interface TopicItem {
    id: string | number;
    title: string;
    lang: string;
    status: 'completed' | 'pending';
    score: number;
    total: number;
    difficulty?: string;
}

export const VideoRecommendations = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [allTopics, setAllTopics] = useState<TopicItem[]>([]);
    const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'pending'>('all');
    const [languageFilter, setLanguageFilter] = useState<string>('all');
    const [expandedLangs, setExpandedLangs] = useState<Set<string>>(new Set());
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);

    // Voice search
    const handleVoiceResult = useCallback((text: string) => {
        setSearchQuery(prev => prev + text);
    }, []);
    const { isListening, startListening, stopListening, isSupported: voiceSupported } = useVoiceSearch(handleVoiceResult);

    useEffect(() => {
        const fetchTopics = async () => {
            setLoading(true);
            try {
                const res = await topicsAPI.getAll();
                const topics = (res.data?.data?.topics || []).map((t: any, i: number) => ({
                    id: t.id || i + 1,
                    title: t.topicName || t.title,
                    lang: t.language,
                    status: (t.status || 'pending') as 'completed' | 'pending',
                    score: t.score ?? 0,
                    total: t.total ?? 100,
                    difficulty: t.difficulty || 'Beginner',
                }));
                setAllTopics(topics);
            } catch {
                // fallback empty
            } finally {
                setLoading(false);
            }
        };
        fetchTopics();
    }, []);

    const completedCount = allTopics.filter(t => t.status === 'completed').length;
    const pendingCount = allTopics.filter(t => t.status === 'pending').length;

    const filteredTopics = allTopics.filter(topic => {
        const matchesStatus = statusFilter === 'all' || topic.status === statusFilter;
        const matchesSearch = !searchQuery.trim() || topic.title.toLowerCase().includes(searchQuery.toLowerCase()) || topic.lang.toLowerCase().includes(searchQuery.toLowerCase()) || (topic.difficulty || '').toLowerCase().includes(searchQuery.toLowerCase()) || topic.status.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesLang = languageFilter === 'all' || topic.lang === languageFilter;
        return matchesStatus && matchesSearch && matchesLang;
    });

    const availableLanguages = useMemo(() => {
        const langCount: Record<string, number> = {};
        allTopics.forEach(t => { langCount[t.lang] = (langCount[t.lang] || 0) + 1; });
        return Object.entries(langCount)
            .sort((a, b) => b[1] - a[1])
            .map(([lang, count]) => ({ lang, count }));
    }, [allTopics]);

    const groupedTopics = useMemo(() => {
        const groups: Record<string, typeof filteredTopics> = {};
        filteredTopics.forEach(t => {
            if (!groups[t.lang]) groups[t.lang] = [];
            groups[t.lang].push(t);
        });
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
                <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 w-full max-w-6xl mx-auto space-y-6">
                    {/* Header */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <BookOpen className="w-8 h-8 text-brand" />
                            Topics
                        </h1>
                        <p className="text-gray-500 mt-1">Browse all learning topics and track your progress</p>
                    </motion.div>

                    {/* Search Bar */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 }}>
                        <div className="relative">
                            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search topics by name or language..."
                                value={searchQuery}
                                onChange={e => setSearchQuery(e.target.value)}
                                className="w-full pl-11 pr-12 py-3 rounded-xl border border-pink-100 bg-white/80 backdrop-blur text-sm focus:outline-none focus:ring-2 focus:ring-brand/40 placeholder:text-gray-400"
                            />
                            {voiceSupported && (
                                <button
                                    onClick={isListening ? stopListening : startListening}
                                    className={`absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-colors ${
                                        isListening
                                            ? 'bg-red-100 text-red-500 animate-pulse'
                                            : 'text-gray-400 hover:text-brand hover:bg-brand/5'
                                    }`}
                                    title={isListening ? 'Stop recording' : 'Voice search'}
                                >
                                    {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                                </button>
                            )}
                        </div>
                    </motion.div>

                    {/* Stats Summary */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="grid grid-cols-3 gap-4">
                        <GlassCard className="p-4 flex items-center gap-3">
                            <div className="p-2.5 bg-brand/10 rounded-xl"><BookOpen className="w-5 h-5 text-brand" /></div>
                            <div>
                                <p className="text-2xl font-bold text-gray-800">{allTopics.length}</p>
                                <p className="text-xs text-gray-500">Total Topics</p>
                            </div>
                        </GlassCard>
                        <GlassCard className="p-4 flex items-center gap-3">
                            <div className="p-2.5 bg-candy-mint/40 rounded-xl"><CheckCircle2 className="w-5 h-5 text-emerald-600" /></div>
                            <div>
                                <p className="text-2xl font-bold text-gray-800">{completedCount}</p>
                                <p className="text-xs text-gray-500">Completed</p>
                            </div>
                        </GlassCard>
                        <GlassCard className="p-4 flex items-center gap-3">
                            <div className="p-2.5 bg-candy-peach/40 rounded-xl"><Clock className="w-5 h-5 text-orange-600" /></div>
                            <div>
                                <p className="text-2xl font-bold text-gray-800">{pendingCount}</p>
                                <p className="text-xs text-gray-500">Pending</p>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Filter */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="space-y-3">
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


                    </motion.div>

                    {/* Topics List — Grouped by Language */}
                    {loading ? (
                        <div className="flex justify-center py-20">
                            <Loader2 className="w-8 h-8 text-brand animate-spin" />
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {groupedTopics.map(([lang, topics]) => {
                                const colors = LANG_COLORS[lang] || DEFAULT_LANG_COLOR;
                                const isCollapsed = !expandedLangs.has(lang);
                                const completedInLang = topics.filter(t => t.status === 'completed').length;
                                return (
                                    <div key={lang} className="space-y-3">
                                        {/* Language Group Header */}
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
                                                                                {topic.difficulty && (
                                                                                    <span className="text-[10px] font-medium text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{topic.difficulty}</span>
                                                                                )}
                                                                            </div>
                                                                            <h3 className="font-semibold text-gray-800 truncate text-sm">{topic.title}</h3>
                                                                        </div>

                                                                        {/* Score or Arrow */}
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
                        </div>
                    )}

                    {filteredTopics.length === 0 && !loading && (
                        <div className="text-center py-12 text-gray-400">
                            <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-40" />
                            <p className="font-medium">No topics found{searchQuery ? ` for "${searchQuery}"` : ''}</p>
                        </div>
                    )}
                </div>
            </PageWrapper>
        </>
    );
};
