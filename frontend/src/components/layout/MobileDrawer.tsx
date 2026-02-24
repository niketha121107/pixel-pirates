import { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Search, BookOpen, Home, X, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MobileDrawerProps {
    isOpen: boolean;
    onClose: () => void;
}

export const MobileDrawer = ({ isOpen, onClose }: MobileDrawerProps) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [query, setQuery] = useState('');
    const [difficulty, setDifficulty] = useState<'easy' | 'difficult'>('easy');
    const [recentSearches] = useState([
        'Python Functions',
        'Java OOP',
        'C Pointers',
        'Data Structures',
    ]);

    const handleSearch = () => {
        if (query.trim()) {
            navigate(`/topic?q=${encodeURIComponent(query.trim())}&difficulty=${difficulty}`);
            onClose();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch();
    };

    const isDashboard = location.pathname === '/dashboard';
    const isProfile = location.pathname === '/profile';

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

                        {/* Dashboard Nav Link */}
                        <div className="px-4 mb-2">
                            <Link
                                to="/dashboard"
                                onClick={onClose}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                                    isDashboard
                                        ? 'bg-brand/10 text-brand border border-brand/20'
                                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                                }`}
                            >
                                <Home className="w-5 h-5" />
                                Dashboard
                            </Link>
                        </div>

                        {/* Profile Nav Link */}
                        <div className="px-4 mb-4">
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

                        <div className="px-4 mb-3">
                            <div className="h-px bg-pink-100" />
                        </div>

                        {/* Search */}
                        <div className="px-4 mb-4">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search topics..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="w-full bg-pink-50/30 border border-pink-100 rounded-xl py-2.5 pl-10 pr-4 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/40 transition-all"
                                />
                            </div>
                        </div>

                        {/* Difficulty Toggle */}
                        <div className="px-4 mb-4">
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Difficulty</p>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setDifficulty('easy')}
                                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                                        difficulty === 'easy'
                                            ? 'bg-candy-mint/50 text-emerald-700 border border-emerald-300'
                                            : 'bg-pink-50/30 text-gray-500 border border-pink-100 hover:bg-pink-50'
                                    }`}
                                >
                                    Easy
                                </button>
                                <button
                                    onClick={() => setDifficulty('difficult')}
                                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                                        difficulty === 'difficult'
                                            ? 'bg-candy-pink/50 text-pink-700 border border-pink-300'
                                            : 'bg-pink-50/30 text-gray-500 border border-pink-100 hover:bg-pink-50'
                                    }`}
                                >
                                    Difficult
                                </button>
                            </div>
                        </div>

                        {/* Recent Searches */}
                        <div className="flex-1 px-4 overflow-y-auto">
                            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Recent Searches</p>
                            <div className="space-y-1">
                                {recentSearches.map((item, i) => (
                                    <motion.button
                                        key={i}
                                        whileHover={{ x: 4 }}
                                        onClick={() => {
                                            navigate(`/topic?q=${encodeURIComponent(item)}&difficulty=${difficulty}`);
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors text-left"
                                    >
                                        <BookOpen className="w-4 h-4 text-gray-400 flex-shrink-0" />
                                        <span className="truncate">{item}</span>
                                    </motion.button>
                                ))}
                            </div>
                        </div>
                    </motion.aside>
                </>
            )}
        </AnimatePresence>
    );
};
