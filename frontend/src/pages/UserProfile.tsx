import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { GlassCard } from '../components/ui/GlassCard';
import { ProfileAvatar } from '../components/profile/ProfileAvatar';
import { WallpaperSettings } from '../components/profile/WallpaperSettings';
import type { WallpaperOption } from '../components/profile/WallpaperSettings';
import { NoteSection, INITIAL_NOTES } from '../components/profile/NoteSection';
import type { Note } from '../components/profile/NoteSection';
import { MotivationalQuotes } from '../components/profile/MotivationalQuotes';
import { useUserPreferences } from '../context/UserPreferencesContext';
import {
    Mail, BookOpen, Trophy, Flame, Target, Calendar,
    Edit3, Save, MapPin, GraduationCap, Code2, Clock, TrendingUp,
    Award, Star, Zap, CheckCircle2, X, ImageIcon, UserCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';

// ─── Mock User Data ───────────────────────────────────────────────────
const USER_STATS = {
    topicsCompleted: 5,
    totalTopics: 12,
    quizzesTaken: 5,
    avgScore: 72,
    streak: 12,
    totalHours: 34,
    joinDate: 'Jan 2026',
    rank: 3,
    badges: [
        { name: 'First Quiz', icon: '🏅', earned: true },
        { name: 'Week Streak', icon: '🔥', earned: true },
        { name: 'Perfect Score', icon: '⭐', earned: true },
        { name: 'Night Owl', icon: '🦉', earned: true },
        { name: 'Speed Demon', icon: '⚡', earned: false },
        { name: 'Completionist', icon: '🏆', earned: false },
        { name: 'Social Learner', icon: '🤝', earned: false },
        { name: 'Top 10', icon: '🥇', earned: false },
    ],
    languages: [
        { name: 'Python', level: 78, color: 'bg-blue-500' },
        { name: 'Java', level: 55, color: 'bg-orange-500' },
        { name: 'C', level: 65, color: 'bg-gray-600' },
        { name: 'SQL', level: 70, color: 'bg-emerald-500' },
        { name: 'JavaScript', level: 30, color: 'bg-yellow-500' },
    ],
};

export const UserProfile = () => {
    const { preferences, savePreferences } = useUserPreferences();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    // Pending (unsaved) selections — initialised from saved prefs
    const [pendingAvatar, setPendingAvatar] = useState(preferences.avatar);
    const [pendingWallpaper, setPendingWallpaper] = useState(preferences.wallpaperId);

    const [notes, setNotes] = useState<Note[]>(INITIAL_NOTES);
    const [profile, setProfile] = useState({
        name: 'Alex Thompson',
        username: '@alexcoder',
        email: 'alex.thompson@university.edu',
        bio: 'CS student passionate about algorithms and web dev. Currently mastering Python and data structures. Always eager to learn something new! 🚀',
        location: 'San Francisco, CA',
        university: 'Stanford University',
        year: '3rd Year CS',
    });
    const [editProfile, setEditProfile] = useState(profile);

    // Detect unsaved changes
    const hasUnsavedChanges = useMemo(
        () => pendingAvatar !== preferences.avatar || pendingWallpaper !== preferences.wallpaperId,
        [pendingAvatar, pendingWallpaper, preferences.avatar, preferences.wallpaperId]
    );

    const handleSaveProfile = () => {
        setProfile(editProfile);
        setIsEditing(false);
    };

    const handleSavePreferences = () => {
        savePreferences(pendingAvatar, pendingWallpaper);
    };

    const handleDiscardPreferences = () => {
        setPendingAvatar(preferences.avatar);
        setPendingWallpaper(preferences.wallpaperId);
    };

    const handleWallpaperChange = (wp: WallpaperOption) => {
        setPendingWallpaper(wp.id);
    };

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64" withPadding={false}>
                {/* ═══ Save Changes Bar ═══ */}
                <AnimatePresence>
                    {hasUnsavedChanges && (
                        <motion.div
                            initial={{ y: -60, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: -60, opacity: 0 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
                            className="fixed top-16 left-0 lg:left-64 right-0 z-30"
                        >
                            <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 pt-2">
                                <div className="flex items-center justify-between gap-4 px-5 py-3 bg-white/95 backdrop-blur-xl border border-brand/30 rounded-2xl shadow-lg">
                                    <div className="flex items-center gap-3">
                                        <div className="w-9 h-9 rounded-xl bg-brand/10 flex items-center justify-center">
                                            <Save className="w-4.5 h-4.5 text-brand" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold text-gray-800">You have unsaved changes</p>
                                            <p className="text-[11px] text-gray-500 flex items-center gap-2">
                                                {pendingAvatar !== preferences.avatar && (
                                                    <span className="flex items-center gap-1"><UserCircle className="w-3 h-3" /> Avatar</span>
                                                )}
                                                {pendingAvatar !== preferences.avatar && pendingWallpaper !== preferences.wallpaperId && (
                                                    <span className="text-gray-300">·</span>
                                                )}
                                                {pendingWallpaper !== preferences.wallpaperId && (
                                                    <span className="flex items-center gap-1"><ImageIcon className="w-3 h-3" /> Wallpaper</span>
                                                )}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={handleDiscardPreferences}
                                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                                        >
                                            <X className="w-4 h-4" />
                                            Discard
                                        </motion.button>
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={handleSavePreferences}
                                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-brand shadow-md hover:shadow-lg transition-shadow"
                                        >
                                            <Save className="w-4 h-4" />
                                            Save Changes
                                        </motion.button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className={`pt-24 pb-12 px-4 sm:px-6 lg:px-8 w-full max-w-6xl mx-auto space-y-6 transition-all ${hasUnsavedChanges ? 'mt-14' : ''}`}>

                    {/* ═══ Profile Header - Snap-style ═══ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <GlassCard className="overflow-hidden">
                            {/* Cover/Banner */}
                            <div className="h-32 sm:h-40 bg-gradient-to-r from-brand via-pink-400 to-orange-400 relative overflow-hidden">
                                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMiIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjEpIi8+PC9zdmc+')] opacity-50" />
                                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black/20 to-transparent" />
                            </div>

                            {/* Profile Info */}
                            <div className="px-6 pb-6 -mt-14 relative">
                                <div className="flex flex-col sm:flex-row sm:items-end gap-4">
                                    <ProfileAvatar currentAvatar={pendingAvatar} onAvatarChange={setPendingAvatar} />

                                    <div className="flex-1 pt-2 sm:pt-0 sm:pb-2">
                                        {isEditing ? (
                                            <div className="space-y-2">
                                                <input
                                                    value={editProfile.name}
                                                    onChange={(e) => setEditProfile({ ...editProfile, name: e.target.value })}
                                                    className="text-xl font-bold text-gray-800 bg-pink-50/50 border border-pink-200 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-brand/30 w-full sm:w-auto"
                                                />
                                                <input
                                                    value={editProfile.username}
                                                    onChange={(e) => setEditProfile({ ...editProfile, username: e.target.value })}
                                                    className="text-sm text-gray-500 bg-pink-50/50 border border-pink-200 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-brand/30 block"
                                                />
                                            </div>
                                        ) : (
                                            <div>
                                                <h1 className="text-2xl font-bold text-gray-800">{profile.name}</h1>
                                                <p className="text-sm text-gray-500 font-medium">{profile.username}</p>
                                            </div>
                                        )}
                                    </div>

                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => isEditing ? handleSaveProfile() : setIsEditing(true)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all self-start sm:self-end ${
                                            isEditing
                                                ? 'bg-brand text-white shadow-md'
                                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        }`}
                                    >
                                        {isEditing ? <><Save className="w-4 h-4" /> Save</> : <><Edit3 className="w-4 h-4" /> Edit Profile</>}
                                    </motion.button>
                                </div>

                                {/* Bio & Details */}
                                <div className="mt-4 space-y-3">
                                    {isEditing ? (
                                        <textarea
                                            value={editProfile.bio}
                                            onChange={(e) => setEditProfile({ ...editProfile, bio: e.target.value })}
                                            rows={2}
                                            className="w-full text-sm text-gray-600 bg-pink-50/50 border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30 resize-none"
                                        />
                                    ) : (
                                        <p className="text-sm text-gray-600 leading-relaxed max-w-xl">{profile.bio}</p>
                                    )}

                                    <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                                        {isEditing ? (
                                            <>
                                                <div className="flex items-center gap-1.5">
                                                    <MapPin className="w-3.5 h-3.5" />
                                                    <input
                                                        value={editProfile.location}
                                                        onChange={(e) => setEditProfile({ ...editProfile, location: e.target.value })}
                                                        className="bg-pink-50/50 border border-pink-200 rounded px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-brand/30"
                                                    />
                                                </div>
                                                <div className="flex items-center gap-1.5">
                                                    <GraduationCap className="w-3.5 h-3.5" />
                                                    <input
                                                        value={editProfile.university}
                                                        onChange={(e) => setEditProfile({ ...editProfile, university: e.target.value })}
                                                        className="bg-pink-50/50 border border-pink-200 rounded px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-brand/30"
                                                    />
                                                </div>
                                                <div className="flex items-center gap-1.5">
                                                    <Mail className="w-3.5 h-3.5" />
                                                    <input
                                                        value={editProfile.email}
                                                        onChange={(e) => setEditProfile({ ...editProfile, email: e.target.value })}
                                                        className="bg-pink-50/50 border border-pink-200 rounded px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-brand/30"
                                                    />
                                                </div>
                                            </>
                                        ) : (
                                            <>
                                                <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> {profile.location}</span>
                                                <span className="flex items-center gap-1.5"><GraduationCap className="w-3.5 h-3.5" /> {profile.university}</span>
                                                <span className="flex items-center gap-1.5"><Code2 className="w-3.5 h-3.5" /> {profile.year}</span>
                                                <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" /> {profile.email}</span>
                                                <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" /> Joined {USER_STATS.joinDate}</span>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* ═══ Stats Row ═══ */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3"
                    >
                        {[
                            { label: 'Topics Done', value: USER_STATS.topicsCompleted, icon: <BookOpen className="w-4 h-4" />, color: 'text-brand', bg: 'bg-brand/10' },
                            { label: 'Avg Score', value: `${USER_STATS.avgScore}%`, icon: <Target className="w-4 h-4" />, color: 'text-emerald-600', bg: 'bg-emerald-50' },
                            { label: 'Day Streak', value: USER_STATS.streak, icon: <Flame className="w-4 h-4" />, color: 'text-orange-600', bg: 'bg-orange-50' },
                            { label: 'Study Hours', value: USER_STATS.totalHours, icon: <Clock className="w-4 h-4" />, color: 'text-blue-600', bg: 'bg-blue-50' },
                            { label: 'Quizzes', value: USER_STATS.quizzesTaken, icon: <CheckCircle2 className="w-4 h-4" />, color: 'text-purple-600', bg: 'bg-purple-50' },
                            { label: 'Rank', value: `#${USER_STATS.rank}`, icon: <Trophy className="w-4 h-4" />, color: 'text-yellow-600', bg: 'bg-yellow-50' },
                        ].map((stat) => (
                            <GlassCard key={stat.label} className="p-4" interactive>
                                <div className={`w-8 h-8 rounded-lg ${stat.bg} flex items-center justify-center ${stat.color} mb-2`}>
                                    {stat.icon}
                                </div>
                                <p className="text-xl font-bold text-gray-800">{stat.value}</p>
                                <p className="text-[11px] text-gray-500 font-medium">{stat.label}</p>
                            </GlassCard>
                        ))}
                    </motion.div>

                    {/* ═══ Two Column Layout ═══ */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Left Column: Badges + Language Skills */}
                        <div className="lg:col-span-1 space-y-6">
                            {/* Badges */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                                <GlassCard className="p-6">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 to-amber-400 flex items-center justify-center">
                                            <Award className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-800">Badges</h3>
                                            <p className="text-xs text-gray-500">{USER_STATS.badges.filter(b => b.earned).length}/{USER_STATS.badges.length} earned</p>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-4 gap-2">
                                        {USER_STATS.badges.map((badge) => (
                                            <motion.div
                                                key={badge.name}
                                                whileHover={{ scale: 1.1, y: -2 }}
                                                className={`flex flex-col items-center p-2 rounded-xl transition-all ${
                                                    badge.earned
                                                        ? 'bg-yellow-50 border border-yellow-200'
                                                        : 'bg-gray-50 border border-gray-200 opacity-40 grayscale'
                                                }`}
                                                title={badge.name}
                                            >
                                                <span className="text-2xl">{badge.icon}</span>
                                                <span className="text-[9px] text-gray-600 font-medium mt-1 text-center leading-tight">{badge.name}</span>
                                            </motion.div>
                                        ))}
                                    </div>
                                </GlassCard>
                            </motion.div>

                            {/* Language Skills */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                                <GlassCard className="p-6">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center">
                                            <Code2 className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-800">Language Skills</h3>
                                            <p className="text-xs text-gray-500">Your proficiency levels</p>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        {USER_STATS.languages.map((lang) => (
                                            <div key={lang.name}>
                                                <div className="flex justify-between mb-1">
                                                    <span className="text-xs font-semibold text-gray-700">{lang.name}</span>
                                                    <span className="text-xs text-gray-500">{lang.level}%</span>
                                                </div>
                                                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${lang.level}%` }}
                                                        transition={{ duration: 1, delay: 0.5 }}
                                                        className={`h-full rounded-full ${lang.color}`}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </GlassCard>
                            </motion.div>

                            {/* Motivational Quotes */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                                <MotivationalQuotes />
                            </motion.div>
                        </div>

                        {/* Right Column: Notes + Wallpaper */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Wallpaper Settings */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                                <WallpaperSettings currentWallpaper={pendingWallpaper} onWallpaperChange={handleWallpaperChange} />
                            </motion.div>

                            {/* Notes Section */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                                <NoteSection notes={notes} onNotesChange={setNotes} />
                            </motion.div>
                        </div>
                    </div>

                    {/* ═══ Quick Links ═══ */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.35 }}
                    >
                        <GlassCard className="p-6">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                <Zap className="w-5 h-5 text-brand" />
                                Quick Actions
                            </h3>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                {[
                                    { label: 'Dashboard', to: '/dashboard', icon: <TrendingUp className="w-5 h-5" />, color: 'from-brand to-pink-400' },
                                    { label: 'Leaderboard', to: '/leaderboard', icon: <Trophy className="w-5 h-5" />, color: 'from-yellow-400 to-amber-400' },
                                    { label: 'Analytics', to: '/analytics', icon: <Target className="w-5 h-5" />, color: 'from-blue-400 to-indigo-400' },
                                    { label: 'Progress', to: '/progress', icon: <Star className="w-5 h-5" />, color: 'from-emerald-400 to-teal-400' },
                                ].map((action) => (
                                    <Link key={action.label} to={action.to}>
                                        <motion.div
                                            whileHover={{ scale: 1.03, y: -2 }}
                                            whileTap={{ scale: 0.97 }}
                                            className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-white border border-gray-100 hover:border-brand/20 hover:shadow-sm transition-all cursor-pointer"
                                        >
                                            <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center text-white flex-shrink-0`}>
                                                {action.icon}
                                            </div>
                                            <span className="text-sm font-medium text-gray-700">{action.label}</span>
                                        </motion.div>
                                    </Link>
                                ))}
                            </div>
                        </GlassCard>
                    </motion.div>

                </div>
            </PageWrapper>
        </>
    );
};
