import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp } from '../context/AppContext';
import { topics } from '../data/mockData';
import { ExplanationStyle } from '../types';

export default function MockTest() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { completeTopic, updateScore, incrementConfusion, resetConfusion, preferredStyle, confusionCount, setPreferredStyle } = useApp();

    const topic = topics.find(t => t.id === id);
    const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
    const [selectedOption, setSelectedOption] = useState<number | null>(null);
    const [showCorrection, setShowCorrection] = useState(false);
    const [score, setScore] = useState(0);
    const [isFinished, setIsFinished] = useState(false);
    const [showAdaptiveModal, setShowAdaptiveModal] = useState(false);

    useEffect(() => {
        if (!topic) navigate('/dashboard');
        window.scrollTo(0, 0);
    }, [topic, navigate]);

    if (!topic) return null;

    const questions = topic.quiz;
    const currentQ = questions[currentQuestionIdx];

    const handleOptionSelect = (optIdx: number) => {
        if (showCorrection) return;
        setSelectedOption(optIdx);

        const isCorrect = optIdx === currentQ.correctAnswer;
        if (isCorrect) {
            setScore(prev => prev + 10);
            resetConfusion();
        } else {
            incrementConfusion();
        }

        setShowCorrection(true);
    };

    const handleNext = () => {
        if (confusionCount >= 2) {
            setShowAdaptiveModal(true);
            return;
        }
        proceedToNext();
    };

    const proceedToNext = () => {
        setShowAdaptiveModal(false);
        if (currentQuestionIdx < questions.length - 1) {
            setCurrentQuestionIdx(prev => prev + 1);
            setSelectedOption(null);
            setShowCorrection(false);
        } else {
            handleFinishTest();
        }
    };

    const handleStyleSwitch = (newStyle: ExplanationStyle) => {
        setPreferredStyle(newStyle);
        resetConfusion();
        proceedToNext();
    };

    const handleFinishTest = () => {
        updateScore(score);
        completeTopic(topic.id);
        setIsFinished(true);
    };

    if (isFinished) {
        const percentage = Math.round((score / (questions.length * 10)) * 100);
        let message = "Keep practicing!";
        let emoji = "💪";
        let color = "text-warning";
        let bg = "bg-warning";

        if (percentage >= 80) {
            message = "Outstanding!";
            emoji = "🏆";
            color = "text-success";
            bg = "bg-success";
        } else if (percentage >= 60) {
            message = "Great job!";
            emoji = "🌟";
            color = "text-primary";
            bg = "bg-primary";
        }

        return (
            <div className="min-h-[80vh] flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-card rounded-3xl p-10 max-w-lg w-full text-center relative overflow-hidden"
                >
                    <div className={`absolute top-0 left-0 w-full h-2 ${bg}`} />
                    <div className="w-24 h-24 mx-auto rounded-3xl bg-slate-50 flex items-center justify-center text-6xl shadow-inner mb-6">
                        {emoji}
                    </div>
                    <h2 className={`text-4xl font-bold font-display ${color} mb-2`}>{message}</h2>
                    <p className="text-slate-500 font-medium mb-8">You scored {score} points on {topic.topicName}</p>

                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4">
                            <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Score</p>
                            <p className="text-2xl font-bold font-display text-slate-800">{percentage}%</p>
                        </div>
                        <div className="bg-slate-50 border border-slate-100 rounded-2xl p-4">
                            <p className="text-xs text-slate-400 font-bold uppercase tracking-wider mb-1">Earned</p>
                            <p className="text-2xl font-bold font-display text-primary">+{score} XP</p>
                        </div>
                    </div>

                    <button
                        onClick={() => navigate('/dashboard')}
                        className="w-full py-4 rounded-xl font-bold font-display text-white bg-slate-900 shadow-[0_10px_20px_rgba(15,23,42,0.15)] hover:shadow-[0_15px_30px_rgba(15,23,42,0.25)] hover:bg-slate-800 transition-all duration-300"
                    >
                        Back to Dashboard
                    </button>
                    <p className="mt-4 text-xs font-medium text-slate-400">Your XP and topic progress have been updated.</p>
                </motion.div>
            </div>
        );
    }

    const progress = ((currentQuestionIdx + 1) / questions.length) * 100;

    return (
        <div className="max-w-3xl mx-auto space-y-6 pt-4 pb-12">
            {/* Header & Progress */}
            <div className="flex items-center justify-between mb-2">
                <button
                    onClick={() => navigate(`/topic/${topic.id}`)}
                    className="text-sm font-semibold text-slate-500 hover:text-primary transition-colors flex items-center gap-1.5"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
                    Exit Test
                </button>
                <div className="flex items-center gap-4">
                    <span className="text-sm font-bold font-display text-primary bg-primary/10 px-3 py-1 rounded-lg">Level: {topic.difficulty}</span>
                    <span className="text-sm font-bold font-display text-slate-500 px-3 py-1 bg-white rounded-lg border border-slate-200 shadow-sm">
                        {currentQuestionIdx + 1} / {questions.length}
                    </span>
                </div>
            </div>

            <div className="w-full h-2.5 bg-slate-200/50 rounded-full overflow-hidden shadow-inner mb-8">
                <motion.div
                    className="h-full bg-gradient-to-r from-primary to-accent rounded-full"
                    initial={{ width: `${(currentQuestionIdx / questions.length) * 100}%` }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                />
            </div>

            {/* Question Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentQuestionIdx}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                    className="glass-card rounded-3xl p-8 md:p-12 shadow-[0_20px_50px_rgba(8,112,184,0.04)]"
                >
                    <h2 className="text-2xl md:text-3xl font-bold font-display text-slate-800 leading-tight mb-10">
                        {currentQ.question}
                    </h2>

                    <div className="space-y-4">
                        {currentQ.options.map((opt: string, idx: number) => {
                            let btnClass = "bg-white border-slate-200 text-slate-700 hover:border-primary hover:bg-primary/5 hover:text-primary";
                            let icon = <span className="w-6 h-6 rounded-full border-2 border-slate-300 flex-shrink-0 flex items-center justify-center text-xs font-bold text-slate-400">{String.fromCharCode(65 + idx)}</span>;

                            if (showCorrection) {
                                if (idx === currentQ.correctAnswer) {
                                    btnClass = "bg-success/10 border-success text-success shadow-[0_0_15px_rgba(16,185,129,0.2)]";
                                    icon = <span className="text-xl leading-none">✅</span>;
                                } else if (idx === selectedOption) {
                                    btnClass = "bg-danger/10 border-danger text-danger";
                                    icon = <span className="text-xl leading-none">❌</span>;
                                } else {
                                    btnClass = "opacity-50 border-slate-200 text-slate-400 bg-white";
                                }
                            } else if (idx === selectedOption) {
                                btnClass = "bg-primary/5 border-primary text-primary shadow-sm";
                                icon = <span className="w-6 h-6 rounded-full border-2 border-primary flex-shrink-0 flex items-center justify-center"><div className="w-2.5 h-2.5 bg-primary rounded-full" /></span>;
                            }

                            return (
                                <button
                                    key={idx}
                                    onClick={() => handleOptionSelect(idx)}
                                    disabled={showCorrection}
                                    className={`w-full p-5 rounded-2xl border-2 text-left flex items-center gap-4 transition-all duration-300 ${btnClass}`}
                                >
                                    {icon}
                                    <span className="font-semibold text-lg">{opt}</span>
                                </button>
                            );
                        })}
                    </div>

                    {showCorrection && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-10 flex justify-end"
                        >
                            <button
                                onClick={handleNext}
                                className="px-8 py-3.5 bg-slate-900 text-white rounded-xl font-bold shadow-[0_10px_20px_rgba(15,23,42,0.15)] hover:shadow-[0_15px_30px_rgba(15,23,42,0.25)] hover:bg-slate-800 transition-all flex items-center gap-2 group cursor-pointer"
                            >
                                {currentQuestionIdx < questions.length - 1 ? 'Next Question' : 'Finish Test'}
                                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                            </button>
                        </motion.div>
                    )}
                </motion.div>
            </AnimatePresence>

            {/* Adaptive Modal */}
            <AnimatePresence>
                {showAdaptiveModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
                    >
                        <motion.div
                            initial={{ scale: 0.9, y: 20 }}
                            animate={{ scale: 1, y: 0 }}
                            exit={{ scale: 0.9, y: 20 }}
                            className="bg-white rounded-3xl p-8 max-w-sm w-full shadow-2xl relative overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-accent to-primary" />
                            <div className="text-center mb-6">
                                <span className="text-5xl block mb-4">🤔</span>
                                <h3 className="text-2xl font-bold font-display text-slate-800 mb-2">Need a different approach?</h3>
                                <p className="text-slate-500 font-medium text-sm">You've missed a couple of questions. Would you like to try a different explanation style for the remaining concepts?</p>
                            </div>

                            <div className="space-y-3">
                                {topic.explanations.map(exp => (
                                    <button
                                        key={exp.style}
                                        onClick={() => handleStyleSwitch(exp.style as ExplanationStyle)}
                                        className={`w-full p-4 rounded-xl border flex items-center justify-between transition-all group hover:border-primary/50 hover:bg-primary/5
                                            ${preferredStyle === exp.style ? 'border-primary bg-primary/5 ring-1 ring-primary/20' : 'border-slate-200'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">{exp.icon}</span>
                                            <span className="font-bold text-slate-700">{exp.title}</span>
                                        </div>
                                        {preferredStyle === exp.style && (
                                            <span className="text-xs font-bold text-primary uppercase tracking-wider">Current</span>
                                        )}
                                    </button>
                                ))}
                            </div>

                            <button
                                onClick={proceedToNext}
                                className="w-full mt-6 py-3 text-sm font-bold text-slate-500 hover:text-slate-700 transition-colors"
                            >
                                Skip, continue as is
                            </button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

        </div>
    );
}
