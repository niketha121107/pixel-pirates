import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { topicsAPI, quizAPI, progressAPI, aiAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import { CheckCircle2, XCircle, ArrowRight, Home, Trophy, RotateCcw, Sparkles, Rocket, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface Question {
    text: string;
    options: string[];
    correctIdx: number;
    explanation: string;
}

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
    const [searchParams] = useSearchParams();
    const topicId = searchParams.get('topicId') || '';
    const subtopicId = searchParams.get('subtopicId') || '';

    const [questions, setQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState<(number | null)[]>([]);
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [showResult, setShowResult] = useState(false);

    // Feedback state
    const [feedbackState, setFeedbackState] = useState<'idle' | 'correct' | 'wrong'>('idle');
    const [wrongMessage, setWrongMessage] = useState('');

    // Fetch questions from API
    useEffect(() => {
        setLoading(true);
        console.log(`QuizPage: Fetching quiz for topicId=${topicId}`);
        
        // Always try AI endpoint first if topicId is provided
        const fetchQuiz = topicId
            ? aiAPI.quiz(topicId, 5, 'mixed')
                .then(res => {
                    console.log('AI quiz generated successfully');
                    return res;
                })
                .catch((aiErr) => {
                    // Fallback: try regular quiz API from topics
                    console.warn('AI quiz failed, trying regular API:', aiErr?.message || aiErr);
                    return topicsAPI.getQuiz(topicId)
                        .catch((topicsErr) => {
                            console.error('Both AI and regular quiz failed:', topicsErr?.message || topicsErr);
                            throw topicsErr;
                        });
                })
            : aiAPI.generateAdaptive('topic-1', 5)
                .catch(() => {
                    // Fallback: try adaptive quiz
                    console.warn('AI adaptive failed, trying regular API');
                    return quizAPI.adaptive('topic-1', 5);
                });

        fetchQuiz
            .then(res => {
                const data = res.data?.data;
                const rawQuestions = data?.quiz || data?.questions || [];
                const mapped: Question[] = rawQuestions.map((q: any) => ({
                    text: q.question || q.text || '',
                    options: q.options || [],
                    correctIdx: typeof q.correctAnswer === 'number' ? q.correctAnswer : (q.correctIdx ?? 0),
                    explanation: q.explanation || 'Review this concept for a deeper understanding.',
                }));
                setQuestions(mapped);
                setAnswers(Array(mapped.length).fill(null));
            })
            .catch((err) => {
                console.error('Failed to fetch quiz:', err);
                setQuestions([]);
            })
            .finally(() => setLoading(false));
    }, [topicId]);

    const totalQuestions = questions.length;
    const currentQuestion = questions[currentQ] || { text: '', options: [], correctIdx: 0, explanation: '' };
    const progressPercentage = totalQuestions > 0 ? ((currentQ + 1) / totalQuestions) * 100 : 0;

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
            // Submit quiz result to backend
            if (topicId) {
                const finalAnswers = [...answers];
                finalAnswers[currentQ] = selectedAnswer ?? -1;
                const finalScore = finalAnswers.filter((a, i) => a === questions[i]?.correctIdx).length;
                const pct = totalQuestions > 0 ? Math.round((finalScore / totalQuestions) * 100) : 0;
                
                progressAPI.saveTopic({
                    topic_id: topicId,
                    quiz_score: finalScore,
                    quiz_total: totalQuestions,
                    attempts: 1,
                    status: pct >= 70 ? 'completed' : 'in-progress',
                }).then(() => {
                    // Trigger progress page refresh after successful completion
                    if (pct >= 70) {
                        localStorage.setItem('quiz-completed-trigger', Date.now().toString());
                    }
                }).catch(() => {});
                
                quizAPI.submit({
                    topic_id: topicId,
                    answers: questions.map((q, i) => ({
                        question_id: q.text?.slice(0, 20) || `q-${i}`,
                        selected_answer: finalAnswers[i] ?? -1,
                    })),
                    time_taken: 0,
                }).then(() => {
                    // Also trigger refresh on successful backend submission
                    if (pct >= 70) {
                        localStorage.setItem('quiz-completed-trigger', Date.now().toString());
                    }
                }).catch(() => {});
            }
        }
        setFeedbackState('idle');
    }, [currentQ, totalQuestions, topicId, answers, selectedAnswer, questions]);

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

    const score = totalQuestions > 0 ? answers.filter((a, i) => a === questions[i]?.correctIdx).length : 0;
    const percentage = totalQuestions > 0 ? Math.round((score / totalQuestions) * 100) : 0;

    // const handleRetry = () => {
    //     setCurrentQ(0);
    //     setAnswers(Array(totalQuestions).fill(null));
    //     setSelectedAnswer(null);
    //     setShowResult(false);
    //     setFeedbackState('idle');
    // };

    // Loading state
    if (loading) {
        return (
            <PageWrapper className="justify-center items-center py-12" withPadding={false}>
                <div className="flex flex-col items-center gap-4">
                    <Loader2 className="w-10 h-10 text-brand animate-spin" />
                    <p className="text-gray-500 font-medium">Loading quiz questions...</p>
                </div>
            </PageWrapper>
        );
    }

    // No questions available
    if (questions.length === 0) {
        return (
            <PageWrapper className="justify-center items-center py-12" withPadding={false}>
                <div className="flex flex-col items-center gap-4 text-center">
                    <Trophy className="w-12 h-12 text-gray-300" />
                    <h2 className="text-xl font-bold text-gray-800">No quiz available</h2>
                    <p className="text-gray-500">No questions found for this topic. Try another one!</p>
                    <Link to="/videos"><GradientButton>Back to Topics</GradientButton></Link>
                </div>
            </PageWrapper>
        );
    }

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

                                {/* Detailed marks breakdown */}
                                <div className="mt-4 grid grid-cols-3 gap-3 max-w-sm mx-auto">
                                    <div className="bg-green-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-green-600">{score}</p>
                                        <p className="text-[10px] text-green-600 font-medium">Correct</p>
                                    </div>
                                    <div className="bg-red-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-red-500">{totalQuestions - score}</p>
                                        <p className="text-[10px] text-red-500 font-medium">Wrong</p>
                                    </div>
                                    <div className="bg-blue-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-blue-600">{percentage}%</p>
                                        <p className="text-[10px] text-blue-600 font-medium">Percentage</p>
                                    </div>
                                </div>

                                <div className="flex gap-3 mt-6 flex-wrap justify-center">
                                    {topicId && (
                                        <Link to={`/topic?id=${topicId}`}>
                                            <button className="flex items-center gap-2 px-5 py-3 bg-emerald-50 text-emerald-600 rounded-xl font-semibold hover:bg-emerald-100 transition-colors">
                                                <ArrowRight className="w-4 h-4 rotate-180" /> Back to Topic
                                            </button>
                                        </Link>
                                    )}
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
