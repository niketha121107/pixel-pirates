import { useState, useEffect, useCallback, useRef } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { CheckCircle2, XCircle, ArrowRight, Home, Trophy, RotateCcw, Sparkles, Rocket } from 'lucide-react';
import { cn } from '../lib/utils';

interface Question {
    text: string;
    options: string[];
    correctIdx: number;
    explanation: string;
}

const questions: Question[] = [
    {
        text: "Which keyword is used in Python to create a generator function?",
        options: ["return", "yield", "generator", "async"],
        correctIdx: 1,
        explanation: "The 'yield' keyword is used to create generator functions. When Python encounters 'yield', it turns the function into a generator that can produce a series of values lazily."
    },
    {
        text: "What is the time complexity of searching in a balanced binary search tree?",
        options: ["O(n)", "O(log n)", "O(n²)", "O(1)"],
        correctIdx: 1,
        explanation: "A balanced BST halves the search space at each step, giving O(log n) time complexity, similar to binary search on a sorted array."
    },
    {
        text: "Which data structure uses LIFO (Last In First Out) ordering?",
        options: ["Queue", "Array", "Stack", "Linked List"],
        correctIdx: 2,
        explanation: "A Stack follows LIFO ordering — the last element pushed onto the stack is the first one to be popped off. Think of a stack of plates."
    },
    {
        text: "What does the 'this' keyword refer to in a JavaScript arrow function?",
        options: ["The function itself", "The global object", "The enclosing lexical context", "undefined"],
        correctIdx: 2,
        explanation: "Arrow functions don't have their own 'this' — they inherit 'this' from the enclosing lexical scope (the surrounding code where the arrow function was defined)."
    },
    {
        text: "In SQL, which clause is used to filter grouped results?",
        options: ["WHERE", "HAVING", "FILTER", "GROUP BY"],
        correctIdx: 1,
        explanation: "HAVING is used to filter results after GROUP BY aggregation. WHERE filters individual rows before grouping, while HAVING filters the grouped results."
    }
];

// ── Encouraging messages for wrong answers ──
const WRONG_MESSAGES = [
    "Best try! Let's crush the next question with the correct answer! 💪",
    "Almost there! You'll nail it next time — keep pushing! 🔥",
    "Don't worry! Every mistake is a step closer to mastery! 🚀",
    "Great effort! The next one is yours — let's go! ⚡",
    "Nice attempt! Learning from mistakes makes you stronger! 🌟",
];

// ── Glitter particle component ──
interface GlitterParticle {
    id: number;
    x: number;
    y: number;
    size: number;
    color: string;
    delay: number;
    duration: number;
    rotate: number;
}

const GLITTER_COLORS = [
    '#fbbf24', '#f59e0b', '#eab308', '#facc15',
    '#ec4899', '#f472b6', '#fb923c', '#a78bfa',
    '#34d399', '#22d3ee', '#60a5fa', '#c084fc',
];

function generateGlitter(count: number): GlitterParticle[] {
    return Array.from({ length: count }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 10 + 4,
        color: GLITTER_COLORS[Math.floor(Math.random() * GLITTER_COLORS.length)],
        delay: Math.random() * 0.6,
        duration: Math.random() * 1.2 + 0.8,
        rotate: Math.random() * 360,
    }));
}

const GlitterOverlay = ({ onDone }: { onDone: () => void }) => {
    const particles = useRef(generateGlitter(60)).current;

    useEffect(() => {
        const t = setTimeout(onDone, 2200);
        return () => clearTimeout(t);
    }, [onDone]);

    return (
        <motion.div
            className="fixed inset-0 pointer-events-none z-[200]"
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, delay: 1.7 }}
        >
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-sm"
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: p.size,
                        height: p.size,
                        backgroundColor: p.color,
                        rotate: p.rotate,
                    }}
                    initial={{ opacity: 0, scale: 0, y: 0 }}
                    animate={{
                        opacity: [0, 1, 1, 0],
                        scale: [0, 1.2, 1, 0.5],
                        y: [0, -60 - Math.random() * 120],
                        rotate: p.rotate + 180 + Math.random() * 180,
                    }}
                    transition={{
                        duration: p.duration,
                        delay: p.delay,
                        ease: 'easeOut',
                    }}
                />
            ))}
            {/* Central sparkle burst */}
            <motion.div
                className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: [0, 1.5, 1], opacity: [0, 1, 0] }}
                transition={{ duration: 1 }}
            >
                <Sparkles className="w-20 h-20 text-yellow-400 drop-shadow-lg" />
            </motion.div>
        </motion.div>
    );
};

