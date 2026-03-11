import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { leaderboardAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { Trophy, Medal, Crown } from 'lucide-react';
import { motion } from 'framer-motion';

const badgeFromRank = (rank: number) => {
    if (rank === 1) return 'Diamond';
    if (rank === 2) return 'Platinum';
    if (rank <= 4) return 'Gold';
    return 'Silver';
};

export const Leaderboard = () => {
    const { user } = useAuth();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [leaderboardData, setLeaderboardData] = useState<{ rank: number; name: string; xp: number; badge: string; isCurrentUser: boolean }[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        leaderboardAPI.top(10)
            .then(res => {
                const entries = (res.data?.data?.topUsers || []).map((u: any) => ({
                    rank: u.rank,
                    name: u.userId === user?.id ? `${u.name} (You)` : u.name,
                    xp: u.score,
                    badge: badgeFromRank(u.rank),
                    isCurrentUser: u.userId === user?.id,
                }));
                setLeaderboardData(entries);
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [user]);

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-4xl mx-auto space-y-8">

                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="text-center sm:text-left flex items-center gap-4">
                        <div className="p-4 bg-brand/20 rounded-2xl text-brand hidden sm:block">
                            <Trophy className="w-10 h-10" />
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Global Leaderboard</h1>
                            <p className="text-gray-500">Compete with learners worldwide. Climb the ranks.</p>
                        </div>
                    </motion.div>

                    <GlassCard className="p-2 sm:p-6">
                        <div className="space-y-3">
                            {leaderboardData.map((user, idx) => (
                                <motion.div
                                    key={user.rank}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className={`flex items-center justify-between p-4 sm:px-6 rounded-xl border transition-all ${
                                        user.isCurrentUser
                                            ? 'bg-brand/5 border-brand/30 shadow-md'
                                            : 'bg-pink-50/30 border-pink-100 hover:border-pink-200'
                                    }`}
                                >
                                    <div className="flex items-center gap-4 sm:gap-6">
                                        <div className="w-8 flex justify-center font-bold text-lg">
                                            {user.rank === 1 && <Crown className="w-6 h-6 text-yellow-400" />}
                                            {user.rank === 2 && <Medal className="w-6 h-6 text-gray-300" />}
                                            {user.rank === 3 && <Medal className="w-6 h-6 text-orange-400" />}
                                            {user.rank > 3 && <span className="text-gray-500">#{user.rank}</span>}
                                        </div>

                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-full bg-gradient-brand p-[2px]">
                                                <div className="w-full h-full rounded-full bg-brand-surface border-[1.5px] border-transparent flex items-center justify-center text-sm font-bold text-white overflow-hidden">
                                                    <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}&backgroundColor=b6e3f4`} alt={user.name} />
                                                </div>
                                            </div>
                                            <div className="flex flex-col">
                                                <span className={`font-bold ${user.isCurrentUser ? 'text-brand' : 'text-gray-800'}`}>
                                                    {user.name}
                                                </span>
                                                <span className="text-xs text-brand/70 font-semibold">{user.badge}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="text-right">
                                        <span className="font-bold text-gray-800 text-lg">{user.xp}</span>
                                        <span className="text-xs text-gray-500 ml-1">XP</span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </GlassCard>

                </div>
            </PageWrapper>
        </>
    );
};
