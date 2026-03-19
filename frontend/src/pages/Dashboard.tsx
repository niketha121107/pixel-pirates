import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useUserPreferences } from '../context/UserPreferencesContext';
import { PageWrapper } from '../components/layout/PageWrapper';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';

type HubAction = {
    key: string;
    label: string;
    href: string;
    image: string;
    fallback: string;
    bgColor: string;
};

const DASHBOARD_HUB_ACTIONS: HubAction[] = [
    { key: 'notes', label: 'Notes', href: '/notes', image: '/dashboard-icons/notes.svg', fallback: '📝', bgColor: 'bg-amber-100' },
    { key: 'chat', label: 'Chatbot', href: '/chat', image: '/dashboard-icons/chatbot.svg', fallback: '🤖', bgColor: 'bg-purple-100' },
    { key: 'mock', label: 'Mock Test', href: '/mock-test', image: '/dashboard-icons/mocktest.svg', fallback: '🎯', bgColor: 'bg-blue-100' },
    { key: 'topics', label: 'Topics', href: '/videos', image: '/dashboard-icons/topics.svg', fallback: '📚', bgColor: 'bg-orange-100' },
];

const Sparkle = ({ x, y, size = 4, delay = 0 }: { x: number; y: number; size?: number; delay?: number }) => (
    <motion.div
        initial={{ opacity: 0.3, scale: 0, x: 0, y: 0 }}
        animate={{ 
            opacity: [0.3, 0.8, 0.3], 
            scale: [0, 1, 0],
            x: [0, 8, 0],
            y: [0, 8, 0]
        }}
        transition={{ duration: 4, delay, repeat: Infinity, ease: "easeInOut" }}
        className="absolute pointer-events-none"
        style={{ left: `${x}%`, top: `${y}%` }}
    >
        <div className={`w-${size} h-${size} bg-yellow-300 rounded-full shadow-lg`} />
    </motion.div>
);

const DecorativeElement = ({ symbol, x, y, delay = 0, scale = 1 }: { symbol: string; x: number; y: number; delay?: number; scale?: number }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 0.6, y: [-10, 10, -10] }}
        transition={{ duration: 4 + delay, delay, repeat: Infinity, ease: "easeInOut" }}
        className="absolute pointer-events-none text-2xl md:text-3xl"
        style={{ left: `${x}%`, top: `${y}%`, transform: `scale(${scale})` }}
    >
        {symbol}
    </motion.div>
);

const ActionTile = ({ action }: { action: HubAction }) => (
    <Link to={action.href} className="group flex flex-col items-center" title={`Open ${action.label}`}>
        <div className={`w-28 h-28 md:w-32 md:h-32 rounded-3xl ${action.bgColor} overflow-hidden group-hover:-translate-y-2 group-hover:scale-[1.1] transition-all duration-300 shadow-lg hover:shadow-2xl flex items-center justify-center border-2 border-white/50 relative`}>
            <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-60 transition-opacity duration-300" style={{
                background: action.bgColor,
                filter: 'blur(12px)'
            }}></div>
            <img
                src={action.image}
                alt={action.label}
                className="w-20 h-20 md:w-24 md:h-24 object-contain group-hover:scale-125 transition-transform duration-300 relative z-10"
                onError={(e) => {
                    const target = e.currentTarget;
                    target.style.display = 'none';
                    const fallback = target.nextElementSibling as HTMLElement | null;
                    if (fallback) fallback.style.display = 'flex';
                }}
            />
            <div style={{ display: 'none' }} className="w-full h-full items-center justify-center text-3xl text-gray-400 relative z-10">
                {action.fallback}
            </div>
        </div>
        <p className="text-center mt-3 text-xs md:text-sm font-semibold text-gray-700 group-hover:text-gray-900 transition-colors">{action.label}</p>
    </Link>
);

