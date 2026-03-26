import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { quizAPI, topicsAPI, progressAPI, aiAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { useAntiCheat } from '../context/AntiCheatContext';
import { useAuth } from '../context/AuthContext';
import { useLearningTimer } from '../context/LearningTimerContext';
import { motion } from 'framer-motion';
import { sanitizeMojibakeText } from '../lib/text';
import {
    ClipboardList, CheckCircle2, XCircle, Clock, AlertTriangle,
    ArrowRight, ArrowLeft, Trophy, Shield, Loader2,
    PenLine, List, MessageSquare, BarChart3
} from 'lucide-react';

type QuestionType = 'mcq' | 'fillup' | 'written';

interface MockQuestion {
    id: number;
    type: QuestionType;
    question: string;
    options?: string[];
    correctAnswer: string;
    correctIdx?: number;
    explanation: string;
    points: number;
}

interface QuestionEvaluation {
    isAnswered: boolean;
    isCorrect: boolean;
    awardedPoints: number;
}

type TestMode = 'setup' | 'active' | 'review';

const normalizeQuestionType = (rawType: unknown): QuestionType => {
    const t = String(rawType || '').toLowerCase();
    if (['written', 'qa', 'q&a', 'subjective', 'essay', 'long_answer'].includes(t)) return 'written';
    if (['fillup', 'fill_up', 'fill-in-the-blank', 'fillintheblank', 'blank'].includes(t)) return 'fillup';
    return 'mcq';
};

const dedupeQuestions = (source: MockQuestion[]): MockQuestion[] => {
    const seen = new Set<string>();
    return source.filter((q) => {
        const key = `${q.type}::${String(q.question || '').trim().toLowerCase()}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
};

const buildBalancedQuestionSet = (
    source: MockQuestion[],
    selectedTypes: QuestionType[],
    targetCount: number
): MockQuestion[] => {
    if (selectedTypes.length === 0 || targetCount <= 0) return [];

    const uniqueSource = dedupeQuestions(source);

    const grouped: Record<QuestionType, MockQuestion[]> = {
        mcq: uniqueSource.filter(q => q.type === 'mcq'),
        fillup: uniqueSource.filter(q => q.type === 'fillup'),
        written: uniqueSource.filter(q => q.type === 'written'),
    };

    const shuffled = (arr: MockQuestion[]) => {
        const next = [...arr];
        for (let i = next.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [next[i], next[j]] = [next[j], next[i]];
        }
        return next;
    };

    const buckets: Record<QuestionType, MockQuestion[]> = {
        mcq: shuffled(grouped.mcq),
        fillup: shuffled(grouped.fillup),
        written: shuffled(grouped.written),
    };

    const result: MockQuestion[] = [];
    const used = new Set<string>();

    const takeNext = (type: QuestionType): MockQuestion | null => {
        const bucket = buckets[type];
        while (bucket.length > 0) {
            const candidate = bucket.shift()!;
            const key = `${candidate.type}::${String(candidate.question || '').trim().toLowerCase()}`;
            if (used.has(key)) continue;
            used.add(key);
            return candidate;
        }
        return null;
    };

    // First pass: ensure every selected type appears at least once.
    selectedTypes.forEach((type) => {
        const next = takeNext(type);
        if (next) result.push(next);
    });

    let hasProgress = true;
    while (result.length < targetCount && hasProgress) {
        hasProgress = false;
        for (const type of selectedTypes) {
            if (result.length >= targetCount) break;
            const next = takeNext(type);
            if (!next) continue;
            result.push(next);
            hasProgress = true;
        }
    }

    return result.slice(0, targetCount).map((q, idx) => ({ ...q, id: idx + 1 }));
};

const shuffleQuestions = (arr: MockQuestion[]): MockQuestion[] => {
    const next = [...arr];
    for (let i = next.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        [next[i], next[j]] = [next[j], next[i]];
    }
    return next;
};

const mapToMockQuestion = (q: any, idx: number): MockQuestion => {
    const options = Array.isArray(q.options) ? q.options : [];
    const normalizedType = normalizeQuestionType(q.type);
    const numericCorrect = typeof q.correctAnswer === 'number' ? q.correctAnswer : q.correctIdx;
    const resolvedCorrect = typeof numericCorrect === 'number'
        ? (options[numericCorrect] || '')
        : (q.correctAnswer || q.answer || '');

    return {
        id: idx + 1,
        type: normalizedType,
        question: sanitizeMojibakeText(q.question || q.text || ''),
        options,
        correctAnswer: String(resolvedCorrect || ''),
        correctIdx: typeof numericCorrect === 'number' ? numericCorrect : undefined,
        explanation: sanitizeMojibakeText(q.explanation || ''),
        points: q.points || (normalizedType === 'written' ? 15 : 10),
    };
};

const evaluateQuestion = (question: MockQuestion, rawAnswer?: string): QuestionEvaluation => {
    const userAnswer = String(rawAnswer || '').trim().toLowerCase();
    const correct = question.correctAnswer.trim().toLowerCase();
    const isAnswered = userAnswer.length > 0;

    if (!isAnswered) {
        return { isAnswered: false, isCorrect: false, awardedPoints: 0 };
    }

    if (question.type === 'mcq') {
        const isCorrect = userAnswer === correct;
        return { isAnswered: true, isCorrect, awardedPoints: isCorrect ? question.points : 0 };
    }

    if (question.type === 'fillup') {
        const isCorrect = userAnswer === correct || correct.includes(userAnswer);
        return { isAnswered: true, isCorrect, awardedPoints: isCorrect ? question.points : 0 };
    }

    const keywords = correct.split(/\s+/).filter(w => w.length > 3);
    const matched = keywords.filter(k => userAnswer.includes(k));
    const ratio = keywords.length > 0 ? matched.length / keywords.length : 0;
    const awardedPoints = Math.round(question.points * ratio);
    const isCorrect = ratio > 0.5;
    return { isAnswered: true, isCorrect, awardedPoints };
};

const SAMPLE_QUESTIONS: MockQuestion[] = [
    {
        id: 1, type: 'mcq', question: 'What is the output of `print(type([]))` in Python?',
        options: ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"],
        correctAnswer: "<class 'list'>", correctIdx: 0, explanation: '[] creates an empty list in Python.', points: 10,
    },
    {
        id: 2, type: 'fillup', question: 'In JavaScript, the keyword ___ is used to declare a constant variable.',
        correctAnswer: 'const', explanation: 'The "const" keyword declares a block-scoped constant.', points: 10,
    },
    {
        id: 3, type: 'mcq', question: 'Which data structure uses FIFO (First In First Out)?',
        options: ['Stack', 'Queue', 'Tree', 'Graph'],
        correctAnswer: 'Queue', correctIdx: 1, explanation: 'Queue follows FIFO - first element inserted is the first removed.', points: 10,
    },
    {
        id: 4, type: 'written', question: 'Explain the difference between == and === in JavaScript.',
        correctAnswer: '== checks value equality with type coercion, === checks both value and type without coercion',
        explanation: '== is loose equality (performs type coercion), === is strict equality (no type coercion).', points: 15,
    },
    {
        id: 5, type: 'fillup', question: 'The time complexity of binary search is O(___)',
        correctAnswer: 'log n', explanation: 'Binary search halves the search space each step, giving O(log n).', points: 10,
    },
    {
        id: 6, type: 'mcq', question: 'Which HTTP method is used to update an existing resource?',
        options: ['GET', 'POST', 'PUT', 'DELETE'],
        correctAnswer: 'PUT', correctIdx: 2, explanation: 'PUT is used to update/replace an existing resource.', points: 10,
    },
    {
        id: 7, type: 'written', question: 'What is the purpose of the virtual DOM in React?',
        correctAnswer: 'The virtual DOM is a lightweight copy of the real DOM that React uses to optimize updates by only re-rendering changed components',
        explanation: 'Virtual DOM allows React to batch and minimize actual DOM manipulations for better performance.', points: 15,
    },
    {
        id: 8, type: 'fillup', question: 'In CSS, the ___ property is used to make a flex container.',
        correctAnswer: 'display', explanation: 'display: flex creates a flex container.', points: 10,
    },
    {
        id: 9, type: 'mcq', question: 'What does SQL stand for?',
        options: ['Structured Query Language', 'Simple Query Language', 'Standard Query Logic', 'System Query Language'],
        correctAnswer: 'Structured Query Language', correctIdx: 0, explanation: 'SQL = Structured Query Language, used for managing relational databases.', points: 10,
    },
    {
        id: 10, type: 'written', question: 'Describe what a REST API is and give one example of its use.',
        correctAnswer: 'REST API is an architectural style for building web services that uses HTTP methods. Example: A weather API that returns weather data when you send a GET request.',
        explanation: 'REST (Representational State Transfer) uses standard HTTP methods for CRUD operations.', points: 15,
    },
];

export const MockTest = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const { startTracking, stopTracking } = useLearningTimer();
    const topicId = searchParams.get('topicId') || '';
    const subtopicId = searchParams.get('subtopicId') || '';
    const isTopicContextTest = Boolean(topicId);
    const { setTestActive, warnings, maxWarnings } = useAntiCheat();

    const [drawerOpen, setDrawerOpen] = useState(false);
    const [mode, setMode] = useState<TestMode>('setup');
    const [questions, setQuestions] = useState<MockQuestion[]>([]);
    const [currentIdx, setCurrentIdx] = useState(0);
    const [answers, setAnswers] = useState<Record<number, string>>({});
    const [timeLeft, setTimeLeft] = useState(0);
    const [totalTime, setTotalTime] = useState(0);
    const [score, setScore] = useState(0);
    const [loading, setLoading] = useState(false);
    const [testAlreadyCompleted, setTestAlreadyCompleted] = useState(false);

    // Setup options
    const [questionCount, setQuestionCount] = useState(isTopicContextTest ? 5 : 10);
    const [testDuration, setTestDuration] = useState(15); // minutes
    const [selectedTypes, setSelectedTypes] = useState<QuestionType[]>(isTopicContextTest ? ['mcq'] : ['mcq', 'fillup', 'written']);
    const [topicFilter, setTopicFilter] = useState(searchParams.get('topic') || topicId || '');
    const startedTopicModeRef = useRef(false);

    useEffect(() => {
        if (!isTopicContextTest) return;
        setQuestionCount(5);
        setSelectedTypes(['mcq']);

        // Check if test already completed for this topic
        if (user?.id && topicId) {
            const resultsKey = `edutwin-mock-results_${user.id}`;
            const stored = localStorage.getItem(resultsKey);
            if (stored) {
                try {
                    const results = JSON.parse(stored);
                    const existingResult = results.find((r: any) => r.topicId === topicId || r.topic === topicId);
                    if (existingResult) {
                        setTestAlreadyCompleted(true);
                    }
                } catch (e) {
                    // ignore
                }
            }
        }
    }, [isTopicContextTest, user?.id, topicId]);

    // Timer
    useEffect(() => {
        if (mode !== 'active' || timeLeft <= 0) return;
        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    finishTest();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [mode, timeLeft]);

    useEffect(() => {
        if (mode !== 'active') return;

        window.history.pushState({ mockTestGuard: true }, '');
        const handlePopState = () => {
            setCurrentIdx((prev) => {
                if (prev > 0) {
                    window.history.pushState({ mockTestGuard: true }, '');
                    return prev - 1;
                }
                return prev;
            });
            window.history.pushState({ mockTestGuard: true }, '');
        };

        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [mode]);

    // Activate anti-cheat during test
    useEffect(() => {
        if (mode === 'active') {
            setTestActive(true);
        } else {
            setTestActive(false);
        }
        return () => setTestActive(false);
    }, [mode, setTestActive]);

    // Stop tracking when component unmounts or user navigates away
    useEffect(() => {
        return () => {
            if (mode === 'active') {
                stopTracking();
            }
        };
    }, [mode, stopTracking]);

    const fillWithUniqueTopicBankQuestions = useCallback(async (
        baseQuestions: MockQuestion[],
        targetCount: number,
        allowedTypes: QuestionType[]
    ): Promise<MockQuestion[]> => {
        if (baseQuestions.length >= targetCount) {
            return baseQuestions.slice(0, targetCount).map((q, idx) => ({ ...q, id: idx + 1 }));
        }

        const existing = dedupeQuestions(baseQuestions);
        const existingKeys = new Set(
            existing.map((q) => `${q.type}::${String(q.question || '').trim().toLowerCase()}`)
        );

        try {
            const topicsRes = await topicsAPI.getAll();
            const topics = topicsRes.data?.data?.topics || [];

            const topicPool: MockQuestion[] = [];
            topics.forEach((topic: any) => {
                const quizQuestions = Array.isArray(topic?.quiz) ? topic.quiz : [];
                quizQuestions.forEach((question: any) => {
                    topicPool.push(mapToMockQuestion(question, topicPool.length));
                });
            });

            const allowedPool = dedupeQuestions(topicPool)
                .filter((q) => allowedTypes.includes(q.type))
                .filter((q) => {
                    const key = `${q.type}::${String(q.question || '').trim().toLowerCase()}`;
                    return !existingKeys.has(key);
                });

            const needed = Math.max(0, targetCount - existing.length);
            const supplement = shuffleQuestions(allowedPool).slice(0, needed);
            const merged = [...existing, ...supplement];

            if (merged.length >= targetCount) {
                return merged.slice(0, targetCount).map((q, idx) => ({ ...q, id: idx + 1 }));
            }
        } catch {
            // If topic bank fetch fails, return what we currently have and let fallback logic run.
        }

        return existing.map((q, idx) => ({ ...q, id: idx + 1 }));
    }, []);

    const startTest = useCallback(async () => {
        setLoading(true);
        let preparedQuestions: MockQuestion[] = [];
        try {
            if (isTopicContextTest) {
                // Topic context: strictly 5 MCQs from the current learned topic/subtopic
                const topicQuizRes = await topicsAPI.getQuiz(topicId, subtopicId || undefined);
                const topicQuiz = topicQuizRes.data?.data?.quiz || topicQuizRes.data?.data?.questions || [];
                const mappedTopicQuiz = (topicQuiz || []).map((q: any, i: number) => ({
                    id: i + 1,
                    type: 'mcq' as QuestionType,
                    question: sanitizeMojibakeText(q.question || q.text || ''),
                    options: Array.isArray(q.options) ? q.options : [],
                    correctAnswer: typeof q.correctAnswer === 'number'
                        ? (q.options?.[q.correctAnswer] || '')
                        : (q.correctAnswer || q.options?.[q.correctIdx] || ''),
                    correctIdx: typeof q.correctAnswer === 'number' ? q.correctAnswer : q.correctIdx,
                    explanation: sanitizeMojibakeText(q.explanation || ''),
                    points: q.points || 10,
                })) as MockQuestion[];

                const mcqs = dedupeQuestions(mappedTopicQuiz.filter((q) => q.options && q.options.length >= 2));
                preparedQuestions = buildBalancedQuestionSet(mcqs, ['mcq'], 5);

                if (preparedQuestions.length === 0) {
                    throw new Error('No topic-specific MCQs available');
                }
                setQuestions(preparedQuestions);
            } else {
                // Custom topic AI quiz - try AI generation first for any topic
                if (topicFilter && topicFilter.trim() !== '') {
                    try {
                        console.log(`🚀 Requesting AI-generated questions for custom topic: ${topicFilter}`);
                        const res = await aiAPI.customTopicQuiz(topicFilter, questionCount, 'mixed');
                        const aiQuestions = res.data?.data?.questions || [];
                        
                        if (aiQuestions.length > 0) {
                            console.log(`✅ Received ${aiQuestions.length} AI-generated questions for "${topicFilter}"`);
                            const mapped = aiQuestions.map((q: any, i: number) => mapToMockQuestion(q, i)) as MockQuestion[];
                            
                            const filteredByType = mapped.filter((q: MockQuestion) => selectedTypes.includes(q.type));
                            preparedQuestions = buildBalancedQuestionSet(filteredByType, selectedTypes, questionCount);
                            
                            // Accept if we got at least 3 questions, pad if needed
                            if (preparedQuestions.length >= 3) {
                                if (preparedQuestions.length < questionCount) {
                                    preparedQuestions = await fillWithUniqueTopicBankQuestions(preparedQuestions, questionCount, selectedTypes);
                                }
                                setQuestions(preparedQuestions);
                            } else {
                                throw new Error(`AI returned insufficient questions: ${preparedQuestions.length}`);
                            }
                        } else {
                            throw new Error('AI returned no questions');
                        }
                    } catch (aiError: any) {
                        console.warn(`⚠️ AI custom topic failed: ${aiError?.message}. Falling back to mock test...`);
                        
                        // Fallback to generic mock test
                        const res = await quizAPI.mockTest(
                            undefined,
                            topicFilter,
                            questionCount,
                            true
                        );
                        const apiQuestions = res.data?.data?.mockTest?.questions || res.data?.data?.questions || [];
                        if (apiQuestions.length > 0) {
                            const mapped = apiQuestions.map((q: any, i: number) => mapToMockQuestion(q, i)) as MockQuestion[];
                            const filteredByType = mapped.filter((q: MockQuestion) => selectedTypes.includes(q.type));
                            preparedQuestions = buildBalancedQuestionSet(filteredByType, selectedTypes, questionCount);
                            
                            if (preparedQuestions.length < questionCount) {
                                preparedQuestions = await fillWithUniqueTopicBankQuestions(preparedQuestions, questionCount, selectedTypes);
                            }
                            
                            if (preparedQuestions.length === questionCount) {
                                setQuestions(preparedQuestions);
                            } else {
                                throw new Error('Could not build the requested number of unique questions from API results');
                            }
                        } else {
                            throw new Error('No questions from API');
                        }
                    }
                } else {
                    throw new Error('Topic is required to generate questions');
                }
            }
        } catch {
            // Use sample questions filtered by type
                const fallbackTypes: QuestionType[] = isTopicContextTest ? ['mcq'] : selectedTypes;
            const fallbackCount = isTopicContextTest ? 5 : questionCount;
            const filtered = dedupeQuestions(SAMPLE_QUESTIONS.filter(q => fallbackTypes.includes(q.type)));
            preparedQuestions = buildBalancedQuestionSet(filtered.length > 0 ? filtered : SAMPLE_QUESTIONS, fallbackTypes, fallbackCount);
            if (!isTopicContextTest && preparedQuestions.length < fallbackCount) {
                preparedQuestions = await fillWithUniqueTopicBankQuestions(preparedQuestions, fallbackCount, fallbackTypes);
            }
            setQuestions(preparedQuestions);
        } finally {
            setLoading(false);
        }

        setAnswers({});
        setCurrentIdx(0);
        setTimeLeft(testDuration * 60);
        setTotalTime(testDuration * 60);
        setMode('active');
        
        // Start tracking learning time for mock test
        const testName = topicId 
            ? `${topicFilter || 'Topic'} Mock Test`
            : `${topicFilter || 'General'} Mock Test`;
        startTracking(`mock-test-${Date.now()}`, testName);
    }, [isTopicContextTest, topicId, subtopicId, selectedTypes, questionCount, testDuration, topicFilter]);

    useEffect(() => {
        if (!isTopicContextTest) return;
        if (startedTopicModeRef.current) return;
        if (mode !== 'setup') return;
        startedTopicModeRef.current = true;
        startTest();
    }, [isTopicContextTest, mode, startTest]);

    const finishTest = useCallback(() => {
        const evaluations = questions.map((q) => evaluateQuestion(q, answers[q.id]));
        const total = evaluations.reduce((sum, e) => sum + e.awardedPoints, 0);
        const answeredCount = evaluations.filter((e) => e.isAnswered).length;
        setScore(total);
        const max = questions.reduce((sum, q) => sum + q.points, 0);
        const percentage = max > 0 ? Math.round((total / max) * 100) : 0;

        // Use user-specific key to isolate test results per user
        const userKey = `edutwin-mock-results_${user?.id || 'guest'}`;
        const stored = localStorage.getItem(userKey);
        const results = stored ? JSON.parse(stored) : [];
        results.unshift({
            id: Date.now().toString(),
            topicId,
            subtopicId,
            topic: topicFilter,
            score: total,
            maxScore: max,
            percentage,
            totalQuestions: questions.length,
            answeredQuestions: answeredCount,
            selectedTypes,
            timeTakenSec: totalTime - timeLeft,
            createdAt: new Date().toISOString(),
        });
        localStorage.setItem(userKey, JSON.stringify(results.slice(0, 200)));

        if (topicId && percentage >= 70) {
            topicsAPI.updateStatus(topicId, { status: 'completed', score: percentage }).catch(() => {});
        }

        // Save mock result to database
        progressAPI.saveMockResult({
            topics: [topicFilter || topicId || 'general'],
            score: total,
            total_questions: questions.length,
            percentage,
            time_taken: totalTime - timeLeft,
        }).catch(() => {});

        // Stop tracking learning time
        stopTracking();
        
        setMode('review');
        setTestActive(false);
    }, [questions, answers, setTestActive, topicFilter, topicId, subtopicId, selectedTypes, totalTime, timeLeft]);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    };

    const maxScore = questions.reduce((sum, q) => sum + q.points, 0);
    const reviewStats = questions.reduce((acc, q) => {
        const evaluation = evaluateQuestion(q, answers[q.id]);
        if (evaluation.isCorrect) acc.correct += 1;
        else acc.wrong += 1;
        return acc;
    }, { correct: 0, wrong: 0 });
    const currentQ = questions[currentIdx];
    const progress = questions.length > 0 ? ((currentIdx + 1) / questions.length) * 100 : 0;

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
            <PageWrapper>
                <div className="lg:ml-64">
                    {/* Test Already Completed Warning */}
                    {isTopicContextTest && testAlreadyCompleted && (
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="py-12 px-4">
                            <GlassCard className="p-8 text-center max-w-md mx-auto border-2 border-yellow-300 bg-yellow-50">
                                <AlertTriangle className="w-16 h-16 text-yellow-600 mx-auto mb-4" />
                                <h2 className="text-2xl font-bold text-yellow-900 mb-2">Test Already Completed</h2>
                                <p className="text-yellow-800 mb-4">
                                    You have already completed the mock test for this topic. Only one attempt is allowed per topic to ensure fair assessment.
                                </p>
                                <p className="text-sm text-yellow-700 mb-6">
                                    Your final result has been recorded and cannot be retaken.
                                </p>
                                <div className="flex flex-col gap-2">
                                    <button
                                        onClick={() => navigate(`/topic?id=${topicId}`)}
                                        className="px-6 py-2.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors"
                                    >
                                        Back to Topic
                                    </button>
                                    <button
                                        onClick={() => navigate('/mock-test-results')}
                                        className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition-colors"
                                    >
                                        View Results
                                    </button>
                                </div>
                            </GlassCard>
                        </motion.div>
                    )}

                    {/* Normal test flow */}
                    {!testAlreadyCompleted && (
                    <>
                    {/* Setup Mode */}
                    {mode === 'setup' && !isTopicContextTest && (
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                            <div className="mb-8">
                                <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                                    <ClipboardList className="w-8 h-8 text-brand" />
                                    Mock Test
                                </h1>
                                <p className="text-gray-500 mt-1">
                                    {isTopicContextTest
                                        ? 'Topic mode: 5 MCQs from your current learned topic'
                                        : 'Challenge yourself with different question formats'}
                                </p>
                            </div>

                            {/* Anti-cheat notice - PROMINENT RULES */}
                            <GlassCard className="p-6 mb-6 border-2 border-red-400 bg-red-50 shadow-lg">
                                <div className="flex items-start gap-4">
                                    <Shield className="w-7 h-7 text-red-600 mt-0.5 flex-shrink-0" />
                                    <div className="flex-1">
                                        <h3 className="font-bold text-red-900 text-lg mb-3">⚠️ MOCK TEST INTEGRITY RULES</h3>
                                        <div className="space-y-3">
                                            <div>
                                                <p className="font-semibold text-red-800 text-sm mb-1">SCREENSHOTS & SCREEN RECORDING</p>
                                                <ul className="text-xs text-red-700 space-y-0.5 ml-4">
                                                    <li>❌ PrintScreen key is disabled</li>
                                                    <li>❌ Shift+PrintScreen is disabled</li>
                                                    <li>❌ Windows+Shift+S (Snipping Tool) is disabled</li>
                                                    <li>❌ Screen recording of any kind is not allowed</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <p className="font-semibold text-red-800 text-sm mb-1">COPY, PASTE & TEXT SHORTCUTS</p>
                                                <ul className="text-xs text-red-700 space-y-0.5 ml-4">
                                                    <li>❌ Ctrl+C (Copy) is disabled</li>
                                                    <li>❌ Ctrl+V (Paste) is disabled</li>
                                                    <li>❌ Ctrl+X (Cut) is disabled</li>
                                                    <li>❌ Ctrl+A (Select All) is disabled</li>
                                                </ul>
                                            </div>
                                            <div>
                                                <p className="font-semibold text-red-800 text-sm mb-1">OTHER RESTRICTIONS</p>
                                                <ul className="text-xs text-red-700 space-y-0.5 ml-4">
                                                    <li>❌ Right-click context menu is disabled</li>
                                                    <li>❌ Developer Tools (F12, F11) access is blocked</li>
                                                    <li>❌ Tab switching will trigger a warning</li>
                                                    <li>❌ Text selection within the test is restricted</li>
                                                </ul>
                                            </div>
                                            <div className="mt-3 p-3 bg-red-100 rounded-lg border border-red-300">
                                                <p className="font-bold text-red-900 text-sm">⛔ CONSEQUENCES:</p>
                                                <p className="text-xs text-red-800 mt-1">After <span className="font-bold text-red-900">{maxWarnings} warnings</span>, your account will be <span className="font-bold text-red-900">SUSPENDED FOR 5 HOURS</span></p>
                                                <p className="text-xs text-red-700 mt-2">Current warnings: <span className="font-bold text-lg text-red-900">{warnings}/{maxWarnings}</span></p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </GlassCard>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                {/* Question Settings */}
                                <GlassCard className="p-6">
                                    <h2 className="font-bold text-gray-800 mb-4">Test Settings</h2>

                                    <div className="mb-4">
                                        <label className="text-sm font-medium text-gray-600 mb-2 block">Topic <span className="text-red-500 font-bold">*</span> (mandatory)</label>
                                        <input
                                            type="text"
                                            value={topicFilter}
                                            onChange={e => setTopicFilter(e.target.value)}
                                            placeholder="e.g., Python, JavaScript..."
                                            disabled={isTopicContextTest}
                                            className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 transition-all ${
                                                topicFilter.trim() === '' 
                                                    ? 'border-red-300 bg-red-50 focus:ring-red-400' 
                                                    : 'border-gray-200 focus:ring-brand/40'
                                            }`}
                                        />
                                        {topicFilter.trim() === '' && (
                                            <p className="text-xs text-red-500 mt-1">⚠️ Topic selection is required to generate questions</p>
                                        )}
                                    </div>

                                    <div className="mb-4">
                                        <label className="text-sm font-medium text-gray-600 mb-2 block">Number of Questions</label>
                                        <div className="flex gap-2">
                                            {[5, 10, 15, 20].map(n => (
                                                <button
                                                    key={n}
                                                    onClick={() => setQuestionCount(n)}
                                                    disabled={isTopicContextTest}
                                                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                                                        questionCount === n
                                                            ? 'bg-brand text-white'
                                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                    }`}
                                                >
                                                    {n}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="mb-4">
                                        <label className="text-sm font-medium text-gray-600 mb-2 block">Duration (minutes)</label>
                                        <div className="flex gap-2">
                                            {[10, 15, 20, 30].map(n => (
                                                <button
                                                    key={n}
                                                    onClick={() => setTestDuration(n)}
                                                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                                                        testDuration === n
                                                            ? 'bg-brand text-white'
                                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                    }`}
                                                >
                                                    {n}m
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </GlassCard>

                                {/* Question Types */}
                                <GlassCard className="p-6">
                                    <h2 className="font-bold text-gray-800 mb-4">Question Types</h2>
                                    <div className="space-y-3">
                                        {([
                                            { type: 'mcq' as QuestionType, label: 'Multiple Choice (Choose)', icon: List, desc: 'Select the correct answer from options' },
                                            { type: 'fillup' as QuestionType, label: 'Fill in the Blanks', icon: PenLine, desc: 'Type the missing word or phrase' },
                                            { type: 'written' as QuestionType, label: 'Written Answer (Q&A)', icon: MessageSquare, desc: 'Write a detailed answer' },
                                        ]).map(({ type, label, icon: Icon, desc }) => (
                                            <button
                                                key={type}
                                                onClick={() => {
                                                        if (isTopicContextTest) return;
                                                    setSelectedTypes(prev =>
                                                        prev.includes(type)
                                                            ? prev.filter(t => t !== type)
                                                            : [...prev, type]
                                                    );
                                                }}
                                                className={`w-full p-4 rounded-xl border-2 text-left transition-all flex items-center gap-3 ${
                                                    selectedTypes.includes(type)
                                                        ? 'border-brand bg-brand/5'
                                                        : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                            >
                                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                                                    selectedTypes.includes(type) ? 'bg-brand/10 text-brand' : 'bg-gray-100 text-gray-400'
                                                }`}>
                                                    <Icon className="w-5 h-5" />
                                                </div>
                                                <div>
                                                    <p className="font-medium text-sm text-gray-800">{label}</p>
                                                    <p className="text-xs text-gray-500">{desc}</p>
                                                </div>
                                                {selectedTypes.includes(type) && (
                                                    <CheckCircle2 className="w-5 h-5 text-brand ml-auto" />
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                </GlassCard>
                            </div>

                            <div className="flex justify-center">
                                <GradientButton
                                    onClick={startTest}
                                    disabled={selectedTypes.length === 0 || loading || topicFilter.trim() === ''}
                                    className="px-12 py-3 text-base"
                                    title={topicFilter.trim() === '' ? 'Please select a topic first' : ''}
                                >
                                    {loading ? (
                                        <span className="flex items-center gap-2"><Loader2 className="w-5 h-5 animate-spin" /> Preparing Test...</span>
                                    ) : (
                                        <span className="flex items-center gap-2"><ClipboardList className="w-5 h-5" /> Start Mock Test</span>
                                    )}
                                </GradientButton>
                            </div>
                        </motion.div>
                    )}

                    {/* Active Test Mode */}
                    {mode === 'active' && currentQ && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            {/* Top bar */}
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <h2 className="text-lg font-bold text-gray-800">
                                        Question {currentIdx + 1}/{questions.length}
                                    </h2>
                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${
                                        currentQ.type === 'mcq' ? 'bg-blue-100 text-blue-700' :
                                        currentQ.type === 'fillup' ? 'bg-green-100 text-green-700' :
                                        'bg-purple-100 text-purple-700'
                                    }`}>
                                        {currentQ.type === 'mcq' ? 'Choose' : currentQ.type === 'fillup' ? 'Fill Up' : 'Q&A'}
                                    </span>
                                    <span className="text-sm text-gray-500">{currentQ.points} pts</span>
                                </div>
                                <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-sm font-bold ${
                                    timeLeft < 60 ? 'bg-red-100 text-red-700 animate-pulse' :
                                    timeLeft < 300 ? 'bg-amber-100 text-amber-700' :
                                    'bg-gray-100 text-gray-700'
                                }`}>
                                    <Clock className="w-4 h-4" />
                                    {formatTime(timeLeft)}
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="h-2 bg-gray-200 rounded-full mb-6 overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-brand to-purple-500 rounded-full"
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>

                            {/* Warning counter */}
                            {warnings > 0 && (
                                <div className="mb-4 flex items-center gap-2 text-amber-600 text-xs bg-amber-50 px-3 py-2 rounded-lg">
                                    <AlertTriangle className="w-4 h-4" />
                                    Warnings: {warnings}/{maxWarnings}
                                </div>
                            )}

                            {/* Question Card */}
                            <GlassCard className="p-6 mb-6">
                                    <p className="text-lg font-semibold text-gray-800 mb-6 select-none" style={{ userSelect: 'none', WebkitUserSelect: 'none' }}>
                                    {sanitizeMojibakeText(currentQ.question)}
                                </p>

                                {/* MCQ Options */}
                                {currentQ.type === 'mcq' && currentQ.options && (
                                    <div className="space-y-3">
                                        {currentQ.options.map((opt, i) => (
                                            <motion.button
                                                key={i}
                                                whileHover={{ scale: 1.01 }}
                                                whileTap={{ scale: 0.99 }}
                                                onClick={() => setAnswers(prev => ({ ...prev, [currentQ.id]: opt }))}
                                                className={`w-full text-left p-4 rounded-xl border-2 transition-all select-none ${
                                                    answers[currentQ.id] === opt
                                                        ? 'border-brand bg-brand/5 text-gray-800'
                                                        : 'border-gray-200 hover:border-gray-300 text-gray-600'
                                                }`}
                                                style={{ userSelect: 'none' }}
                                            >
                                                <span className="font-medium text-sm">{String.fromCharCode(65 + i)}. {opt}</span>
                                            </motion.button>
                                        ))}
                                    </div>
                                )}

                                {/* Fill in the Blank */}
                                {currentQ.type === 'fillup' && (
                                    <div>
                                        <input
                                            type="text"
                                            value={answers[currentQ.id] || ''}
                                            onChange={e => setAnswers(prev => ({ ...prev, [currentQ.id]: e.target.value }))}
                                            placeholder="Type your answer here..."
                                            className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-brand focus:outline-none text-sm transition-all"
                                            autoComplete="off"
                                            onPaste={e => e.preventDefault()}
                                            onCopy={e => e.preventDefault()}
                                            style={{ userSelect: 'none' }}
                                        />
                                        <p className="text-xs text-gray-400 mt-2">Fill in the blank with the correct term</p>
                                    </div>
                                )}

                                {/* Written Answer */}
                                {currentQ.type === 'written' && (
                                    <div>
                                        <textarea
                                            value={answers[currentQ.id] || ''}
                                            onChange={e => setAnswers(prev => ({ ...prev, [currentQ.id]: e.target.value }))}
                                            placeholder="Write your detailed answer here..."
                                            rows={5}
                                            className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-brand focus:outline-none text-sm transition-all resize-none"
                                            autoComplete="off"
                                            onPaste={e => e.preventDefault()}
                                            onCopy={e => e.preventDefault()}
                                            style={{ userSelect: 'none' }}
                                        />
                                        <p className="text-xs text-gray-400 mt-2">Provide a detailed explanation</p>
                                    </div>
                                )}
                            </GlassCard>

                            {/* Navigation */}
                            <div className="flex items-center justify-between">
                                <button
                                    onClick={() => setCurrentIdx(Math.max(0, currentIdx - 1))}
                                    disabled={currentIdx === 0}
                                    className="px-6 py-2.5 rounded-xl text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:opacity-40 transition-colors"
                                >
                                    Previous
                                </button>

                                {/* Question pills */}
                                <div className="hidden md:flex gap-1.5 flex-wrap justify-center max-w-md">
                                    {questions.map((q, i) => (
                                        <button
                                            key={q.id}
                                            onClick={() => setCurrentIdx(i)}
                                            className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${
                                                i === currentIdx ? 'bg-brand text-white' :
                                                answers[q.id] ? 'bg-green-100 text-green-700' :
                                                'bg-gray-100 text-gray-500'
                                            }`}
                                        >
                                            {i + 1}
                                        </button>
                                    ))}
                                </div>

                                {currentIdx < questions.length - 1 ? (
                                    <button
                                        onClick={() => setCurrentIdx(currentIdx + 1)}
                                        className="px-6 py-2.5 rounded-xl text-sm font-medium bg-brand text-white hover:bg-brand/90 transition-colors flex items-center gap-2"
                                    >
                                        Next <ArrowRight className="w-4 h-4" />
                                    </button>
                                ) : (
                                    <GradientButton onClick={finishTest} className="px-6 py-2.5">
                                        Submit Test
                                    </GradientButton>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Review Mode */}
                    {mode === 'review' && (
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                            {/* Test Completed Badge */}
                            <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
                                <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0" />
                                <div>
                                    <h3 className="font-semibold text-green-900">Test Completed Successfully!</h3>
                                    <p className="text-sm text-green-700">Your answers have been submitted and evaluated.</p>
                                </div>
                            </div>

                            {/* Score Card */}
                            <GlassCard className="p-8 text-center mb-8">
                                <Trophy className={`w-16 h-16 mx-auto mb-4 ${
                                    score / maxScore >= 0.7 ? 'text-yellow-500' :
                                    score / maxScore >= 0.4 ? 'text-blue-500' : 'text-gray-400'
                                }`} />
                                <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Complete!</h1>
                                <div className="text-5xl font-bold text-brand mb-2">{score}/{maxScore}</div>
                                <p className="text-gray-500 mb-1">
                                    {Math.round((score / maxScore) * 100)}% score
                                </p>
                                <p className="text-sm text-gray-400">
                                    Time spent: {formatTime(totalTime - timeLeft)}
                                </p>

                                {/* Detailed marks breakdown */}
                                <div className="mt-4 grid grid-cols-3 gap-3 max-w-sm mx-auto">
                                    <div className="bg-green-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-green-600">{reviewStats.correct}</p>
                                        <p className="text-[10px] text-green-600 font-medium">Correct</p>
                                    </div>
                                    <div className="bg-red-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-red-500">{reviewStats.wrong}</p>
                                        <p className="text-[10px] text-red-500 font-medium">Wrong</p>
                                    </div>
                                    <div className="bg-blue-50 rounded-xl p-3">
                                        <p className="text-2xl font-bold text-blue-600">{Math.round((score / maxScore) * 100)}%</p>
                                        <p className="text-[10px] text-blue-600 font-medium">Percentage</p>
                                    </div>
                                </div>

                                <div className="flex gap-3 justify-center mt-6 flex-wrap">
                                    <button
                                        onClick={() => navigate('/mock-test-results')}
                                        className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand text-white hover:bg-brand/90 font-medium text-sm transition-colors"
                                    >
                                        <BarChart3 className="w-4 h-4" /> View Results
                                    </button>
                                    {topicFilter && (
                                        <button
                                            onClick={() => navigate(topicId ? `/topic?id=${topicId}${subtopicId ? `&subtopicId=${subtopicId}` : ''}` : `/topic?id=${topicFilter}`)}
                                            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-50 text-emerald-600 hover:bg-emerald-100 font-medium text-sm transition-colors"
                                        >
                                            <ArrowLeft className="w-4 h-4" /> Back to Topic
                                        </button>
                                    )}
                                </div>
                            </GlassCard>

                            {/* Review Questions */}
                            <h2 className="text-lg font-bold text-gray-800 mb-4">Review Answers</h2>
                            <div className="space-y-4">
                                {questions.map((q, i) => {
                                    const isCorrect = evaluateQuestion(q, answers[q.id]).isCorrect;

                                    return (
                                        <GlassCard key={q.id} className={`p-5 border-l-4 ${isCorrect ? 'border-l-green-400' : 'border-l-red-400'}`}>
                                            <div className="flex items-start gap-3">
                                                {isCorrect ? (
                                                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                                                ) : (
                                                    <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                                                )}
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-semibold text-gray-400">Q{i + 1}</span>
                                                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                                            q.type === 'mcq' ? 'bg-blue-50 text-blue-600' :
                                                            q.type === 'fillup' ? 'bg-green-50 text-green-600' :
                                                            'bg-purple-50 text-purple-600'
                                                        }`}>
                                                            {q.type === 'mcq' ? 'MCQ' : q.type === 'fillup' ? 'Fill Up' : 'Written'}
                                                        </span>
                                                    </div>
                                                    <p className="font-medium text-gray-800 text-sm mb-2">{sanitizeMojibakeText(q.question)}</p>
                                                    <p className="text-sm text-gray-600">
                                                        <span className="font-medium">Your answer:</span> {answers[q.id] || <em className="text-gray-400">Not answered</em>}
                                                    </p>
                                                    <p className="text-sm text-green-600 mt-1">
                                                        <span className="font-medium">Correct:</span> {sanitizeMojibakeText(q.correctAnswer)}
                                                    </p>
                                                    <p className="text-xs text-gray-500 mt-2 bg-gray-50 p-2 rounded-lg">{sanitizeMojibakeText(q.explanation)}</p>
                                                </div>
                                            </div>
                                        </GlassCard>
                                    );
                                })}
                            </div>
                        </motion.div>
                    )}
                    </>
                    )}
                </div>
            </PageWrapper>
        </>
    );
};
