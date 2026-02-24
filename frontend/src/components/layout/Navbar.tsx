import { Bell, Home, User, CheckCheck, Trash2, Clock, PartyPopper, Info } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useUserPreferences } from '../../context/UserPreferencesContext';
import { useNotifications } from '../../context/NotificationContext';
import type { NotificationType } from '../../context/NotificationContext';

const typeStyles: Record<NotificationType, { icon: typeof Clock; bg: string; color: string }> = {
    reminder: { icon: Clock, bg: 'bg-amber-100', color: 'text-amber-600' },
    congrats: { icon: PartyPopper, bg: 'bg-green-100', color: 'text-green-600' },
    info:     { icon: Info, bg: 'bg-blue-100', color: 'text-blue-600' },
};

function timeAgo(ts: number) {
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60_000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
}

export const Navbar = ({ onMenuClick }: { onMenuClick: () => void }) => {
    const { preferences } = useUserPreferences();
    const { notifications, unreadCount, markAsRead, markAllAsRead, clearAll } = useNotifications();
    const [showNotifications, setShowNotifications] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setShowNotifications(false);
            }
        };
        if (showNotifications) document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [showNotifications]);

    return (
        <nav className="fixed w-full z-40 glass-panel h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
                <button
                    onClick={onMenuClick}
                    className="lg:hidden p-2 -ml-2 text-gray-500 hover:text-gray-800 transition-colors"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                </button>
                <Link to="/dashboard" className="text-2xl font-bold tracking-tighter">
                    <span className="text-gradient hover:opacity-80 transition-opacity cursor-pointer">EduTwin</span>
                </Link>
            </div>

            <div className="flex items-center gap-3">
                <Link to="/dashboard">
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand/5 text-brand hover:bg-brand/10 transition-colors font-medium text-sm"
                    >
                        <Home className="w-4 h-4" />
                        <span className="hidden sm:inline">Dashboard</span>
                    </motion.button>
                </Link>

                <Link to="/profile">
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-purple-50 text-purple-600 hover:bg-purple-100 transition-colors font-medium text-sm"
                    >
                        <User className="w-4 h-4" />
                        <span className="hidden sm:inline">Profile</span>
                    </motion.button>
                </Link>

                {/* Notification Bell + Dropdown */}
                <div className="relative" ref={dropdownRef}>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setShowNotifications(prev => !prev)}
                        className="relative p-2 text-gray-500 hover:text-gray-800 transition-colors"
                    >
                        <Bell className="w-5 h-5" />
                        {unreadCount > 0 && (
                            <span className="absolute top-0.5 right-0.5 min-w-[18px] h-[18px] flex items-center justify-center bg-status-error rounded-full text-[10px] font-bold text-white leading-none px-1">
                                {unreadCount > 9 ? '9+' : unreadCount}
                            </span>
                        )}
                    </motion.button>

                    <AnimatePresence>
                        {showNotifications && (
                            <motion.div
                                initial={{ opacity: 0, y: -8, scale: 0.95 }}
                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                exit={{ opacity: 0, y: -8, scale: 0.95 }}
                                transition={{ duration: 0.15 }}
                                className="absolute right-0 top-12 w-[360px] max-h-[480px] bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden z-50"
                            >
                                {/* Header */}
                                <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50">
                                    <div>
                                        <h3 className="font-bold text-gray-800 text-sm">Notifications</h3>
                                        {unreadCount > 0 && (
                                            <p className="text-xs text-gray-500">{unreadCount} unread</p>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {unreadCount > 0 && (
                                            <button
                                                onClick={markAllAsRead}
                                                className="flex items-center gap-1 text-xs text-brand hover:text-brand/80 font-medium"
                                            >
                                                <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                                            </button>
                                        )}
                                        {notifications.length > 0 && (
                                            <button
                                                onClick={clearAll}
                                                className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 font-medium"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                {/* Notification List */}
                                <div className="overflow-y-auto max-h-[400px] divide-y divide-gray-50">
                                    {notifications.length === 0 ? (
                                        <div className="py-12 text-center text-gray-400">
                                            <Bell className="w-8 h-8 mx-auto mb-2 opacity-40" />
                                            <p className="text-sm">No notifications yet</p>
                                        </div>
                                    ) : (
                                        notifications.map(n => {
                                            const style = typeStyles[n.type];
                                            const Icon = style.icon;
                                            return (
                                                <button
                                                    key={n.id}
                                                    onClick={() => markAsRead(n.id)}
                                                    className={`w-full text-left px-4 py-3 flex gap-3 hover:bg-gray-50 transition-colors ${
                                                        !n.read ? 'bg-brand/[0.03]' : ''
                                                    }`}
                                                >
                                                    <div className={`flex-shrink-0 w-9 h-9 rounded-xl ${style.bg} flex items-center justify-center`}>
                                                        <Icon className={`w-4.5 h-4.5 ${style.color}`} />
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center gap-2">
                                                            <p className={`text-sm font-semibold truncate ${!n.read ? 'text-gray-800' : 'text-gray-600'}`}>
                                                                {n.title}
                                                            </p>
                                                            {!n.read && (
                                                                <span className="flex-shrink-0 w-2 h-2 bg-brand rounded-full" />
                                                            )}
                                                        </div>
                                                        <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{n.message}</p>
                                                        <p className="text-[10px] text-gray-400 mt-1">{timeAgo(n.timestamp)}</p>
                                                    </div>
                                                </button>
                                            );
                                        })
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <Link to="/profile">
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="w-8 h-8 rounded-full bg-gradient-brand p-[2px] cursor-pointer"
                    >
                        <div className="w-full h-full rounded-full bg-brand-surface border-[1.5px] border-transparent flex items-center justify-center text-sm font-bold text-white overflow-hidden">
                            <img src={preferences.avatar} alt="User avatar" />
                        </div>
                    </motion.div>
                </Link>
            </div>
        </nav>
    );
};
