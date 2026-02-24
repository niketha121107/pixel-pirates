import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp } from '../context/AppContext';
import { useAuth } from '../context/AuthContext';
import { topics } from '../data/mockData';
import { Video, ExplanationStyle } from '../types';

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function TopicPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { user } = useAuth();
    const { markVideoWatched, startTopic, preferredStyle, setPreferredStyle } = useApp();

    const topic = topics.find(t => t.id === id);
    const [selectedStyle, setSelectedStyle] = useState<ExplanationStyle>(preferredStyle);
    const [isChangingStyle, setIsChangingStyle] = useState(false);

    useEffect(() => {
        if (topic) {
            startTopic(topic.id);
        }
        window.scrollTo(0, 0);
    }, [topic, startTopic]);

    if (!topic) {
        return <div className="p-8 text-center text-slate-500">Topic not found</div>;
    }

    const explanation = topic.explanations.find(e => e.style === selectedStyle);

    const handleStyleChange = (style: ExplanationStyle) => {
        if (style === selectedStyle) return;
        setIsChangingStyle(true);
        setPreferredStyle(style);
        setTimeout(() => {
            setSelectedStyle(style);
            setIsChangingStyle(false);
        }, 400); // Wait for exit animation
    };

    const handleVideoWatch = (video: Video) => {
        markVideoWatched({
            ...video,
            watchedAt: new Date().toISOString(),
            timeWatched: video.duration
        });
    };

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-8 pb-8"
        >
            {/* Header */}
            <motion.div variants={item} className="mb-8">
                <Link to="/dashboard" className="inline-flex items-center text-sm font-semibold text-slate-500 hover:text-primary transition-colors mb-6 group">
                    <svg className="w-5 h-5 mr-1.5 transition-transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                    Back to Dashboard
                </Link>
                <div className="flex items-center gap-3 mb-3">
                    <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-primary/10 text-primary border border-primary/20">{topic.language}</span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest bg-slate-100 text-slate-500 border border-slate-200">{topic.difficulty}</span>
                </div>
                <h1 className="text-4xl md:text-5xl font-bold font-display text-slate-800 mb-4 tracking-tight">{topic.topicName}</h1>
                <p className="text-lg text-slate-500 leading-relaxed max-w-4xl">{topic.overview}</p>
            </motion.div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">

                {/* Left Col: Explanations */}
                <motion.div variants={item} className="lg:col-span-2 space-y-6">
                    <h2 className="text-2xl font-bold font-display text-slate-800">Choose Explanation Style</h2>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {topic.explanations.map(exp => (
                            <button
                                key={exp.style}
                                onClick={() => handleStyleChange(exp.style as ExplanationStyle)}
                                disabled={isChangingStyle}
                                className={`p-4 rounded-2xl flex flex-col items-center justify-center gap-3 text-center transition-all duration-300 relative overflow-hidden group border
                  ${selectedStyle === exp.style
                                        ? 'border-primary/50 bg-gradient-to-br from-primary/5 to-accent/5 shadow-md shadow-primary/10 ring-1 ring-primary/20'
                                        : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'}`}
                            >
                                {selectedStyle === exp.style && (
                                    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary to-accent" />
                                )}
                                <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl transition-transform duration-300 group-hover:scale-110
                  ${selectedStyle === exp.style ? 'bg-primary/20 shadow-inner' : 'bg-slate-100'}`}>
                                    {exp.icon}
                                </div>
                                <div>
                                    <h3 className={`font-bold font-display text-sm ${selectedStyle === exp.style ? 'text-primary' : 'text-slate-700'}`}>
                                        {exp.title}
                                    </h3>
                                    <span className={`text-[10px] font-bold uppercase tracking-wider mt-1 block ${selectedStyle === exp.style ? 'text-primary/70' : 'text-slate-400'}`}>
                                        Tap to view
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>

                    <div className="glass-card rounded-3xl p-8 md:p-10 min-h-[300px] relative mt-4">
                        {isChangingStyle && (
                            <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/50 backdrop-blur-sm rounded-3xl">
                                <div className="w-8 h-8 border-3 border-primary/20 border-t-primary rounded-full animate-spin" />
                            </div>
                        )}
                        <AnimatePresence mode="wait">
                            {explanation && !isChangingStyle && (
                                <motion.div
                                    key={selectedStyle}
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.98 }}
                                    transition={{ duration: 0.4 }}
                                    className="prose prose-slate max-w-none prose-p:leading-loose prose-p:text-slate-600 prose-strong:text-slate-800 prose-headings:font-display"
                                >
                                    <p className="text-lg">{explanation?.content}</p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>

                {/* Right Col: Videos */}
                <motion.div variants={item} className="lg:col-span-1 space-y-6">
                    <h2 className="text-2xl font-bold font-display text-slate-800 flex items-center gap-2">
                        <span className="text-2xl">📺</span> Videos
                    </h2>
                    <div className="space-y-5">
                        {topic.recommendedVideos.map(video => {
                            const isWatched = user?.videosWatched.some(v => v.id === video.id);
                            return (
                                <div key={video.id} className="glass-card rounded-3xl overflow-hidden group">
                                    <div className="relative pt-[56.25%] bg-slate-900 border-b border-white/10">
                                        <iframe
                                            src={`https://www.youtube.com/embed/${video.youtubeId}`}
                                            title={video.title}
                                            className="absolute top-0 left-0 w-full h-full"
                                            allowFullScreen
                                        />
                                    </div>
                                    <div className="p-5">
                                        <div className="flex justify-between items-start mb-3">
                                            <h4 className="font-bold font-display text-slate-800 leading-snug pr-4">{video.title}</h4>
                                        </div>
                                        <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
                                            <span>{video.language}</span>
                                            <span>{video.duration}</span>
                                        </div>
                                        {!isWatched ? (
                                            <button
                                                onClick={() => handleVideoWatch(video)}
                                                className="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider text-primary bg-primary/10 hover:bg-primary hover:text-white transition-colors duration-300 cursor-pointer"
                                            >
                                                Mark as Watched
                                            </button>
                                        ) : (
                                            <div className="w-full py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider text-success bg-success/10 text-center flex items-center justify-center gap-2 border border-success/20">
                                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>
                                                Watched
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="pt-8">
                        <button
                            onClick={() => navigate(`/quiz/${topic.id}`)}
                            className="w-full py-4 rounded-2xl bg-gradient-to-r from-primary to-accent text-white font-bold font-display text-lg flex flex-col items-center justify-center gap-1 shadow-[0_10px_25px_rgba(79,70,229,0.3)] hover:shadow-[0_15px_35px_rgba(79,70,229,0.4)] hover:-translate-y-1 transition-all duration-300 group cursor-pointer"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-2xl group-hover:scale-110 transition-transform">🎯</span>
                                Start Mock Test
                            </div>
                            <span className="text-xs font-medium text-white/80 uppercase tracking-widest">({topic.quiz.length} Questions)</span>
                        </button>
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
