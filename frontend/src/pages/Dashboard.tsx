import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useApp } from '../context/AppContext';
import { topics } from '../data/mockData';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

function AnimatedNumber({ target, duration = 1200 }: { target: number; duration?: number }) {
    const [val, setVal] = useState(0);
    const ref = useRef<HTMLSpanElement>(null);
    useEffect(() => {
        let start = 0;
        const step = (ts: number) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / duration, 1);
            setVal(Math.floor(progress * target));
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }, [target, duration]);
    return <span ref={ref}>{val}</span>;
}

export default function Dashboard() {
    const { user } = useAuth();
    const { completedTopics, pendingTopics, videosWatched, leaderboard, getTopicStatus } = useApp();
    const navigate = useNavigate();

    if (!user) return null;

    const currentUserRank = leaderboard.find(l => l.userId === user.id)?.rank ?? '-';
    const currentUser = {
        ...user,
        completedTopics: completedTopics,
        pendingTopics: pendingTopics,
        videosWatched: videosWatched,
        rank: currentUserRank,
    };

    const topicsByStatus = topics.reduce((acc, topic) => {
        const status = getTopicStatus(topic.id);
        if (!acc[status]) {
            acc[status] = [];
        }
        acc[status].push(topic);
        return acc;
    }, {} as Record<string, typeof topics>);

    return (
        <motion.div variants={container} initial="hidden" animate="show" className="space-y-8 pb-8">
            {/* Welcome Section */}
            <motion.div variants={item}>
                <div className="mb-10 animate-fade-in">
                    <h1 className="text-4xl md:text-5xl font-bold font-display tracking-tight text-slate-800 mb-2">
                        Welcome back, <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">{currentUser.name}</span> <span className="inline-block animate-wave origin-bottom-right">👋</span>
                    </h1>
                    <p className="text-lg text-slate-500 font-medium tracking-wide">Track your progress, learn adaptively, and climb the leaderboard.</p>
                </div>
            </motion.div>

            {/* Progress Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Topics Completed" value={currentUser.completedTopics.length} icon="✅" color="text-success" bg="bg-success/10" border="border-success/20" />
                <StatCard title="Topics Pending" value={currentUser.pendingTopics.length} icon="⏳" color="text-warning" bg="bg-warning/10" border="border-warning/20" />
                <StatCard title="Videos Watched" value={currentUser.videosWatched.length} icon="📺" color="text-accent" bg="bg-accent/10" border="border-accent/20" />
                <StatCard title="Current Rank" value={`#${currentUser.rank}`} icon="🏆" color="text-primary" bg="bg-primary/10" border="border-primary/20" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 pt-4">
                {/* Left Column: Flow */}
                <div className="lg:col-span-8 xl:col-span-9 space-y-8">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold font-display text-slate-800 flex items-center gap-2">
                            <span className="text-2xl">📚</span> Your Flow
                        </h2>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                        {Object.entries(topicsByStatus).map(([status, ts]) => (
                            ts.map(topic => (
                                <Link key={topic.id} to={`/topic/${topic.id}`}>
                                    <motion.div
                                        whileHover={{ y: -4, scale: 1.01 }}
                                        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                                        className="glass-card rounded-2xl p-6 h-full flex flex-col justify-between group hover:border-primary/30 transition-all duration-300"
                                    >
                                        <div>
                                            <div className="flex justify-between items-start mb-4">
                                                <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider
                                                    ${status === 'completed' ? 'bg-success/10 text-success' :
                                                        status === 'in-progress' ? 'bg-warning/10 text-warning' :
                                                            'bg-slate-100 text-slate-500'}`}
                                                >
                                                    {topic.language}
                                                </span>
                                                <StatusBadge status={status as any} />
                                            </div>
                                            <h3 className="text-xl font-bold font-display text-slate-800 mb-2 group-hover:text-primary transition-colors">{topic.topicName}</h3>
                                            <p className="text-slate-500 text-sm line-clamp-2 leading-relaxed">{topic.overview}</p>
                                        </div>
                                        <div className="mt-6 flex items-center justify-between text-xs font-medium text-slate-400">
                                            <span>{topic.difficulty}</span>
                                            <span className="flex items-center gap-1.5">
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                {topic.quiz.length} questions
                                            </span>
                                        </div>
                                    </motion.div>
                                </Link>
                            ))
                        ))}
                    </div>

                    {/* Recently Watched */}
                    <div className="mt-4">
                        <h2 className="text-2xl font-bold font-display text-slate-800 flex items-center gap-2 mb-6">
                            <span className="text-2xl">📺</span> Keep Exploring
                        </h2>
                        {currentUser.videosWatched.length > 0 ? (
                            <div className="flex overflow-x-auto gap-5 pb-6 snap-x hide-scrollbar mask-edges">
                                {currentUser.videosWatched.slice().reverse().map((video, idx) => (
                                    <motion.div
                                        key={`${video.id}-${idx}`}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                        className="flex-none w-72 glass-card rounded-2xl overflow-hidden snap-start group cursor-pointer hover:border-primary/20 transition-colors"
                                    >
                                        <div className="relative h-40 overflow-hidden">
                                            <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                                                <div className="w-12 h-12 rounded-full bg-primary/90 flex items-center justify-center text-white shadow-lg backdrop-blur-sm transform scale-75 group-hover:scale-100 transition-transform duration-300">
                                                    <svg className="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
                                                </div>
                                            </div>
                                            <span className="absolute bottom-2 right-2 bg-black/70 backdrop-blur-md text-white text-xs font-bold px-2 py-1 rounded-md">
                                                {video.duration}
                                            </span>
                                        </div>
                                        <div className="p-4">
                                            <h4 className="font-bold font-display text-slate-800 text-sm line-clamp-1 group-hover:text-primary transition-colors">{video.title}</h4>
                                            <p className="text-slate-500 text-xs mt-1.5">{video.language}</p>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        ) : (
                            <div className="glass-card p-10 rounded-2xl text-center">
                                <p className="text-slate-500 text-sm font-medium">No videos watched yet. Start learning a topic!</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: Leaderboard */}
                <div className="lg:col-span-4 xl:col-span-3">
                    <div className="sticky top-28 glass-card rounded-3xl p-6 shadow-lg border border-slate-100/50">
                        <h2 className="text-2xl font-bold font-display text-slate-800 flex items-center gap-2 mb-6">
                            <span className="text-2xl">🏆</span> Top Performers
                        </h2>

                        <div className="space-y-3">
                            <div className="grid grid-cols-12 gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider px-4 mb-2">
                                <div className="col-span-2">Rank</div>
                                <div className="col-span-6">Student</div>
                                <div className="col-span-2 text-right">Score</div>
                                <div className="col-span-2 text-right">TP</div>
                            </div>

                            {leaderboard.map((entry, idx) => {
                                const isCurrentUser = entry.userId === currentUser.id;
                                return (
                                    <motion.div
                                        key={entry.userId}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                        className={`grid grid-cols-12 gap-2 items-center p-3 rounded-2xl text-sm font-medium transition-colors
                                            ${isCurrentUser
                                                ? 'bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 shadow-sm shadow-primary/5'
                                                : 'hover:bg-slate-50/80 border border-transparent'}`}
                                    >
                                        <div className="col-span-2 flex items-center">
                                            {idx < 3 ? (
                                                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold font-display shadow-sm
                                                    ${idx === 0 ? 'bg-amber-100 text-amber-700 border-amber-200' :
                                                        idx === 1 ? 'bg-slate-200 text-slate-700 border-slate-300' :
                                                            'bg-orange-100 text-orange-800 border-orange-200'} border`}
                                                >
                                                    {idx + 1}
                                                </div>
                                            ) : (
                                                <div className="w-8 h-8 rounded-full flex items-center justify-center text-slate-500 font-bold font-display">
                                                    {idx + 1}
                                                </div>
                                            )}
                                        </div>

                                        <div className="col-span-6 flex items-center gap-3 w-full min-w-0">
                                            <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex-shrink-0 flex items-center justify-center text-lg">
                                                {entry.avatar}
                                            </div>
                                            <div className="flex flex-col min-w-0">
                                                <span className={`font-bold font-display truncate ${isCurrentUser ? 'text-primary' : 'text-slate-800'}`}>
                                                    {entry.name}
                                                </span>
                                                {isCurrentUser && <span className="text-[10px] font-bold text-primary uppercase tracking-widest leading-none mt-0.5">You</span>}
                                            </div>
                                        </div>

                                        <div className="col-span-2 text-right font-display font-bold text-slate-700">
                                            {entry.score}
                                        </div>

                                        <div className="col-span-2 text-right font-display text-slate-500">
                                            {entry.topicsCompleted}
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                        <div className="mt-8 text-center border-t border-slate-100 pt-6">
                            <p className="text-xs text-slate-400 font-medium">Keep learning to climb the ranks!</p>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

function StatCard({ title, value, icon, color, bg, border }: { title: string, value: string | number, icon: string, color: string, bg: string, border: string }) {
    return (
        <motion.div
            whileHover={{ y: -4, scale: 1.02 }}
            className={`glass-card rounded-3xl p-6 ${border} hover:border-primary/20 transition-all duration-300 relative overflow-hidden group`}
        >
            <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full ${bg} blur-2xl group-hover:bg-primary/20 transition-colors duration-500`} />
            <div className="relative z-10">
                <div className={`w-12 h-12 rounded-2xl ${bg} flex items-center justify-center text-2xl mb-4 shadow-sm`}>
                    {icon}
                </div>
                <h3 className="text-4xl font-bold font-display text-slate-800 mb-1">
                    {typeof value === 'number' ? <AnimatedNumber target={value} /> : value}
                </h3>
                <p className="text-sm font-medium text-slate-500">{title}</p>
            </div>
        </motion.div>
    );
}

function StatusBadge({ status }: { status: 'completed' | 'in-progress' | 'pending' }) {
    switch (status) {
        case 'completed': return <span className="flex items-center gap-1 text-[11px] font-bold text-success bg-success/10 px-2.5 py-1 rounded-lg uppercase tracking-wide"><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg> Completed</span>;
        case 'in-progress': return <span className="flex items-center gap-1 text-[11px] font-bold text-warning bg-warning/10 px-2.5 py-1 rounded-lg uppercase tracking-wide"><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> In Progress</span>;
        default: return <span className="flex items-center gap-1 text-[11px] font-bold text-slate-400 bg-slate-100 px-2.5 py-1 rounded-lg uppercase tracking-wide"><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg> Pending</span>;
    }
}
