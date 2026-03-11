import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { BookOpen, User, ClipboardList, Bot, LogOut, StickyNote, TrendingUp, Clock, Search, Trash2, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { topicsAPI, searchAPI, usersAPI } from '../../services/api';

export const Sidebar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { logout } = useAuth();

    const [completedCount, setCompletedCount] = useState(0);
    const [pendingCount, setPendingCount] = useState(0);
    const [searchHistory, setSearchHistory] = useState<string[]>([]);
    const [avgScore, setAvgScore] = useState(0);
    const [streak, setStreak] = useState(0);

    useEffect(() => {
        const storedMock = localStorage.getItem('edutwin-mock-results');
        if (storedMock) {
            try {
                const results = JSON.parse(storedMock) as Array<{ percentage?: number }>;
                const valid = results.filter(r => typeof r.percentage === 'number').map(r => Number(r.percentage));
                if (valid.length > 0) {
                    const localAvg = Math.round(valid.reduce((a, b) => a + b, 0) / valid.length);
                    setAvgScore(localAvg);
                }
            } catch {
                // ignore malformed local data
            }
        }

        topicsAPI.getAll()
            .then(res => {
                const topics = res.data?.data?.topics || [];
                const completed = topics.filter((t: any) => t.status === 'completed');
                const pending = topics.filter((t: any) => t.status !== 'completed');
                setCompletedCount(completed.length);
                setPendingCount(pending.length);
            })
            .catch(() => {});

        searchAPI.recent()
            .then(res => {
                const items = res.data?.data?.searches || res.data?.data?.recentSearches || [];
                setSearchHistory(items.map((s: any) => typeof s === 'string' ? s : s.query || '').filter(Boolean).slice(0, 5));
            })
            .catch(() => {});

        usersAPI.stats()
            .then(res => {
                const stats = res.data?.data?.stats || {};
                if (typeof stats.avgScore === 'number' && stats.avgScore > 0) {
                    setAvgScore(stats.avgScore);
                }
                setStreak(stats.streak || 0);
            })
            .catch(() => {});
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    const isProfile = location.pathname === '/profile';
    const isTopics = location.pathname === '/videos';
    const isMockTest = location.pathname === '/mock-test';
    const isChat = location.pathname === '/chat';
    const isNotes = location.pathname === '/notes';
    const isProgress = location.pathname === '/progress';

    return (
        <aside className="hidden lg:flex flex-col w-64 fixed left-0 top-16 bottom-0 bg-white/90 backdrop-blur-md border-r border-pink-100 pt-4 pb-4 z-30 overflow-y-auto">
            {/* Profile Nav Link */}
            <div className="px-4 mb-2">
                <Link
                    to="/profile"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isProfile
                            ? 'bg-purple-50 text-purple-600 border border-purple-200'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <User className="w-5 h-5" />
                    My Profile
                </Link>
            </div>

            {/* Topics */}
            <div className="px-4 mb-2">
                <Link
                    to="/videos"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isTopics
                            ? 'bg-brand/10 text-brand border border-brand/20'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <BookOpen className="w-5 h-5" />
                    <span className="flex-1">Topics</span>
                    <span className="flex items-center gap-1 text-xs">
                        <span className="bg-emerald-100 text-emerald-600 px-1.5 py-0.5 rounded-full font-bold">{completedCount}</span>
                        <span className="bg-orange-100 text-orange-600 px-1.5 py-0.5 rounded-full font-bold">{pendingCount}</span>
                    </span>
                </Link>
            </div>

            {/* Mock Test */}
            <div className="px-4 mb-2">
                <Link
                    to="/mock-test"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isMockTest
                            ? 'bg-amber-50 text-amber-600 border border-amber-200'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <ClipboardList className="w-5 h-5" />
                    Mock Test
                </Link>
            </div>

            {/* AI Chat */}
            <div className="px-4 mb-2">
                <Link
                    to="/chat"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isChat
                            ? 'bg-green-50 text-green-600 border border-green-200'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <Bot className="w-5 h-5" />
                    AI Tutor Chat
                </Link>
            </div>

            {/* Notes */}
            <div className="px-4 mb-2">
                <Link
                    to="/notes"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isNotes
                            ? 'bg-yellow-50 text-yellow-600 border border-yellow-200'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <StickyNote className="w-5 h-5" />
                    My Notes
                </Link>
            </div>

            {/* Progress */}
            <div className="px-4 mb-2">
                <Link
                    to="/progress"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                        isProgress
                            ? 'bg-blue-50 text-blue-600 border border-blue-200'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                    }`}
                >
                    <TrendingUp className="w-5 h-5" />
                    Progress
                </Link>
            </div>

            <div className="flex-1" />

            {/* Search History */}
            {searchHistory.length > 0 && (
                <div className="px-4 mb-3">
                    <div className="flex items-center justify-between mb-2 px-1">
                        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
                            <Search className="w-3 h-3" /> Recent Searches
                        </p>
                        <button
                            onClick={() => {
                                searchAPI.clearRecent().catch(() => {});
                                setSearchHistory([]);
                            }}
                            className="text-gray-400 hover:text-red-500 transition-colors"
                            title="Clear history"
                        >
                            <Trash2 className="w-3 h-3" />
                        </button>
                    </div>
                    <div className="space-y-0.5">
                        {searchHistory.map((query, i) => (
                            <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs text-gray-500 hover:bg-gray-50 transition-colors">
                                <Clock className="w-3 h-3 text-gray-300 flex-shrink-0" />
                                <span className="truncate">{query}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Progress Flash Cards */}
            <div className="px-4 mb-3">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 px-1 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> Progress Flash Cards
                </p>
                <div className="space-y-2">
                    <div className="rounded-xl border border-blue-200 bg-blue-50/70 p-3">
                        <p className="text-xs font-semibold text-blue-700">Performance Snapshot</p>
                        <p className="text-xs text-blue-900 mt-1">Average Score: {avgScore}%</p>
                        <p className="text-xs text-blue-900">Completion: {completedCount}/{completedCount + pendingCount || 0}</p>
                    </div>
                    <div className="rounded-xl border border-purple-200 bg-purple-50/70 p-3">
                        <p className="text-xs font-semibold text-purple-700">Learning Streak</p>
                        <p className="text-xs text-purple-900 mt-1">Current Streak: {streak} day{streak === 1 ? '' : 's'}</p>
                        <p className="text-xs text-purple-900">Tip: Finish one pending topic today.</p>
                    </div>
                </div>
            </div>

            {/* Logout Button */}
            <div className="px-4 pt-2 border-t border-pink-100 mt-2">
                <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm text-red-500 hover:bg-red-50 hover:text-red-600 w-full"
                >
                    <LogOut className="w-5 h-5" />
                    Log Out
                </button>
            </div>
        </aside>
    );
};
