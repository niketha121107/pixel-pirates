import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X, ClipboardList, Loader2, Clock, CheckCircle2, XCircle,
    Trophy, ArrowRight, ArrowLeft, Eye
} from 'lucide-react';
import { GlassCard } from './ui/GlassCard';
import { GradientButton } from './ui/GradientButton';
import { topicsAPI, progressAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface MockQuestion {
    id: number;
    type: 'mcq';
    question: string;
    options: string[];
    correctAnswer: string;
    correctIdx?: number;
    explanation: string;
    points: number;
}

interface MockTestModalProps {
    isOpen: boolean;
    onClose: () => void;
    topicId: string;
    topicTitle: string;
    onTestCompleted?: () => void;
}

type TestMode = 'setup' | 'active' | 'results';

export const MockTestModal = ({
    isOpen,
    onClose,
    topicId,
    topicTitle,
    onTestCompleted
}: MockTestModalProps) => {
    const { user } = useAuth();
    const [mode, setMode] = useState<TestMode>('setup');
    const [testDuration, setTestDuration] = useState(30);
    const [loading, setLoading] = useState(false);
    const [questions, setQuestions] = useState<MockQuestion[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [timeLeft, setTimeLeft] = useState(0);
    const [totalTime, setTotalTime] = useState(0);
    const [score, setScore] = useState(0);
    const [error, setError] = useState('');
    const [showDetails, setShowDetails] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    // Timer effect
    useEffect(() => {
        if (mode !== 'active' || timeLeft < 0) return;
        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    // Time expired - auto-submit the test
                    setTimeout(() => finishTest(), 100);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [mode, timeLeft]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const fetchQuestions = async () => {
        setLoading(true);
        setError('');
        
        try {
            const quizRes = await topicsAPI.getQuiz(topicId, undefined);
            const topicQuiz = quizRes.data?.data?.quiz || quizRes.data?.data?.questions || [];
            
            if (!topicQuiz || topicQuiz.length === 0) {
                setError('No questions available for this topic');
                setLoading(false);
                return;
            }

            // Map and filter only MCQ questions, limit to 5
            const mcqs = topicQuiz
                .filter((q: any) => {
                    const type = String(q.type || '').toLowerCase();
                    return type === 'mcq' || (q.options && q.options.length > 0);
                })
                .slice(0, 5)
                .map((q: any, idx: number) => ({
                    id: idx + 1,
                    type: 'mcq' as const,
                    question: q.question || q.text || '',
                    options: Array.isArray(q.options) ? q.options : [],
                    correctAnswer: typeof q.correctAnswer === 'number'
                        ? (q.options?.[q.correctAnswer] || '')
                        : (q.correctAnswer || q.options?.[q.correctIdx] || ''),
                    correctIdx: typeof q.correctAnswer === 'number' ? q.correctAnswer : q.correctIdx,
                    explanation: q.explanation || '',
                    points: q.points || 10,
                })) as MockQuestion[];

            if (mcqs.length === 0) {
                setError('No multiple choice questions found for this topic');
                setLoading(false);
                return;
            }

            setQuestions(mcqs);
            setTotalTime(testDuration);
            setTimeLeft(testDuration);
            setMode('active');
        } catch (err: any) {
            setError(err.message || 'Failed to load questions');
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = (option: string) => {
        setAnswers(prev => ({
            ...prev,
            [currentIdx + 1]: option
        }));
    };

    const handleNext = () => {
        if (currentIdx < questions.length - 1) {
            setCurrentIdx(prev => prev + 1);
        }
    };

    const handlePrev = () => {
        if (currentIdx > 0) {
            setCurrentIdx(prev => prev - 1);
        }
    };

    const finishTest = async () => {
        // Calculate score
        let totalScore = 0;
        questions.forEach((q, idx) => {
            const userAnswer = answers[idx + 1];
            if (userAnswer === q.correctAnswer) {
                totalScore += q.points;
            }
        });
        
        setScore(totalScore);
        
        // Record progress to backend
        const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);
        const percentage = totalPoints > 0 ? Math.round((totalScore / totalPoints) * 100) : 0;
        
        // Save result to localStorage for TopicView to display
        if (user?.id) {
            try {
                const resultsKey = `edutwin-mock-results_${user.id}`;
                const existingString = localStorage.getItem(resultsKey);
                let results = [];
                
                if (existingString) {
                    try {
                        results = JSON.parse(existingString);
                    } catch (e) {
                        results = [];
                    }
                }
                
                // Find and update existing result for this topic, or add new one
                const resultIndex = results.findIndex((r: any) => r.topicId === topicId || r.topic === topicId);
                const testResult = {
                    topicId,
                    topic: topicTitle,
                    score: totalScore,
                    total: totalPoints,
                    percentage: percentage,
                    answers: answers,
                    completedAt: new Date().toISOString()
                };
                
                if (resultIndex >= 0) {
                    results[resultIndex] = testResult;
                } else {
                    results.push(testResult);
                }
                
                localStorage.setItem(resultsKey, JSON.stringify(results));
            } catch (err) {
                console.error('Failed to save result to localStorage:', err);
            }
        }
        
        try {
            setSubmitting(true);
            const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);
            const timeTaken = totalTime - timeLeft;
            
            console.log('📝 Saving test result:', {
                topicId,
                totalScore,
                percentage,
                totalPoints,
                timeTaken,
                status: 'completed'  // Always mark as completed
            });
            
            // Record topic progress to backend
            const topicRes = await progressAPI.saveTopic({
                topic_id: topicId,
                quiz_score: totalScore,
                quiz_total: totalPoints,
                attempts: 1,
                status: 'completed'  // Always mark as completed
            });
            console.log('✅ saveTopic succeeded:', topicRes.data);
            
            // Also save mock result to backend for stats aggregation
            const mockRes = await progressAPI.saveMockResult({
                topics: [topicId],
                score: totalScore,
                total_questions: questions.length,  // Use length instead of totalPoints
                percentage: percentage,
                time_taken: timeTaken,
                answers: Object.values(answers)
            });
            console.log('✅ saveMockResult succeeded:', mockRes.data);
        } catch (err: any) {
            console.error('❌ Failed to save progress:', err);
            if (err.response?.data) {
                console.error('Backend error:', err.response.data);
            }
        } finally {
            setSubmitting(false);
        }
        
        // Notify parent that test is completed
        if (onTestCompleted) {
            onTestCompleted();
        }
        
        setMode('results');
        setShowDetails(false);
    };

    const handleStart = () => {
        if (!testDuration) return;
        fetchQuestions();
    };

    const handleClose = () => {
        // Only allow closing after results
        if (mode === 'results' || mode === 'setup') {
            setMode('setup');
            setCurrentIdx(0);
            setAnswers({});
            setScore(0);
            setError('');
            onClose();
        }
    };

    const currentQuestion = questions[currentIdx];
    const progress = ((currentIdx + 1) / questions.length) * 100;
    const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);
    const percentage = totalPoints > 0 ? Math.round((score / totalPoints) * 100) : 0;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    {/* Backdrop - not clickable when test is running */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={mode === 'setup' || mode === 'results' ? handleClose : undefined}
                        className={`absolute inset-0 bg-black/50 backdrop-blur-sm ${mode === 'active' ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-white rounded-3xl shadow-2xl"
                    >
                        {/* SETUP MODE */}
                        {mode === 'setup' && (
                            <>
                                {/* Header */}
                                <div className="sticky top-0 bg-gradient-to-r from-brand via-pink-400 to-rose-400 px-6 py-6 sm:px-8 flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-white mb-1">Topic Test Setup</h2>
                                        <p className="text-white/80 text-sm">{topicTitle}</p>
                                    </div>
                                    <button
                                        onClick={handleClose}
                                        className="flex-shrink-0 p-2 hover:bg-white/20 rounded-full transition-colors"
                                    >
                                        <X className="w-6 h-6 text-white" />
                                    </button>
                                </div>

                                {/* Content */}
                                <div className="p-6 sm:p-8 space-y-6">
                                    {error && (
                                        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                                            <p className="text-sm text-red-700">{error}</p>
                                        </div>
                                    )}

                                    {/* Test Info */}
                                    <GlassCard className="p-6 bg-blue-50 border border-blue-200">
                                        <p className="text-sm text-blue-800 mb-4">
                                            <span className="font-semibold">📋 Test Overview:</span>
                                        </p>
                                        <ul className="text-sm text-blue-700 space-y-2 ml-4">
                                            <li>✓ <strong>5 MCQ Questions</strong> related to {topicTitle}</li>
                                            <li>✓ <strong>Fixed Set:</strong> Questions are specific to this topic</li>
                                            <li>✓ <strong>Immediate Results:</strong> See your score after completing</li>
                                            <li>✓ <strong>Single Attempt:</strong> Each question counts</li>
                                        </ul>
                                    </GlassCard>

                                    {/* Duration */}
                                    <div>
                                        <label className="text-sm font-semibold text-gray-700 mb-3 block">
                                            Duration (seconds)
                                        </label>
                                        <div className="flex gap-2">
                                            {[30, 40, 50, 60].map(n => (
                                                <button
                                                    key={n}
                                                    onClick={() => setTestDuration(n)}
                                                    className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                                                        testDuration === n
                                                            ? 'bg-brand text-white shadow-lg scale-105'
                                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                    }`}
                                                >
                                                    {n}s
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Summary */}
                                    <div className="bg-gradient-to-r from-brand/10 to-pink-100 border border-brand/20 rounded-xl p-4">
                                        <p className="text-sm text-gray-800">
                                            <span className="font-semibold">✨ Ready?</span> You'll answer 5 MCQ questions in {testDuration} seconds. Complete all questions to see your score!
                                        </p>
                                    </div>
                                </div>

                                {/* Footer */}
                                <div className="sticky bottom-0 bg-gray-50 border-t px-6 sm:px-8 py-4 sm:py-6 flex gap-3 sm:gap-4">
                                    <button
                                        onClick={handleClose}
                                        className="flex-1 px-4 py-3 rounded-lg font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <GradientButton
                                        onClick={handleStart}
                                        disabled={loading}
                                        className="flex-1 px-4 py-3 text-base flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Loading Questions...
                                            </>
                                        ) : (
                                            <>
                                                <ClipboardList className="w-5 h-5" />
                                                Start Topic Test
                                            </>
                                        )}
                                    </GradientButton>
                                </div>
                            </>
                        )}

                        {/* ACTIVE TEST MODE */}
                        {mode === 'active' && currentQuestion && (
                            <>
                                {/* Header with timer and progress */}
                                <div className="sticky top-0 bg-white border-b px-6 py-6 sm:px-8">
                                    <div className="flex items-center justify-between mb-4">
                                        <div>
                                            <h2 className="text-lg font-bold text-gray-800">
                                                Question {currentIdx + 1}/{questions.length}
                                            </h2>
                                        </div>
                                        <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-sm font-bold ${
                                            timeLeft === 0 ? 'bg-red-500 text-white animate-pulse' :
                                            timeLeft < 60 ? 'bg-red-100 text-red-700 animate-pulse' :
                                            timeLeft < 300 ? 'bg-amber-100 text-amber-700' :
                                            'bg-gray-100 text-gray-700'
                                        }`}>
                                            <Clock className="w-4 h-4" />
                                            {timeLeft === 0 ? "TIME'S UP!" : formatTime(timeLeft)}
                                        </div>
                                    </div>

                                    {/* Progress bar */}
                                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <motion.div
                                            className="h-full bg-gradient-to-r from-brand to-purple-500 rounded-full"
                                            animate={{ width: `${progress}%` }}
                                            transition={{ duration: 0.3 }}
                                        />
                                    </div>
                                </div>

                                {/* Question Card */}
                                <div className="p-6 sm:p-8 space-y-6">
                                    <GlassCard className="p-6">
                                        <p className="text-lg font-semibold text-gray-800 mb-6">
                                            {currentQuestion.question}
                                        </p>

                                        {/* MCQ Options */}
                                        <div className="space-y-3">
                                            {currentQuestion.options.map((opt, i) => (
                                                <motion.button
                                                    key={i}
                                                    whileHover={{ scale: 1.01 }}
                                                    whileTap={{ scale: 0.99 }}
                                                    onClick={() => handleAnswer(opt)}
                                                    className={`w-full text-left p-4 rounded-xl border-2 transition-all select-none ${
                                                        answers[currentIdx + 1] === opt
                                                            ? 'border-brand bg-brand/5 text-gray-800'
                                                            : 'border-gray-200 hover:border-gray-300 text-gray-600'
                                                    }`}
                                                >
                                                    <span className="font-medium text-sm">{String.fromCharCode(65 + i)}. {opt}</span>
                                                </motion.button>
                                            ))}
                                        </div>
                                    </GlassCard>
                                </div>

                                {/* Navigation */}
                                <div className="sticky bottom-0 bg-gray-50 border-t px-6 sm:px-8 py-4 sm:py-6 space-y-3">
                                    {/* Time's up warning */}
                                    {timeLeft === 0 && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="bg-red-50 border border-red-200 rounded-lg p-3 text-center"
                                        >
                                            <p className="text-sm font-semibold text-red-700">⏱️ Time's Up! Test submitted automatically.</p>
                                        </motion.div>
                                    )}
                                    
                                    <div className="flex gap-3">
                                        <button
                                            onClick={handlePrev}
                                            disabled={currentIdx === 0}
                                            className={`flex items-center gap-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                                                currentIdx === 0
                                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                            }`}
                                        >
                                            <ArrowLeft className="w-4 h-4" /> Previous
                                        </button>

                                        {currentIdx === questions.length - 1 ? (
                                            <GradientButton
                                                onClick={finishTest}
                                                className="flex-1 flex items-center justify-center gap-2"
                                            >
                                                <CheckCircle2 className="w-5 h-5" />
                                                Submit & See Results
                                            </GradientButton>
                                        ) : (
                                            <>
                                                <GradientButton
                                                    onClick={handleNext}
                                                    className="flex-1 flex items-center justify-center gap-2"
                                                >
                                                    Next <ArrowRight className="w-4 h-4" />
                                                </GradientButton>
                                                
                                                <button
                                                    onClick={finishTest}
                                                    className="flex-shrink-0 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
                                                    title="Submit your current answers"
                                                >
                                                    <CheckCircle2 className="w-4 h-4" />
                                                    Submit
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </>
                        )}

                        {/* RESULTS MODE */}
                        {mode === 'results' && (
                            <>
                                {/* Header */}
                                <div className="sticky top-0 bg-gradient-to-r from-brand via-pink-400 to-rose-400 px-6 py-6 sm:px-8 flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">Test Completed!</h2>
                                        <p className="text-white/80 text-sm">{topicTitle}</p>
                                    </div>
                                    <button
                                        onClick={handleClose}
                                        className="flex-shrink-0 p-2 hover:bg-white/20 rounded-full transition-colors"
                                    >
                                        <X className="w-6 h-6 text-white" />
                                    </button>
                                </div>

                                {/* Main Results Card */}
                                <div className="p-6 sm:p-8 space-y-8">
                                    {!showDetails ? (
                                        <>
                                            {/* Score Card - Main Display */}
                                            <motion.div
                                                initial={{ scale: 0.8, opacity: 0, y: 20 }}
                                                animate={{ scale: 1, opacity: 1, y: 0 }}
                                                transition={{ type: 'spring', damping: 15 }}
                                                className="bg-gradient-to-br from-teal-50 to-emerald-50 border-2 border-teal-200 rounded-3xl p-8 sm:p-12"
                                            >
                                                <div className="flex flex-col items-center gap-6">
                                                    {/* Checkmark Circle */}
                                                    <motion.div
                                                        initial={{ scale: 0, rotate: -180 }}
                                                        animate={{ scale: 1, rotate: 0 }}
                                                        transition={{ type: 'spring', damping: 12, delay: 0.2 }}
                                                        className="flex items-center justify-center w-24 h-24 rounded-full bg-teal-100 border-4 border-teal-300"
                                                    >
                                                        <CheckCircle2 className="w-12 h-12 text-teal-500" />
                                                    </motion.div>

                                                    {/* Score Section */}
                                                    <div className="text-center space-y-2">
                                                        <p className="text-lg font-bold text-teal-600 uppercase tracking-wide">Score</p>
                                                        <motion.div
                                                            initial={{ opacity: 0, scale: 0.5 }}
                                                            animate={{ opacity: 1, scale: 1 }}
                                                            transition={{ delay: 0.4 }}
                                                            className="flex items-baseline gap-1 justify-center"
                                                        >
                                                            <span className="text-5xl sm:text-6xl font-black text-teal-700">{score}</span>
                                                            <span className="text-3xl text-teal-500 font-bold mb-2">/</span>
                                                            <span className="text-3xl sm:text-4xl font-bold text-teal-600">{totalPoints}</span>
                                                        </motion.div>
                                                    </div>

                                                    {/* Percentage */}
                                                    <motion.div
                                                        initial={{ opacity: 0, y: 10 }}
                                                        animate={{ opacity: 1, y: 0 }}
                                                        transition={{ delay: 0.6 }}
                                                        className={`text-4xl font-black ${
                                                            percentage >= 80 ? 'text-green-600' :
                                                            percentage >= 60 ? 'text-yellow-600' :
                                                            'text-red-500'
                                                        }`}
                                                    >
                                                        {percentage}%
                                                    </motion.div>

                                                    {/* Message */}
                                                    <motion.p
                                                        initial={{ opacity: 0 }}
                                                        animate={{ opacity: 1 }}
                                                        transition={{ delay: 0.8 }}
                                                        className="text-sm text-teal-600 font-medium"
                                                    >
                                                        This is your final result. Single attempt test.
                                                    </motion.p>
                                                </div>
                                            </motion.div>

                                            {/* Performance Message */}
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                transition={{ delay: 1 }}
                                                className={`p-6 rounded-xl text-center text-sm font-medium ${
                                                    percentage >= 80 ? 'bg-green-100 text-green-700 border border-green-300' :
                                                    percentage >= 60 ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' :
                                                    'bg-red-100 text-red-700 border border-red-300'
                                                }`}
                                            >
                                                {percentage >= 80 ? '🎉 Excellent! You mastered this topic!' :
                                                 percentage >= 60 ? '👍 Good effort! Review the concepts and try again.' :
                                                 '📚 Keep learning! Review this topic and attempt again.'}
                                            </motion.div>
                                        </>
                                    ) : (
                                        <>
                                            {/* Detailed Results View */}
                                            <GlassCard className="p-6">
                                                <h3 className="font-bold text-lg text-gray-800 mb-4">Question Review</h3>
                                                <div className="space-y-3 max-h-96 overflow-y-auto">
                                                    {questions.map((q, idx) => {
                                                        const userAnswer = answers[idx + 1];
                                                        const isCorrect = userAnswer === q.correctAnswer;
                                                        
                                                        return (
                                                            <div
                                                                key={idx}
                                                                className={`p-4 rounded-lg border-l-4 ${
                                                                    isCorrect
                                                                        ? 'bg-green-50 border-green-400'
                                                                        : 'bg-red-50 border-red-400'
                                                                }`}
                                                            >
                                                                <div className="flex items-start gap-3">
                                                                    {isCorrect ? (
                                                                        <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                                                    ) : (
                                                                        <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                                                                    )}
                                                                    <div className="flex-1 min-w-0">
                                                                        <p className="text-xs font-bold text-gray-600 mb-1">Question {idx + 1}</p>
                                                                        <p className="text-sm font-medium text-gray-800 mb-2">{q.question}</p>
                                                                        <p className="text-xs mb-1">
                                                                            <span className="font-semibold text-gray-700">Your answer:</span>
                                                                            <span className={`ml-1 ${isCorrect ? 'text-green-700 font-semibold' : 'text-red-700 font-semibold'}`}>
                                                                                {userAnswer || '(Not answered)'}
                                                                            </span>
                                                                        </p>
                                                                        {!isCorrect && (
                                                                            <p className="text-xs">
                                                                                <span className="font-semibold text-gray-700">Correct answer:</span>
                                                                                <span className="ml-1 text-green-700 font-semibold">{q.correctAnswer}</span>
                                                                            </p>
                                                                        )}
                                                                        {q.explanation && (
                                                                            <p className="text-xs text-gray-600 mt-2 italic border-t border-gray-200 pt-2">
                                                                                💡 {q.explanation}
                                                                            </p>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </GlassCard>
                                        </>
                                    )}
                                </div>

                                {/* Footer - Action Buttons */}
                                <div className="sticky bottom-0 bg-gray-50 border-t px-6 sm:px-8 py-4 sm:py-6 flex gap-3 flex-wrap">
                                    {!showDetails ? (
                                        <>
                                            <GradientButton
                                                onClick={() => setShowDetails(true)}
                                                className="flex-1 min-w-32 px-4 py-3 text-sm flex items-center justify-center gap-2"
                                            >
                                                <Eye className="w-4 h-4" />
                                                View Details
                                            </GradientButton>
                                            <button
                                                onClick={handleClose}
                                                className="flex-1 min-w-32 px-4 py-3 text-sm font-medium rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                                            >
                                                Close
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <button
                                                onClick={() => setShowDetails(false)}
                                                className="flex-1 min-w-32 px-4 py-3 text-sm font-medium rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <ArrowLeft className="w-4 h-4" />
                                                Back
                                            </button>
                                            <button
                                                onClick={handleClose}
                                                className="flex-1 min-w-32 px-4 py-3 text-sm font-medium rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
                                            >
                                                Close
                                            </button>
                                        </>
                                    )}
                                </div>
                            </>
                        )}
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