export const Dashboard = () => {
    const { user, refreshUser } = useAuth();
    const { preferences } = useUserPreferences();
    const [drawerOpen, setDrawerOpen] = useState(false);

    // Refresh user data when dashboard mounts to show updated profile changes
    useEffect(() => {
        refreshUser().catch(() => {});
    }, [refreshUser]);

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64" withPadding={false}>
                <div className="h-screen pt-20 pb-4 px-3 sm:px-6 lg:px-8 w-full overflow-hidden flex flex-col" style={{ background: preferences.wallpaper.gradient }}>
                    {/* Decorative Background Elements */}
                    <div className="absolute inset-0 overflow-hidden pointer-events-none">
                        <DecorativeElement symbol="⭐" x={8} y={15} delay={0} scale={1.2} />
                        <DecorativeElement symbol="✨" x={92} y={12} delay={0.2} scale={0.9} />
                        <DecorativeElement symbol="❤️" x={15} y={45} delay={0.4} scale={1} />
                        <DecorativeElement symbol="🌿" x={85} y={35} delay={0.6} scale={1.1} />
                        <DecorativeElement symbol="⭐" x={25} y={75} delay={0.8} scale={0.8} />
                        <DecorativeElement symbol="💕" x={75} y={70} delay={1} scale={0.95} />
                        <DecorativeElement symbol="✨" x={50} y={25} delay={1.2} scale={0.8} />
                        <DecorativeElement symbol="📖" x={45} y={85} delay={1.4} scale={1} />
                        <DecorativeElement symbol="⭐" x={70} y={50} delay={1.6} scale={0.7} />
                        <DecorativeElement symbol="💫" x={35} y={60} delay={1.8} scale={0.9} />
                        <DecorativeElement symbol="✨" x={65} y={20} delay={2} scale={0.7} />
                        <DecorativeElement symbol="🌟" x={22} y={90} delay={2.2} scale={1} />
                        <DecorativeElement symbol="💕" x={80} y={25} delay={2.4} scale={0.85} />
                        <DecorativeElement symbol="🌿" x={12} y={65} delay={2.6} scale={0.95} />
                        <DecorativeElement symbol="⭐" x={55} y={65} delay={2.8} scale={0.75} />
                        <Sparkle x={20} y={30} size={3} delay={0} />
                        <Sparkle x={80} y={50} size={2} delay={0.5} />
                        <Sparkle x={40} y={70} size={2.5} delay={1} />
                        <Sparkle x={70} y={15} size={2} delay={1.5} />
                        <Sparkle x={30} y={55} size={2} delay={2} />
                        <Sparkle x={60} y={80} size={2.5} delay={2.5} />
                        <Sparkle x={15} y={75} size={2} delay={3} />
                        <Sparkle x={85} y={65} size={2.5} delay={3.5} />
                    </div>

                    {/* Main Content - Centered Grid Layout */}
                    <div className="relative z-10 flex-1 flex items-center justify-center px-2 sm:px-4">
                        <div className="flex flex-col items-center w-full max-w-6xl">
                            {/* Welcome Message - At Top - Responsive sizing */}
                            <motion.div
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="text-center w-full px-4 mb-4 sm:mb-6 md:mb-8"
                            >
                                <h2 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gray-800">
                                    Welcome back, <span className="text-pink-500">{user?.name?.split(' ')[0] || 'Learner'}</span>! 👋
                                </h2>
                                <p className="text-gray-600 text-xs sm:text-sm md:text-base mt-1 sm:mt-2">
                                    Ready to continue your learning journey?
                                </p>
                            </motion.div>

                            {/* Top Row - 2 Icons - Responsive Gap */}
                            <motion.div 
                                initial={{ opacity: 0, y: -20 }} 
                                animate={{ opacity: 1, y: 0 }} 
                                transition={{ delay: 0.2 }} 
                                className="flex justify-center items-center gap-6 sm:gap-12 md:gap-20 lg:gap-72 w-full flex-wrap mb-3 sm:mb-4 md:mb-6"
                            >
                                <ActionTile action={DASHBOARD_HUB_ACTIONS[0]} />
                                <ActionTile action={DASHBOARD_HUB_ACTIONS[1]} />
                            </motion.div>

                            {/* Center Profile - Responsive sizing */}
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.8 }} 
                                animate={{ opacity: 1, scale: 1 }} 
                                transition={{ delay: 0.3 }}
                                className="my-1 sm:my-2 md:my-2"
                            >
                                <Link to="/profile" title="Open Profile">
                                    <motion.div
                                        className="w-40 h-40 sm:w-48 sm:h-48 md:w-56 md:h-56 lg:w-64 lg:h-64 rounded-full p-2 bg-gradient-to-br from-pink-500 via-rose-400 to-amber-300 shadow-2xl cursor-pointer hover:scale-110 transition-transform duration-300 relative"
                                        animate={{ scale: [1, 1.02, 1] }}
                                        transition={{ duration: 3, repeat: Infinity }}
                                    >
                                        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-500 via-rose-400 to-amber-300 blur-2xl opacity-40 -z-10"></div>
                                        <div className="w-full h-full rounded-full overflow-hidden bg-white">
                                            <img
                                                src={preferences.avatar}
                                                alt="Profile"
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                    </motion.div>
                                </Link>
                            </motion.div>

                            {/* Bottom Row - 2 Icons - Responsive Gap */}
                            <motion.div 
                                initial={{ opacity: 0, y: 20 }} 
                                animate={{ opacity: 1, y: 0 }} 
                                transition={{ delay: 0.2 }} 
                                className="flex justify-center items-center gap-6 sm:gap-12 md:gap-20 lg:gap-72 w-full flex-wrap -mt-1 sm:-mt-1 md:-mt-2"
                            >
                                <ActionTile action={DASHBOARD_HUB_ACTIONS[3]} />
                                <ActionTile action={DASHBOARD_HUB_ACTIONS[2]} />
                            </motion.div>
                        </div>
                    </div>
                </div>
            </PageWrapper>
        </>
    );
};