// ── Encouraging popup for wrong answers ──
const WrongAnswerPopup = ({ message, onDone }: { message: string; onDone: () => void }) => {
    useEffect(() => {
        const t = setTimeout(onDone, 2500);
        return () => clearTimeout(t);
    }, [onDone]);

    return (
        <motion.div
            className="fixed inset-0 z-[200] flex items-center justify-center px-6 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
        >
            {/* backdrop blur */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
            <motion.div
                className="relative bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full text-center border-2 border-orange-200"
                initial={{ scale: 0.6, y: 40 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.8, y: -20, opacity: 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            >
                <motion.div
                    initial={{ rotate: -10 }}
                    animate={{ rotate: [0, -10, 10, -5, 5, 0] }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="w-16 h-16 bg-gradient-to-br from-orange-400 to-pink-400 rounded-full flex items-center justify-center mx-auto mb-4"
                >
                    <Rocket className="w-8 h-8 text-white" />
                </motion.div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Keep Going!</h3>
                <p className="text-gray-600 font-medium leading-relaxed">{message}</p>
                <motion.div
                    className="mt-4 h-1 bg-gradient-to-r from-orange-300 via-pink-300 to-purple-300 rounded-full"
                    initial={{ scaleX: 1 }}
                    animate={{ scaleX: 0 }}
                    transition={{ duration: 2.5, ease: 'linear' }}
                    style={{ transformOrigin: 'left' }}
                />
            </motion.div>
        </motion.div>
    );
};

export const QuizPage = () => {
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState<(number | null)[]>(Array(questions.length).fill(null));
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [showResult, setShowResult] = useState(false);

    // Feedback state
    const [feedbackState, setFeedbackState] = useState<'idle' | 'correct' | 'wrong'>('idle');
    const [wrongMessage, setWrongMessage] = useState('');

    const totalQuestions = questions.length;
    const currentQuestion = questions[currentQ];
    const progressPercentage = ((currentQ + 1) / totalQuestions) * 100;

    const handleSelect = (idx: number) => {
        if (feedbackState !== 'idle') return; // lock while showing feedback
        setSelectedAnswer(idx);
    };

    const advanceToNext = useCallback(() => {
        if (currentQ < totalQuestions - 1) {
            setCurrentQ((q) => q + 1);
            setSelectedAnswer(null);
        } else {
            setShowResult(true);
        }
        setFeedbackState('idle');
    }, [currentQ, totalQuestions]);

    const handleNext = () => {
        if (selectedAnswer === null) return;

        const newAnswers = [...answers];
        newAnswers[currentQ] = selectedAnswer;
        setAnswers(newAnswers);

        const isCorrect = selectedAnswer === currentQuestion.correctIdx;

        if (isCorrect) {
            setFeedbackState('correct');
            // glitter overlay auto-advances via onDone
        } else {
            setWrongMessage(WRONG_MESSAGES[Math.floor(Math.random() * WRONG_MESSAGES.length)]);
            setFeedbackState('wrong');
            // popup auto-advances via onDone
        }
    };

    const score = answers.filter((a, i) => a === questions[i].correctIdx).length;
    const percentage = Math.round((score / totalQuestions) * 100);

    const handleRetry = () => {
        setCurrentQ(0);
        setAnswers(Array(questions.length).fill(null));
        setSelectedAnswer(null);
        setShowResult(false);
        setFeedbackState('idle');
    };

    // Results Screen
    if (showResult) {
        return (
            <PageWrapper className="justify-center items-center py-12" withPadding={false}>
                <div className="w-full max-w-3xl px-4 space-y-8">

                    {/* Score Header */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center"
                    >
                        <GlassCard className="p-8">
                            <div className="flex flex-col items-center gap-4">
                                <div className={`w-20 h-20 rounded-full flex items-center justify-center ${
                                    percentage >= 80 ? 'bg-green-100 text-green-600' :
                                    percentage >= 50 ? 'bg-yellow-100 text-yellow-600' :
                                    'bg-red-100 text-red-600'
                                }`}>
                                    <Trophy className="w-10 h-10" />
                                </div>
                                <h1 className="text-3xl font-bold text-gray-800">Mock Test Complete!</h1>
                                <div className="text-5xl font-bold text-brand">{score}/{totalQuestions}</div>
                                <p className="text-gray-500 text-lg">
                                    You scored {percentage}% — {
                                        percentage >= 80 ? 'Excellent work!' :
                                        percentage >= 50 ? 'Good effort, keep practicing!' :
                                        'Keep studying, you\'ll improve!'
                                    }
                                </p>

                                <div className="flex gap-3 mt-4">
                                    <button
                                        onClick={handleRetry}
                                        className="flex items-center gap-2 px-5 py-3 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                                    >
                                        <RotateCcw className="w-4 h-4" /> Retry
                                    </button>
                                    <Link to="/dashboard">
                                        <GradientButton>
                                            <Home className="w-4 h-4" /> Dashboard
                                        </GradientButton>
                                    </Link>
                                </div>
                            </div>
                        </GlassCard>
                    </motion.div>

                    {/* Answer Review */}
                    <div className="space-y-4">
                        <h2 className="text-xl font-bold text-gray-800">Review Answers</h2>
                        {questions.map((q, i) => {
                            const userAnswer = answers[i];
                            const isCorrect = userAnswer === q.correctIdx;
                            return (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                >
                                    <GlassCard className={`p-6 ${isCorrect ? 'border-green-200' : 'border-red-200'}`}>
                                        <div className="flex items-start gap-3 mb-3">
                                            {isCorrect ? (
                                                <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                                            ) : (
                                                <XCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                                            )}
                                            <div className="flex-1">
                                                <p className="font-semibold text-gray-800 mb-2">Q{i + 1}: {q.text}</p>

                                                <div className="space-y-1.5 mb-3">
                                                    {q.options.map((opt, j) => (
                                                        <div
                                                            key={j}
                                                            className={cn(
                                                                "px-3 py-2 rounded-lg text-sm",
                                                                j === q.correctIdx && "bg-green-50 text-green-700 font-medium border border-green-200",
                                                                j === userAnswer && j !== q.correctIdx && "bg-red-50 text-red-700 font-medium border border-red-200",
                                                                j !== q.correctIdx && j !== userAnswer && "text-gray-500"
                                                            )}
                                                        >
                                                            {opt}
                                                            {j === q.correctIdx && " ✓"}
                                                            {j === userAnswer && j !== q.correctIdx && " ✗ (your answer)"}
                                                        </div>
                                                    ))}
                                                </div>

                                                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-sm text-orange-800">
                                                    <strong>Explanation:</strong> {q.explanation}
                                                </div>
                                            </div>
                                        </div>
                                    </GlassCard>
                                </motion.div>
                            );
                        })}
                    </div>
                </div>
            </PageWrapper>
        );
    }

    // Quiz Screen
    return (
        <PageWrapper className="justify-center items-center py-12" withPadding={false}>
            {/* ── Glitter overlay on correct answer ── */}
            <AnimatePresence>
                {feedbackState === 'correct' && (
                    <GlitterOverlay onDone={advanceToNext} />
                )}
            </AnimatePresence>

            {/* ── Encouraging popup on wrong answer ── */}
            <AnimatePresence>
                {feedbackState === 'wrong' && (
                    <WrongAnswerPopup message={wrongMessage} onDone={advanceToNext} />
                )}
            </AnimatePresence>

            <div className="w-full max-w-3xl px-4 space-y-8">

                {/* Top Progress Bar */}
                <div className="flex items-center gap-4 w-full mb-8">
                    <Link to="/topic" className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 text-gray-500 hover:text-gray-800 transition">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path></svg>
                    </Link>
                    <div className="flex-1">
                        <div className="flex justify-between text-sm font-bold text-gray-500 mb-2">
                            <span>Question {currentQ + 1} of {totalQuestions}</span>
                            <span>{Math.round(progressPercentage)}%</span>
                        </div>
                        <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${progressPercentage}%` }}
                                className="h-full bg-gradient-brand rounded-full"
                            />
                        </div>
                    </div>
                </div>

                {/* Main Quiz Area */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentQ}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                    >
                        <GlassCard className="p-8 md:p-12 mb-6 text-center border-brand/10">
                            <h2 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight">
                                {currentQuestion.text}
                            </h2>
                        </GlassCard>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {currentQuestion.options.map((opt, idx) => {
                                const isSelected = selectedAnswer === idx;
                                const showCorrect = feedbackState !== 'idle' && idx === currentQuestion.correctIdx;
                                const showWrong = feedbackState === 'wrong' && idx === selectedAnswer && idx !== currentQuestion.correctIdx;

                                return (
                                    <motion.button
                                        key={idx}
                                        whileHover={feedbackState === 'idle' ? { scale: 1.02 } : {}}
                                        whileTap={feedbackState === 'idle' ? { scale: 0.98 } : {}}
                                        onClick={() => handleSelect(idx)}
                                        className={cn(
                                            "p-5 rounded-2xl border-2 text-left font-semibold text-lg transition-all",
                                            showCorrect
                                                ? "border-green-400 bg-green-50 text-green-700 shadow-md ring-2 ring-green-200"
                                                : showWrong
                                                ? "border-red-400 bg-red-50 text-red-700 shadow-md ring-2 ring-red-200"
                                                : isSelected
                                                ? "border-brand bg-brand/5 text-gray-800 shadow-md"
                                                : "border-gray-200 bg-white text-gray-600 hover:border-brand/30 hover:bg-gray-50"
                                        )}
                                        disabled={feedbackState !== 'idle'}
                                    >
                                        <span className="flex items-center gap-2">
                                            {showCorrect && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                                            {showWrong && <XCircle className="w-5 h-5 text-red-500" />}
                                            {opt}
                                        </span>
                                    </motion.button>
                                );
                            })}
                        </div>

                        <motion.div
                            className="mt-10 flex justify-end"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <GradientButton
                                onClick={handleNext}
                                disabled={selectedAnswer === null || feedbackState !== 'idle'}
                                className={cn(
                                    "px-10 py-4 text-lg group",
                                    (selectedAnswer === null || feedbackState !== 'idle') && "opacity-50 cursor-not-allowed"
                                )}
                            >
                                {currentQ < totalQuestions - 1 ? 'Next Question' : 'Finish Test'}
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </GradientButton>
                        </motion.div>
                    </motion.div>
                </AnimatePresence>

            </div>
        </PageWrapper>
    );
};
