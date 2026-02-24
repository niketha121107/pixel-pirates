import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, RefreshCw, Rocket, Zap, Heart, Trophy, Target, Flame, Star, BookOpen, Brain, Lightbulb } from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';

const ICONS = [
    <Rocket className="w-5 h-5" />,
    <Zap className="w-5 h-5" />,
    <Flame className="w-5 h-5" />,
    <Target className="w-5 h-5" />,
    <Trophy className="w-5 h-5" />,
    <Sparkles className="w-5 h-5" />,
    <Heart className="w-5 h-5" />,
    <Star className="w-5 h-5" />,
    <BookOpen className="w-5 h-5" />,
    <Brain className="w-5 h-5" />,
    <Lightbulb className="w-5 h-5" />,
];

const GRADIENTS = [
    'from-brand to-orange-400',
    'from-blue-500 to-cyan-400',
    'from-orange-500 to-red-400',
    'from-emerald-500 to-teal-400',
    'from-yellow-500 to-amber-400',
    'from-purple-500 to-violet-400',
    'from-pink-500 to-rose-400',
    'from-indigo-500 to-blue-400',
    'from-teal-500 to-emerald-400',
    'from-brand to-pink-400',
    'from-amber-500 to-yellow-400',
    'from-rose-500 to-pink-400',
    'from-cyan-500 to-blue-400',
    'from-violet-500 to-purple-400',
    'from-lime-500 to-green-400',
];

