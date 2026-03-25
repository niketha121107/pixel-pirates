import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { usersAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { GlassCard } from '../components/ui/GlassCard';
import { ProfileAvatar } from '../components/profile/ProfileAvatar';
import { WallpaperSettings } from '../components/profile/WallpaperSettings';
import type { WallpaperOption } from '../components/profile/WallpaperSettings';
import { MotivationalQuotes } from '../components/profile/MotivationalQuotes';
import { useUserPreferences } from '../context/UserPreferencesContext';
import {
    Mail, BookOpen, Trophy, Flame, Target, Calendar,
    Edit3, Save, MapPin, GraduationCap, Code2, Clock, TrendingUp,
    Award, Star, Zap, CheckCircle2, X, ImageIcon, UserCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const UserProfile = () => {
    const { user } = useAuth();
    const { preferences, savePreferences } = useUserPreferences();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [USER_STATS, setUserStats] = useState({
        topicsCompleted: 0,
        totalTopics: 0,
        quizzesTaken: 0,
        avgScore: 0,
        streak: 0,
        totalHours: 0,
        joinDate: '',
        rank: 0,
        badges: [] as { name: string; icon: string; earned: boolean }[],
        languages: [] as { name: string; level: number; color: string }[],
    });

    // Pending (unsaved) selections — initialised from saved prefs
    const [pendingAvatar, setPendingAvatar] = useState(preferences.avatar);
    const [pendingWallpaper, setPendingWallpaper] = useState(preferences.wallpaperId);


    const [profile, setProfile] = useState({
        name: user?.name || '',
        username: `@${(user?.name || '').toLowerCase().replace(/\s+/g, '')}`,
        email: user?.email || '',
        bio: '',
        location: '',
        university: '',
        year: '',
    });
    const [editProfile, setEditProfile] = useState(profile);

    useEffect(() => {
        usersAPI.stats()
            .then(res => {
                const s = res.data?.data?.stats;
                if (s) {
                    setUserStats(prev => ({
                        ...prev,
                        topicsCompleted: s.topicsCompleted ?? 0,
                        totalTopics: s.totalTopics ?? 0,
                        quizzesTaken: s.quizzesTaken ?? 0,
                        avgScore: s.avgScore ?? 0,
                        streak: s.streak ?? 0,
                        totalHours: s.totalHours ?? 0,
                        joinDate: s.joinDate || '',
                        rank: s.rank ?? 0,
                        badges: Array.isArray(s.badges) ? s.badges : prev.badges,
                        languages: Array.isArray(s.languages) ? s.languages : prev.languages,
                    }));
                }
            })
            .catch(() => {});

        usersAPI.profile()
            .then(res => {
                const p = res.data?.data?.user;
                if (p) {
                    const updatedProfile = {
                        name: p.name || user?.name || '',
                        username: p.username || `@${(user?.name || '').toLowerCase().replace(/\s+/g, '')}`,
                        email: p.email || user?.email || '',
                        bio: p.bio || '',
                        location: p.location || '',
                        university: p.university || '',
                        year: p.year || '',
                    };
                    setProfile(updatedProfile);
                    setEditProfile(updatedProfile);
                }
            })
            .catch(() => {});
    }, []);

    // Detect unsaved changes
    const hasUnsavedChanges = useMemo(
        () => pendingAvatar !== preferences.avatar || pendingWallpaper !== preferences.wallpaperId,
        [pendingAvatar, pendingWallpaper, preferences.avatar, preferences.wallpaperId]
    );

    const handleSaveProfile = async () => {
        try {
            await usersAPI.updateProfile({
                name: editProfile.name,
                username: editProfile.username,
                bio: editProfile.bio,
                location: editProfile.location,
                university: editProfile.university,
                year: editProfile.year,
            });
            setProfile(editProfile);
        } catch {
            // Fallback to local update
            setProfile(editProfile);
        }
        setIsEditing(false);
    };

    const handleCancelEditing = () => {
        setEditProfile(profile);
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

                    {/* ═══ Welcome Greeting ═══ */}
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                        <GlassCard className="p-6 bg-gradient-to-r from-brand/5 via-pink-50 to-orange-50">
                            <h1 className="text-2xl md:text-3xl font-bold text-gray-800">
                                Welcome back, <span className="text-gradient">{user?.name?.split(' ')[0] || 'Learner'}</span>! 👋
                            </h1>
                            <p className="text-gray-500 mt-1">Great to see you again. Keep up the amazing learning streak!</p>
                        </GlassCard>
                    </motion.div>

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
                                        <div>
                                            <h1 className="text-2xl font-bold text-gray-800">{profile.name}</h1>
                                            <p className="text-sm text-gray-500 font-medium">{profile.username}</p>
                                        </div>
                                    </div>

                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => setIsEditing(true)}
                                        disabled={isEditing}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all self-start sm:self-end ${
                                            isEditing
                                                ? 'bg-brand/20 text-brand cursor-default'
                                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        }`}
                                    >
                                        {isEditing ? <><Edit3 className="w-4 h-4" /> Editing...</> : <><Edit3 className="w-4 h-4" /> Edit Profile</>}
                                    </motion.button>
                                </div>

                                {/* Bio & Details */}
                                <div className="mt-4 space-y-3">
                                    <p className="text-sm text-gray-600 leading-relaxed max-w-xl">{profile.bio}</p>

                                    <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                                        <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5" /> {profile.location}</span>
                                        <span className="flex items-center gap-1.5"><GraduationCap className="w-3.5 h-3.5" /> {profile.university}</span>
                                        <span className="flex items-center gap-1.5"><Code2 className="w-3.5 h-3.5" /> {profile.year}</span>
                                        <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" /> {profile.email}</span>
                                        <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" /> Joined {USER_STATS.joinDate}</span>
                                    </div>
                                </div>

                                {/* Edit box below profile pic/header */}
                                <AnimatePresence>
                                    {isEditing && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 8 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: 8 }}
                                            className="mt-5 rounded-2xl border border-pink-200 bg-pink-50/40 p-4 sm:p-5"
                                        >
                                            <h3 className="text-sm font-bold text-gray-800 mb-3">Edit Profile</h3>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                                <input
                                                    value={editProfile.name}
                                                    onChange={(e) => setEditProfile({ ...editProfile, name: e.target.value })}
                                                    placeholder="Name"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                                <input
                                                    value={editProfile.username}
                                                    onChange={(e) => setEditProfile({ ...editProfile, username: e.target.value })}
                                                    placeholder="Username"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                                <input
                                                    value={editProfile.location}
                                                    onChange={(e) => setEditProfile({ ...editProfile, location: e.target.value })}
                                                    placeholder="Location"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                                <input
                                                    value={editProfile.university}
                                                    onChange={(e) => setEditProfile({ ...editProfile, university: e.target.value })}
                                                    placeholder="University"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                                <input
                                                    value={editProfile.year}
                                                    onChange={(e) => setEditProfile({ ...editProfile, year: e.target.value })}
                                                    placeholder="Year"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                                <input
                                                    value={editProfile.email}
                                                    onChange={(e) => setEditProfile({ ...editProfile, email: e.target.value })}
                                                    placeholder="Email"
                                                    className="text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                                />
                                            </div>
                                            <textarea
                                                value={editProfile.bio}
                                                onChange={(e) => setEditProfile({ ...editProfile, bio: e.target.value })}
                                                rows={3}
                                                placeholder="Bio"
                                                className="mt-3 w-full text-sm bg-white border border-pink-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand/30 resize-none"
                                            />
                                            <div className="mt-4 flex items-center justify-end gap-2">
                                                <button
                                                    onClick={handleCancelEditing}
                                                    className="px-4 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200"
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    onClick={handleSaveProfile}
                                                    className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-brand hover:bg-brand/90"
                                                >
                                                    <Save className="w-4 h-4" /> Save
                                                </button>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* ═══ Stats Row ═══ */}
                    {/* Stats removed as per user request */}

                    {/* ═══ Two Column Layout ═══ */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Left Column: Badges + Language Skills */}
                        <div className="lg:col-span-1 space-y-6">
                            {/* Motivational Quotes */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                                <MotivationalQuotes streak={USER_STATS.streak} />
                            </motion.div>
                        </div>

                        {/* Right Column: Notes + Wallpaper */}
                        <div className="lg:col-span-2 space-y-6">
                            {/* Wallpaper Settings */}
                            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                                <WallpaperSettings currentWallpaper={pendingWallpaper} onWallpaperChange={handleWallpaperChange} />
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
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                {[
                                    { label: 'Topics', to: '/videos', icon: <BookOpen className="w-5 h-5" />, color: 'from-brand to-pink-400' },
                                    { label: 'Notes', to: '/notes', icon: <Star className="w-5 h-5" />, color: 'from-yellow-400 to-amber-400' },
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
