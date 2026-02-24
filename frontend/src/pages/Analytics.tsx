import { useState } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { StatCard } from '../components/ui/StatCard';
import { GlassCard } from '../components/ui/GlassCard';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { BrainCircuit, BookCheck, AlertTriangle, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export const Analytics = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);

    const data = [
        { name: 'Mon', xp: 120 },
        { name: 'Tue', xp: 300 },
        { name: 'Wed', xp: 250 },
        { name: 'Thu', xp: 450 },
        { name: 'Fri', xp: 390 },
        { name: 'Sat', xp: 600 },
        { name: 'Sun', xp: 800 },
    ];

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-6xl mx-auto space-y-8">

                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Performance Analytics</h1>
                        <p className="text-gray-500">Track your progress and identify areas for improvement.</p>
                    </motion.div>

                    {/* Stats Row */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
                    >
                        <StatCard
                            title="Global Accuracy"
                            value="84%"
                            icon={<Activity className="w-6 h-6" />}
                            trend={{ isPositive: true, value: "2.5%" }}
                        />
                        <StatCard
                            title="Topics Mastered"
                            value="12"
                            icon={<BookCheck className="w-6 h-6" />}
                        />
                        <StatCard
                            title="Total XP Gained"
                            value="8,402"
                            icon={<BrainCircuit className="w-6 h-6" />}
                            trend={{ isPositive: true, value: "850 today" }}
                        />
                        <StatCard
                            title="Weak Areas"
                            value="2"
                            icon={<AlertTriangle className="w-6 h-6 text-status-error" />}
                            className="border-status-error/20"
                        />
                    </motion.div>

                    {/* Charts Row */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                    >
                        <GlassCard className="lg:col-span-2 p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-6">Learning Activity (XP)</h3>
                            <div className="h-[300px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorXp" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="#ec4899" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#fce7f3" />
                                        <XAxis dataKey="name" stroke="#a1a1aa" tickLine={false} axisLine={false} dy={10} />
                                        <YAxis stroke="#a1a1aa" tickLine={false} axisLine={false} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#ffffff', borderColor: '#fce7f3', borderRadius: '12px' }}
                                            itemStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="xp"
                                            stroke="#ec4899"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorXp)"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </GlassCard>

                        <GlassCard className="p-6">
                            <h3 className="text-xl font-bold text-gray-800 mb-6">Weakest Topics</h3>
                            <div className="space-y-4">
                                {[
                                    { title: "Pointer Arithmetic", subject: "C", progress: 25 },
                                    { title: "Red Black Trees", subject: "Java", progress: 40 },
                                    { title: "Async/Await", subject: "JavaScript", progress: 55 }
                                ].map((item, i) => (
                                    <div key={i} className="bg-gray-50 p-4 rounded-xl border border-gray-200">
                                        <div className="flex justify-between text-sm mb-2">
                                            <span className="font-bold text-gray-800">{item.title}</span>
                                            <span className="text-gray-500">{item.subject}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                                            <div className="bg-status-error h-full rounded-full" style={{ width: `${item.progress}%` }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </GlassCard>
                    </motion.div>

                </div>
            </PageWrapper>
        </>
    );
};