const MOTIVATIONAL_QUOTES = [
    // ── Learning & Growth ──
    { quote: "The expert in anything was once a beginner. Keep coding, keep growing!", author: "Helen Hayes" },
    { quote: "Every line of code you write is a step closer to mastery. You're building something amazing!", author: "EduTwin" },
    { quote: "Don't watch the clock; do what it does. Keep going!", author: "Sam Levenson" },
    { quote: "The only way to learn a new programming language is by writing programs in it.", author: "Dennis Ritchie" },
    { quote: "Success is the sum of small efforts, repeated day in and day out.", author: "Robert Collier" },
    { quote: "First, solve the problem. Then, write the code. You've got this!", author: "John Johnson" },
    { quote: "Learning never exhausts the mind. Your curiosity is your superpower!", author: "Leonardo da Vinci" },
    { quote: "It does not matter how slowly you go as long as you do not stop.", author: "Confucius" },
    { quote: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
    { quote: "You're closer than you think. One more topic, one more quiz, one more win!", author: "EduTwin" },
    // ── Persistence ──
    { quote: "Code is like humor. When you have to explain it, it's bad. Keep refining!", author: "Cory House" },
    { quote: "Your learning streak is proof of your dedication. Champions don't skip days!", author: "EduTwin" },
    { quote: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
    { quote: "The secret of getting ahead is getting started.", author: "Mark Twain" },
    { quote: "Education is the most powerful weapon which you can use to change the world.", author: "Nelson Mandela" },
    { quote: "The more that you read, the more things you will know. The more that you learn, the more places you'll go.", author: "Dr. Seuss" },
    { quote: "Live as if you were to die tomorrow. Learn as if you were to live forever.", author: "Mahatma Gandhi" },
    { quote: "An investment in knowledge pays the best interest.", author: "Benjamin Franklin" },
    { quote: "Start where you are. Use what you have. Do what you can.", author: "Arthur Ashe" },
    { quote: "The future belongs to those who prepare for it today.", author: "Malcolm X" },
    // ── Motivation & Drive ──
    { quote: "Dream big. Start small. Act now.", author: "Robin Sharma" },
    { quote: "You don't have to be great to start, but you have to start to be great.", author: "Zig Ziglar" },
    { quote: "Hard work beats talent when talent doesn't work hard.", author: "Tim Notke" },
    { quote: "The best time to plant a tree was 20 years ago. The second best time is now.", author: "Chinese Proverb" },
    { quote: "Push yourself, because no one else is going to do it for you.", author: "EduTwin" },
    { quote: "Wake up with determination. Go to bed with satisfaction.", author: "EduTwin" },
    { quote: "Small daily improvements over time lead to stunning results.", author: "Robin Sharma" },
    { quote: "Mistakes are proof that you are trying. Keep at it!", author: "EduTwin" },
    { quote: "Every expert was once a student. Your time to shine is coming!", author: "EduTwin" },
    { quote: "Discipline is the bridge between goals and accomplishment.", author: "Jim Rohn" },
    // ── Tech & Coding ──
    { quote: "Simplicity is the soul of efficiency.", author: "Austin Freeman" },
    { quote: "Talk is cheap. Show me the code.", author: "Linus Torvalds" },
    { quote: "Programs must be written for people to read, and only incidentally for machines to execute.", author: "Harold Abelson" },
    { quote: "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", author: "Martin Fowler" },
    { quote: "The best error message is the one that never shows up.", author: "Thomas Fuchs" },
    { quote: "Debugging is twice as hard as writing code. So if you write the cleverest code, you're not smart enough to debug it.", author: "Brian Kernighan" },
    { quote: "Knowledge is power. Sharing knowledge is the ultimate superpower.", author: "EduTwin" },
    { quote: "One quiz at a time, one topic at a time — that's how legends are made.", author: "EduTwin" },
    { quote: "You are one lesson away from a breakthrough!", author: "EduTwin" },
    { quote: "Great things never come from comfort zones. Challenge yourself today!", author: "EduTwin" },
    // ── Mindset & Focus ──
    { quote: "Your limitation — it's only your imagination.", author: "EduTwin" },
    { quote: "Don't stop when you're tired. Stop when you're done.", author: "EduTwin" },
    { quote: "Focus on progress, not perfection.", author: "EduTwin" },
    { quote: "It always seems impossible until it's done.", author: "Nelson Mandela" },
    { quote: "The only person you are destined to become is the person you decide to be.", author: "Ralph Waldo Emerson" },
    { quote: "Strive for progress, not perfection. Every step counts!", author: "EduTwin" },
    { quote: "What we learn with pleasure we never forget.", author: "Alfred Mercier" },
    { quote: "A journey of a thousand miles begins with a single step.", author: "Lao Tzu" },
    { quote: "The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice.", author: "Brian Herbert" },
    { quote: "Your brain is a muscle. The more you use it, the stronger it gets!", author: "EduTwin" },
    // ── Encouragement ──
    { quote: "Be so good they can't ignore you.", author: "Steve Martin" },
    { quote: "Genius is 1% inspiration and 99% perspiration.", author: "Thomas Edison" },
    { quote: "The only limit to our realization of tomorrow will be our doubts of today.", author: "Franklin D. Roosevelt" },
    { quote: "You are braver than you believe, stronger than you seem, and smarter than you think.", author: "A.A. Milne" },
    { quote: "When you feel like quitting, think about why you started.", author: "EduTwin" },
].map((q, i) => ({
    ...q,
    icon: ICONS[i % ICONS.length],
    gradient: GRADIENTS[i % GRADIENTS.length],
}));

const DAILY_CHALLENGES = [
    "🎯 Complete one pending topic today!",
    "⚡ Take a quiz and beat your high score!",
    "📝 Write notes for 3 topics you studied!",
    "🔥 Maintain your learning streak!",
    "🌟 Teach someone what you learned today!",
    "💡 Review your highlighted notes!",
    "🚀 Start that topic you've been avoiding!",
    "🏆 Aim for a perfect quiz score!",
    "📖 Read one new article in your field!",
    "🧠 Revise a topic you learned last week!",
    "🤝 Help a peer with a tricky concept!",
    "✍️ Summarise today's learning in 3 bullets!",
];

export const MotivationalQuotes = () => {
    const [currentIndex, setCurrentIndex] = useState(() => Math.floor(Math.random() * MOTIVATIONAL_QUOTES.length));
    const [isAnimating, setIsAnimating] = useState(false);
    const [dailyChallenge] = useState(() => {
        const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
        return DAILY_CHALLENGES[dayOfYear % DAILY_CHALLENGES.length];
    });

    const nextQuote = () => {
        if (isAnimating) return;
        setIsAnimating(true);
        setCurrentIndex((prev) => (prev + 1) % MOTIVATIONAL_QUOTES.length);
        setTimeout(() => setIsAnimating(false), 500);
    };

    // Auto-rotate every 10 seconds
    useEffect(() => {
        const interval = setInterval(nextQuote, 10000);
        return () => clearInterval(interval);
    }, []);

    const current = MOTIVATIONAL_QUOTES[currentIndex];

    // Paginated dots — show a window of 8 dots centred around current
    const DOT_COUNT = 8;
    const half = Math.floor(DOT_COUNT / 2);
    const total = MOTIVATIONAL_QUOTES.length;
    let dotStart = currentIndex - half;
    if (dotStart < 0) dotStart = 0;
    if (dotStart + DOT_COUNT > total) dotStart = Math.max(0, total - DOT_COUNT);
    const dotIndices = Array.from({ length: Math.min(DOT_COUNT, total) }, (_, i) => dotStart + i);

    return (
        <GlassCard className="p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-400 flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-800">Daily Motivation</h3>
                        <p className="text-xs text-gray-500">{total} inspiring quotes · Stay learning</p>
                    </div>
                </div>
                <motion.button
                    whileHover={{ scale: 1.1, rotate: 180 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={nextQuote}
                    className="p-2 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-500 transition-colors"
                    title="Next quote"
                >
                    <RefreshCw className="w-4 h-4" />
                </motion.button>
            </div>

            {/* Quote Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentIndex}
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -30 }}
                    transition={{ duration: 0.4 }}
                    className={`relative p-5 rounded-2xl bg-gradient-to-br ${current.gradient} text-white overflow-hidden`}
                >
                    {/* Decorative elements */}
                    <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full blur-2xl" />
                    <div className="absolute bottom-0 left-0 w-16 h-16 bg-white/5 rounded-full blur-xl" />

                    <div className="relative z-10">
                        <div className="flex items-center gap-2 mb-3 opacity-80">
                            {current.icon}
                            <span className="text-xs font-medium uppercase tracking-wider">Motivation Boost</span>
                        </div>
                        <blockquote className="text-base sm:text-lg font-semibold leading-relaxed mb-3">
                            "{current.quote}"
                        </blockquote>
                        <p className="text-sm opacity-80 font-medium">— {current.author}</p>
                    </div>
                </motion.div>
            </AnimatePresence>

            {/* Quote dots indicator */}
            <div className="flex items-center justify-center gap-1.5 mt-4">
                {dotStart > 0 && <span className="text-gray-400 text-[10px]">···</span>}
                {dotIndices.map((i) => (
                    <button
                        key={i}
                        onClick={() => setCurrentIndex(i)}
                        className={`w-2 h-2 rounded-full transition-all ${
                            i === currentIndex ? 'bg-brand w-4' : 'bg-gray-300 hover:bg-gray-400'
                        }`}
                    />
                ))}
                {dotStart + DOT_COUNT < total && <span className="text-gray-400 text-[10px]">···</span>}
                <span className="ml-2 text-[10px] text-gray-400 font-medium">{currentIndex + 1}/{total}</span>
            </div>

            {/* Daily Challenge */}
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-4 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl"
            >
                <p className="text-xs font-semibold text-orange-800 uppercase tracking-wider mb-1">Today's Challenge</p>
                <p className="text-sm text-gray-700 font-medium">{dailyChallenge}</p>
            </motion.div>

            {/* Streak Motivator */}
            <motion.div
                whileHover={{ scale: 1.01 }}
                className="mt-3 p-3 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl flex items-center gap-3"
            >
                <div className="w-8 h-8 rounded-full bg-emerald-400 flex items-center justify-center flex-shrink-0">
                    <Flame className="w-4 h-4 text-white" />
                </div>
                <div>
                    <p className="text-xs font-bold text-emerald-800">Keep Your Streak Alive!</p>
                    <p className="text-[11px] text-emerald-600">Complete at least one activity today to maintain your 12-day streak.</p>
                </div>
            </motion.div>
        </GlassCard>
    );
};
