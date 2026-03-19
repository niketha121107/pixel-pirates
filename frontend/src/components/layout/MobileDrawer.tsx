import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { BookOpen, X, User, ClipboardList, Bot, LogOut, StickyNote, TrendingUp, Search, Trash2, LayoutDashboard } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { searchAPI, usersAPI } from '../../services/api';

interface MobileDrawerProps {
    isOpen: boolean;
    onClose: () => void;
}

export const MobileDrawer = ({ isOpen, onClose }: MobileDrawerProps) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { logout } = useAuth();
    const [searchHistory, setSearchHistory] = useState<string[]>([]);
    const [avgScore, setAvgScore] = useState(0);
    const [streak, setStreak] = useState(0);


    const isProfile = location.pathname === '/profile';
    const isDashboard = location.pathname === '/dashboard';
    const isTopics = location.pathname === '/videos';
    const isMockTest = location.pathname === '/mock-test';
    const isChat = location.pathname === '/chat';
    const isNotes = location.pathname === '/notes';
    const isProgress = location.pathname === '/progress';

    const handleLogout = () => {
        logout();
        navigate('/signin');
        onClose();
    };

    useEffect(() => {
        if (!isOpen) return;

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

        searchAPI.recent()
            .then(res => {
                const items = res.data?.data?.searches || [];
                setSearchHistory(items.map((s: any) => typeof s === 'string' ? s : s.query || '').filter(Boolean).slice(0, 4));
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
    }, [isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 lg:hidden"
                    />
                    <motion.aside
                        initial={{ x: '-100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '-100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                        className="fixed inset-y-0 left-0 w-3/4 max-w-xs bg-white border-r border-pink-100 z-50 shadow-2xl flex flex-col py-6 lg:hidden"
                    >
                        {/* Header */}
                        <div className="px-5 flex items-center justify-between mb-4">
                            <Link to="/dashboard" onClick={onClose} className="text-2xl font-bold text-gradient">EduTwin</Link>
                            <button
                                onClick={onClose}
                                className="p-2 text-gray-400 hover:text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Dashboard */}
                        <div className="px-4 mb-2">
                            <Link
                                to="/dashboard"
                                onClick={onClose}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                                    isDashboard
                                        ? 'bg-pink-50 text-pink-600 border border-pink-200'
                                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                                }`}
                            >
                                <LayoutDashboard className="w-5 h-5" />
                                Dashboard
                            </Link>
                        </div>

                        {/* Profile Nav Link */}
                        <div className="px-4 mb-2">
                            <Link
                                to="/profile"
                                onClick={onClose}
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
                                onClick={onClose}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                                    isTopics
                                        ? 'bg-brand/10 text-brand border border-brand/20'
                                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                                }`}
                            >
                                <BookOpen className="w-5 h-5" />
                                Topics
                            </Link>
                        </div>

                        {/* Mock Test */}
                        <div className="px-4 mb-2">
                            <Link
                                to="/mock-test"
                                onClick={onClose}
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
                                onClick={onClose}
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
                                onClick={onClose}
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
                                onClick={onClose}
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

                        {searchHistory.length > 0 && (
                            <div className="px-4 mb-2">
                                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                                    <div className="flex items-center justify-between mb-2">
                                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1">
                                            <Search className="w-3 h-3" /> Recent Searches
                                        </p>
                                        <button
                                            onClick={() => {
                                                searchAPI.clearRecent().catch(() => {});
                                                setSearchHistory([]);
                                            }}
                                            className="text-gray-400 hover:text-red-500"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                    {searchHistory.map((q, i) => (
                                        <p key={`${q}-${i}`} className="text-xs text-gray-700 truncate">• {q}</p>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex-1" />

                        {/* Logout Button */}
                        <div className="px-4 pt-3 border-t border-pink-100 mt-2">
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm text-red-500 hover:bg-red-50 hover:text-red-600 w-full"
                            >
                                <LogOut className="w-5 h-5" />
                                Log Out
                            </button>
                        </div>
                    </motion.aside>
                </>
            )}
        </AnimatePresence>
    );
};
