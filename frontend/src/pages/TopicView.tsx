import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { topicsAPI, feedbackAPI, progressAPI } from '../services/api';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { VideoTrackerUI } from '../components/learning/VideoTrackerUI';
import { ConfidenceSlider } from '../components/learning/ConfidenceSlider';
import { FlowchartExplanation } from '../components/learning/FlowchartExplanation';
import type { FlowchartNode } from '../components/learning/FlowchartExplanation';
import { GradientButton } from '../components/ui/GradientButton';
import { GlassCard } from '../components/ui/GlassCard';
import { Link } from 'react-router-dom';
import { ArrowRight, ArrowLeft, BookOpen, FileText, StickyNote, CheckCircle2, Eye, Lightbulb, Workflow, Sparkles, Loader2, Timer, Brain, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUnderstanding } from '../context/UnderstandingContext';
import { useNotifications } from '../context/NotificationContext';
import { useLearningTimer } from '../context/LearningTimerContext';
import { useUserPreferences } from '../context/UserPreferencesContext';
import { useAuth } from '../context/AuthContext';
import { LANGUAGES } from '../hooks/useTranslation';
import { sanitizeMojibakeText } from '../lib/text';

// ─── 4 Explanation Types — The Core Feature ──────────────────────────
type ExplanationType = 'simplified' | 'logical' | 'visual' | 'analogy';

interface ExplanationContent {
    title: string;
    body: string[];
    highlight: string;
    codeExample?: string;
}

const explanationMeta: { id: ExplanationType; label: string; icon: typeof Eye; color: string; bg: string; border: string; desc: string }[] = [
    { id: 'simplified', label: 'Simplified', icon: BookOpen, color: 'text-emerald-600', bg: 'bg-candy-mint/40', border: 'border-emerald-200', desc: 'Plain language, no jargon' },
    { id: 'logical', label: 'Logical', icon: Workflow, color: 'text-pink-600', bg: 'bg-candy-pink/40', border: 'border-pink-200', desc: 'Step-by-step breakdown' },
    { id: 'visual', label: 'Visual', icon: Eye, color: 'text-purple-600', bg: 'bg-candy-lavender/40', border: 'border-purple-200', desc: 'Diagrams & flow charts' },
    { id: 'analogy', label: 'Analogy', icon: Lightbulb, color: 'text-orange-600', bg: 'bg-candy-peach/40', border: 'border-orange-200', desc: 'Real-world comparisons' },
];

const EMPTY_EXPLANATION: ExplanationContent = {
    title: '',
    body: [],
    highlight: '',
};

const sanitizeExplanationText = (text: string) => {
    return sanitizeMojibakeText(text);
};

const buildFlowchartFromBody = (body: string[]): FlowchartNode[] => {
    const cleaned = body
        .map(sanitizeExplanationText)
        .filter(Boolean)
        .filter(line => !line.toLowerCase().startsWith('visualized flow'));

    if (cleaned.length === 0) return [];

    const stepLines = cleaned.filter(line => /^step\s*\d+/i.test(line));
    const source = (stepLines.length > 0 ? stepLines : cleaned).slice(0, 8);

    return source.map((line, idx) => {
        const text = line.replace(/^step\s*\d+\s*[:.-]?\s*/i, '').trim();
        const isDecision = /\?|\b(check|if|whether|more items|decision)\b/i.test(text);
        const isEnd = /\b(stop|exit|done|complete|end|stopiteration)\b/i.test(text) || idx === source.length - 1;
        const type: FlowchartNode['type'] = idx === 0 ? 'start' : isEnd ? 'end' : isDecision ? 'decision' : 'process';

        return {
            id: `auto-flow-${idx + 1}`,
            type,
            label: text.length > 60 ? `${text.slice(0, 60)}...` : text,
            detail: text,
        };
    });
};

const buildAnalogySteps = (body: string[]): string[] => {
    const fullText = sanitizeExplanationText(body.join(' '));
    if (!fullText) return [];

    return fullText
        .split(/(?<=[.!?])\s+/)
        .map(part => part.trim())
        .filter(part => part.length > 8);
};

const buildLogicalSteps = (body: string[]): string[] => {
    const cleaned = body.map(sanitizeExplanationText).filter(Boolean);
    if (cleaned.length === 0) return [];

    const explicitSteps = cleaned
        .filter(line => /^step\s*\d+/i.test(line))
        .map(line => line.replace(/^step\s*\d+\s*[:.-]?\s*/i, '').trim());

    if (explicitSteps.length > 0) return explicitSteps;

    return sanitizeExplanationText(cleaned.join(' '))
        .split(/(?<=[.!?])\s+/)
        .map(part => part.trim())
        .filter(part => part.length > 10)
        .slice(0, 8);
};

const buildAnalogyComparisons = (body: string[]): Array<{ concept: string; realWorld: string }> => {
    const fullText = sanitizeExplanationText(body.join(' '));
    if (!fullText) return [];

    const parts = fullText
        .split(/(?<=[.!?])\s+/)
        .map(p => p.trim())
        .filter(Boolean);

    const comparisons = parts.flatMap((sentence) => {
        const match = sentence.match(/(.+?)\s+is\s+like\s+(.+)/i);
        if (!match) return [];
        return [{ concept: match[1].trim(), realWorld: match[2].trim() }];
    });

    if (comparisons.length > 0) return comparisons.slice(0, 8);

    return parts.slice(0, 6).map((sentence, idx) => ({
        concept: `Concept ${idx + 1}`,
        realWorld: sentence,
    }));
};

export const TopicView = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const topicId = searchParams.get('id') || '';
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [videoProgress, setVideoProgress] = useState(0);
    const [videoEnded, setVideoEnded] = useState(false);
    const [isCompleted, setIsCompleted] = useState(false);
    const [activeTab, setActiveTab] = useState<'pdf' | 'notes'>('pdf');
    const [selectedExplanation, setSelectedExplanation] = useState<ExplanationType>('simplified');
    const [confidence, setConfidence] = useState(40);
    const { saveUnderstanding } = useUnderstanding();
    const { addNotification } = useNotifications();
    const { startTracking, stopTracking, pauseTracking, resumeTracking, elapsedTime, isPaused, getInsight, getTotalLearningHours, getTopicTime } = useLearningTimer();
    const { preferences } = useUserPreferences();
    const location = useLocation();
    const trackingStartedRef = useRef(false);
    const accumulatedTimeRef = useRef(0);
    const wasPausedRef = useRef(false);


    // API-loaded state
    const [topicTitle, setTopicTitle] = useState('');
    const [topicLanguage, setTopicLanguage] = useState('');
    const [topicOverview, setTopicOverview] = useState('');
    const [videoUrl, setVideoUrl] = useState('');
    const [recommendedVideos, setRecommendedVideos] = useState<any[]>([]);
    const [topicNotes, setTopicNotes] = useState('');
    const [translatedNotes, setTranslatedNotes] = useState('');
    const [notesLang, setNotesLang] = useState(preferences.language || 'en');
    const [isTranslatingNotes, setIsTranslatingNotes] = useState(false);
    const [testResult, setTestResult] = useState<any>(null);
    const [hasAttemptedTest, setHasAttemptedTest] = useState(false);
    const [isFetchingFreshVideos, setIsFetchingFreshVideos] = useState(false);
    const [freshVideosError, setFreshVideosError] = useState('');


    const [explanations, setExplanations] = useState<Record<ExplanationType, ExplanationContent>>({
        simplified: EMPTY_EXPLANATION,
        logical: EMPTY_EXPLANATION,
        visual: EMPTY_EXPLANATION,
        analogy: EMPTY_EXPLANATION,
    });
    const [loadingTopic, setLoadingTopic] = useState(true);
    const [flowchartNodes, setFlowchartNodes] = useState<FlowchartNode[] | null>(null);
    const [hasStudyMaterial, setHasStudyMaterial] = useState(false);

    // Fetch topic details
    useEffect(() => {
        if (!topicId) { setLoadingTopic(false); return; }
        setLoadingTopic(true);
        
        // Check if we're returning from study material
        const pauseStateKey = `timer_paused_${topicId}`;
        const pauseState = localStorage.getItem(pauseStateKey);
        const wasReturningFromStudy = pauseState === 'true';
        
        // If returning from study material, resume the tracking
        if (wasReturningFromStudy && trackingStartedRef.current) {
            // Mark that we've resumed, so don't reset on next effect
            localStorage.removeItem(pauseStateKey);
            wasPausedRef.current = true; // Will trigger resume in the location.pathname effect
        } else if (!wasReturningFromStudy) {
            // Only reset if this is a fresh topic load, not a return from study
            trackingStartedRef.current = false;
            accumulatedTimeRef.current = 0;
        }
        
        topicsAPI.getById(topicId)
            .then(res => {
                const topic = res.data?.data?.topic;
                if (topic) {
                    setTopicTitle(topic.topicName || '');
                    setTopicLanguage(topic.language || '');
                    setTopicOverview(topic.overview || '');
                    setIsCompleted(topic.status === 'completed');

                    // Start learning timer (only once per topic or if resumed from study material)
                    if (!trackingStartedRef.current) {
                        startTracking(topicId, topic.topicName || topicId);
                        trackingStartedRef.current = true;
                    } else if (wasReturningFromStudy) {
                        // If we're returning from study and tracking was paused, resume it now
                        resumeTracking();
                    }
                    const videos = topic.recommendedVideos || [];
                    setRecommendedVideos(videos);
                    if (videos.length > 0 && videos[0].youtubeId) {
                        setVideoUrl(`https://www.youtube.com/watch?v=${videos[0].youtubeId}`);
                    }
                    const existingExps = topic.explanations || [];
                    if (existingExps.length > 0) {
                        const parsed: Partial<Record<ExplanationType, ExplanationContent>> = {};
                        for (const exp of existingExps) {
                            const style = exp.style as ExplanationType;
                            if (['simplified', 'logical', 'visual', 'analogy'].includes(style)) {
                                const rawContent = exp.content || '';

                                // Detect flowchart JSON in visual explanation
                                if (style === 'visual' && typeof rawContent === 'string' && rawContent.startsWith('[FLOWCHART]')) {
                                    try {
                                        const json = JSON.parse(rawContent.replace('[FLOWCHART]', ''));
                                        if (json.nodes && Array.isArray(json.nodes)) {
                                            setFlowchartNodes(json.nodes as FlowchartNode[]);
                                        }
                                    } catch {
                                        // Not valid JSON — will fall back to text rendering
                                    }
                                    parsed[style] = {
                                        title: sanitizeExplanationText(exp.title || 'Visual Flowchart'),
                                        body: [], // flowchart takes over rendering
                                        highlight: '',
                                    };
                                } else {
                                    parsed[style] = {
                                        title: sanitizeExplanationText(exp.title || `${style.charAt(0).toUpperCase() + style.slice(1)} Explanation`),
                                        body: typeof rawContent === 'string' ? rawContent.split('\n').filter(Boolean) : [],
                                        highlight: '',
                                        codeExample: exp.codeExample,
                                    };
                                }
                            }
                        }
                        setExplanations(prev => ({ ...prev, ...parsed }));
                    }
                    setTopicNotes(topic.overview || '');

                    // Check if study material exists
                    if (topic.studyMaterial && Object.keys(topic.studyMaterial).length > 0) {
                        setHasStudyMaterial(true);
                    }
                }
            })
            .catch(() => {})
            .finally(() => setLoadingTopic(false));

        // Load test result from localStorage
        if (user?.id && topicId) {
            const resultsKey = `edutwin-mock-results_${user.id}`;
            const stored = localStorage.getItem(resultsKey);
            if (stored) {
                try {
                    const results = JSON.parse(stored);
                    const topicResult = results.find((r: any) => r.topicId === topicId || r.topic === topicId);
                    if (topicResult) {
                        setTestResult(topicResult);
                        setHasAttemptedTest(true);
                    } else {
                        setTestResult(null);
                        setHasAttemptedTest(false);
                    }
                } catch (e) {
                    setTestResult(null);
                    setHasAttemptedTest(false);
                }
            }
        }

        // Load video progress from localStorage
        if (user?.id && topicId) {
            const progressKey = `edutwin-video-progress_${user.id}`;
            const stored = localStorage.getItem(progressKey);
            if (stored) {
                try {
                    const progress = JSON.parse(stored);
                    if (progress[topicId]) {
                        setVideoProgress(progress[topicId]);
                    }
                } catch (e) {
                    // ignore
                }
            }
        }
    }, [topicId, user?.id]);

    // Save video progress to localStorage with user-specific key
    useEffect(() => {
        if (!user?.id || !topicId || videoProgress === 0) return;
        
        const key = `edutwin-video-progress_${user.id}`;
        const stored = localStorage.getItem(key);
        const progress = stored ? JSON.parse(stored) : {};
        progress[topicId] = videoProgress;
        localStorage.setItem(key, JSON.stringify(progress));
    }, [videoProgress, topicId, user?.id]);

    // Save video progress to backend at milestones (25%, 50%, 75%, 90%)
    useEffect(() => {
        if (!user?.id || !topicId || videoProgress === 0 || videoProgress < 25) return;
        
        const milestones = [25, 50, 75, 90, 100];
        const currentMilestone = milestones.find(m => videoProgress >= m && videoProgress < m + 5);
        
        if (currentMilestone) {
            progressAPI.saveTopic({
                topic_id: topicId,
                time_spent: Math.round(elapsedTime),
                status: videoProgress >= 90 ? 'completed' : 'in-progress',
            }).catch(() => {});
        }
    }, [videoProgress, topicId, user?.id, elapsedTime]);

    // Auto-translate notes if saved language is not English
    useEffect(() => {
        if (notesLang !== 'en' && topicNotes && !translatedNotes) {
            setIsTranslatingNotes(true);
            fetch(
                `https://api.mymemory.translated.net/get?q=${encodeURIComponent(topicNotes.slice(0, 500))}&langpair=en|${notesLang}`
            )
                .then(r => r.json())
                .then(data => {
                    if (data.responseData?.translatedText) {
                        setTranslatedNotes(data.responseData.translatedText);
                    }
                })
                .catch(() => {})
                .finally(() => setIsTranslatingNotes(false));
        }
    }, [topicNotes, notesLang]);

    // Keep accumulated time in sync while user is on this topic
    useEffect(() => {
        if (!topicId || !trackingStartedRef.current) return;
        
        const interval = setInterval(() => {
            // Continuously update accumulated time to ensure it's preserved
            accumulatedTimeRef.current = getTopicTime(topicId);
        }, 5000); // Update every 5 seconds
        
        return () => clearInterval(interval);
    }, [topicId, getTopicTime]);

    // Stop tracking and save time to backend when leaving topic or completing
    useEffect(() => {
        return () => { 
            if (trackingStartedRef.current) {
                // Accumulate current session time before stopping
                accumulatedTimeRef.current += elapsedTime;
                stopTracking();
                
                // Save the time spent on this topic to the backend
                const totalTimeSpent = Math.round(accumulatedTimeRef.current);
                if (totalTimeSpent > 0) {
                    progressAPI.saveTopic({
                        topic_id: topicId,
                        time_spent: totalTimeSpent,
                        status: isCompleted ? 'completed' : 'in-progress',
                    }).catch(() => {});
                }
                trackingStartedRef.current = false;
            }
        };
    }, [topicId, isCompleted]);

    // Resume timer if coming back from study material with saved pause state
    useEffect(() => {
        if (!topicId || location.pathname === '/study-material') return;
        
        const savedPauseKey = `timer_pause_${topicId}`;
        const savedPause = localStorage.getItem(savedPauseKey);
        
        if (savedPause) {
            try {
                // Resume from where we paused
                resumeTracking();
            } catch (e) {
                console.log('Could not resume from saved pause state');
            }
        }
    }, [location.pathname, topicId, resumeTracking]);

    // Pause timer when navigating to study material
    useEffect(() => {
        if (location.pathname === '/study-material' && trackingStartedRef.current && !isPaused) {
            pauseTracking();
            wasPausedRef.current = true;
            // Set a flag to indicate we paused for study material (so we know to resume later)
            localStorage.setItem(`timer_paused_${topicId}`, 'true');
        }
    }, [location.pathname, pauseTracking, isPaused, topicId]);

    // Resume timer when coming back to topic view
    useEffect(() => {
        if (topicId && wasPausedRef.current && isPaused && location.pathname !== '/study-material') {
            resumeTracking();
            wasPausedRef.current = false;
        }
    }, [location.pathname, topicId, isPaused, resumeTracking]);

    const insight = getInsight();
    const formatElapsed = (s: number) => {
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return m > 0 ? `${m}m ${sec}s` : `${sec}s`;
    };

    const handleSaveUnderstanding = (value: number, label: string) => {
                saveUnderstanding({ topicId: parseInt(topicId) || 0, topicTitle, value, label });
        if (topicId) {
            const rating = Math.min(5, Math.max(1, Math.ceil(value / 20)));
            feedbackAPI.submit({ topic_id: topicId, rating, comment: label }).catch(() => {});
        }
    };

    const handleComplete = () => {
        if (hasWatchedFull && topicId) {
            // Update accumulated time
            accumulatedTimeRef.current += elapsedTime;
            const totalTimeSpent = Math.round(accumulatedTimeRef.current);
            
            // Update topic status
            topicsAPI.updateStatus(topicId, { status: 'completed', score: 85 }).catch(() => {});
            
            // Save learning time to user progress
            progressAPI.saveTopic({
                topic_id: topicId,
                time_spent: totalTimeSpent,
                status: 'completed',
            }).catch(() => {
                console.log('Failed to save time, but continuing...');
            });
            
            // Stop tracking after saving
            stopTracking();
            
            setIsCompleted(true);
            addNotification({
                type: 'congrats',
                title: 'Congratulations! Topic completed 🎉',
                message: `Great job finishing "${topicTitle}"! Keep up the awesome work.`,
                topicId: parseInt(topicId) || 0,
            });
        }
    };

    const handleFreshVideos = async () => {
        if (!topicId) return;
        
        setIsFetchingFreshVideos(true);
        setFreshVideosError('');
        
        try {
            const response = await topicsAPI.getFreshVideos(topicId, 3);
            const freshVideos = response.data?.data?.recommendedVideos || [];
            
            if (freshVideos.length > 0) {
                setRecommendedVideos(freshVideos);
                if (freshVideos[0].youtubeId) {
                    setVideoUrl(`https://www.youtube.com/watch?v=${freshVideos[0].youtubeId}`);
                }
                addNotification({
                    type: 'success',
                    title: '🎥 Fresh Videos Loaded',
                    message: `Found ${freshVideos.length} fresh videos from YouTube!`,
                    topicId: parseInt(topicId) || 0,
                });
            } else {
                setFreshVideosError('No fresh videos found on YouTube.');
            }
        } catch (error: any) {
            const errorMsg = error.response?.data?.detail || error.message || 'Failed to fetch fresh videos';
            setFreshVideosError(errorMsg);
            
            if (errorMsg.includes('quota')) {
                addNotification({
                    type: 'warning',
                    title: '⚠️ Billing Required',
                    message: 'Enable billing on Google Cloud to access YouTube videos. Click the Fresh Videos button again after enabling.',
                    topicId: parseInt(topicId) || 0,
                });
            }
        } finally {
            setIsFetchingFreshVideos(false);
        }
    };



    const hasWatchedFull = videoProgress >= 95 || videoEnded;
    const currentExplanation = explanations[selectedExplanation];
    const currentMeta = explanationMeta.find(m => m.id === selectedExplanation)!;
    const normalizedBody = currentExplanation.body.map(sanitizeExplanationText).filter(Boolean);
    const computedFlowNodes = selectedExplanation === 'visual'
        ? (flowchartNodes && flowchartNodes.length > 0 ? flowchartNodes : buildFlowchartFromBody(normalizedBody))
        : [];
    const logicalSteps = selectedExplanation === 'logical' ? buildLogicalSteps(normalizedBody) : [];
    const analogySteps = selectedExplanation === 'analogy' ? buildAnalogySteps(normalizedBody) : [];
    const analogyComparisons = selectedExplanation === 'analogy' ? buildAnalogyComparisons(normalizedBody) : [];

    if (loadingTopic) {
        return (
            <>
                <Navbar onMenuClick={() => setDrawerOpen(true)} />
                <Sidebar />
                <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
                <PageWrapper className="lg:pl-64">
                    <div className="flex items-center justify-center min-h-[50vh]">
                        <Loader2 className="w-8 h-8 text-brand animate-spin" />
                    </div>
                </PageWrapper>
            </>
        );
    }

    if (!topicId) {
        return (
            <>
                <Navbar onMenuClick={() => setDrawerOpen(true)} />
                <Sidebar />
                <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
                <PageWrapper className="lg:pl-64">
                    <div className="flex flex-col items-center justify-center min-h-[50vh] text-gray-400 gap-4">
                        <BookOpen className="w-12 h-12 opacity-40" />
                        <p className="text-lg font-medium">No topic selected</p>
                        <Link to="/videos"><GradientButton>Go to Topics</GradientButton></Link>
                    </div>
                </PageWrapper>
            </>
        );
    }

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-5xl mx-auto space-y-8">

                    {/* Header */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <button
                            onClick={() => navigate('/videos')}
                            className="mb-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
                        >
                            <ArrowLeft className="w-4 h-4" /> Back to Topics
                        </button>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand/10 border border-brand/20 rounded-full text-brand text-xs font-bold mb-4">
                            <BookOpen className="w-3.5 h-3.5" /> {topicLanguage || 'Topic'}
                        </div>
                        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">{topicTitle}</h1>
                        <p className="text-lg text-gray-500">{sanitizeExplanationText(topicOverview)}</p>
                    </motion.div>

                    {/* Learning Content */}
                    <motion.div
                        key="learning-content-main"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, delay: 0.1, ease: 'easeOut' }}
                    >

                    {/* Learning Timer & Mindset Insight */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
                        <GlassCard className="p-4">
                            <div className="flex items-center justify-between flex-wrap gap-3">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
                                        <Timer className={`w-5 h-5 ${isPaused ? 'text-orange-600' : 'text-indigo-600'}`} />
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-500 font-medium">Time on this topic {isPaused && <span className="text-orange-600 font-bold">(Paused)</span>}</p>
                                        <p className="text-lg font-bold text-gray-800 font-mono">{formatElapsed(elapsedTime)}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                                        <Brain className="w-5 h-5 text-purple-600" />
                                    </div>
                                    <div className="max-w-sm">
                                        <p className="text-xs text-gray-500 font-medium">Learning Pace: <span className="capitalize font-bold">{insight.pace}</span></p>
                                        <p className="text-xs text-gray-600">{insight.message}</p>
                                    </div>
                                </div>
                            </div>
                            {insight.recommendation && (
                                <p className="text-xs text-brand mt-2 bg-brand/5 px-3 py-1.5 rounded-lg">
                                    💡 {insight.recommendation}
                                </p>
                            )}
                        </GlassCard>
                    </motion.div>

                    {/* ═══════════════════════════════════════════════════════════════
                         SECTION 1: Choose Your Explanation Style  (THE CORE FEATURE)
                         ═══════════════════════════════════════════════════════════════ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="space-y-4">
                        <div className="flex items-center gap-3">
                            <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">1</span>
                            <div>
                                <h2 className="text-xl font-bold text-gray-800">Choose Your Explanation Style</h2>
                                <p className="text-sm text-gray-500">Everyone learns differently — pick the style that clicks for you.</p>
                            </div>
                        </div>

                        {/* 4 Explanation Type Cards */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                            {explanationMeta.map((option) => {
                                const isSelected = selectedExplanation === option.id;
                                return (
                                    <motion.button
                                        key={option.id}
                                        onClick={() => setSelectedExplanation(option.id)}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        className={`relative p-4 rounded-2xl border-2 transition-all text-left overflow-hidden group flex flex-col gap-2 ${
                                            isSelected
                                                ? `${option.bg} ${option.border} shadow-lg`
                                                : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                                        }`}
                                    >
                                        {isSelected && (
                                            <motion.div
                                                layoutId="explanation-glow"
                                                className="absolute inset-0 bg-gradient-to-br from-white/60 to-transparent"
                                                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                                            />
                                        )}
                                        <div className={`relative z-10 p-2 rounded-xl w-fit ${isSelected ? option.bg : 'bg-gray-100'}`}>
                                            <option.icon className={`w-5 h-5 ${isSelected ? option.color : 'text-gray-400'}`} />
                                        </div>
                                        <div className="relative z-10">
                                            <span className={`font-bold text-sm ${isSelected ? 'text-gray-800' : 'text-gray-600'}`}>{option.label}</span>
                                            <p className={`text-xs mt-0.5 ${isSelected ? 'text-gray-600' : 'text-gray-400'}`}>{option.desc}</p>
                                        </div>
                                        {isSelected && (
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                className={`absolute top-2 right-2 w-5 h-5 rounded-full flex items-center justify-center ${option.bg} border ${option.border}`}
                                            >
                                                <CheckCircle2 className={`w-3.5 h-3.5 ${option.color}`} />
                                            </motion.div>
                                        )}
                                    </motion.button>
                                );
                            })}
                        </div>

                        {/* Explanation Content Panel */}
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={selectedExplanation}
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.3 }}
                            >
                                <GlassCard className="p-0 overflow-hidden">
                                    {/* Header bar */}
                                    <div className={`px-6 py-4 ${currentMeta.bg} border-b ${currentMeta.border} flex items-center gap-3`}>
                                        <currentMeta.icon className={`w-5 h-5 ${currentMeta.color}`} />
                                        <div>
                                            <h3 className="font-bold text-gray-800 text-base">{currentExplanation.title || currentMeta.label}</h3>
                                        </div>
                                        <div className="ml-auto">
                                            <Sparkles className={`w-4 h-4 ${currentMeta.color} opacity-60`} />
                                        </div>
                                    </div>

                                    {/* Body */}
                                    <div className="p-6 space-y-3">
                                        {/* Visual tab: always render as flowchart */}
                                        {selectedExplanation === 'visual' && computedFlowNodes.length > 0 ? (
                                            <FlowchartExplanation
                                                nodes={computedFlowNodes}
                                                title="Follow the flow to understand the concept step by step"
                                            />
                                        ) : selectedExplanation === 'logical' && logicalSteps.length > 0 ? (
                                            <div className="space-y-3">
                                                {logicalSteps.map((step, i) => (
                                                    <div key={`${step}-${i}`} className="flex items-start gap-3 rounded-xl border border-pink-200 bg-pink-50/40 p-3">
                                                        <div className="w-6 h-6 rounded-full bg-pink-100 text-pink-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                                                            {i + 1}
                                                        </div>
                                                        <p className="text-sm text-gray-700 leading-relaxed">{step}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : selectedExplanation === 'analogy' && analogySteps.length > 0 ? (
                                            <div className="space-y-3">
                                                {analogyComparisons.length > 0 ? analogyComparisons.map((row, i) => (
                                                    <div key={`${row.concept}-${i}`} className="rounded-xl border border-orange-200 bg-orange-50/40 p-3">
                                                        <div className="flex items-start gap-2 text-sm">
                                                            <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-orange-100 text-orange-700">Concept</span>
                                                            <p className="text-gray-700 leading-relaxed">{row.concept}</p>
                                                        </div>
                                                        <div className="flex items-start gap-2 text-sm mt-2">
                                                            <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-orange-100 text-orange-700">Real World</span>
                                                            <p className="text-gray-700 leading-relaxed">{row.realWorld}</p>
                                                        </div>
                                                    </div>
                                                )) : analogySteps.map((step, i) => (
                                                    <div key={`${step}-${i}`} className="flex items-start gap-3 rounded-xl border border-orange-200 bg-orange-50/40 p-3">
                                                        <div className="w-6 h-6 rounded-full bg-orange-100 text-orange-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                                                            {i + 1}
                                                        </div>
                                                        <p className="text-sm text-gray-700 leading-relaxed">{step}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : currentExplanation.body.length > 0 ? (
                                            <>
                                                {normalizedBody.map((line, i) => {
                                                    if (line === '') return <div key={i} className="h-2" />;
                                                    if (line.startsWith('  ') || line.startsWith('┌') || line.startsWith('│') || line.startsWith('└') || line.startsWith('         ')) {
                                                        return (
                                                            <pre key={i} className="text-xs font-mono text-gray-600 leading-relaxed whitespace-pre">
                                                                {line}
                                                            </pre>
                                                        );
                                                    }
                                                    return (
                                                        <p key={i} className="text-sm text-gray-700 leading-relaxed"
                                                           dangerouslySetInnerHTML={{
                                                               __html: line
                                                                   .replace(/\*\*(.*?)\*\*/g, '<strong class="text-gray-800">$1</strong>')
                                                                   .replace(/`(.*?)`/g, '<code class="px-1.5 py-0.5 bg-gray-100 rounded text-brand text-xs font-mono">$1</code>')
                                                           }}
                                                        />
                                                    );
                                                })}

                                                {/* Code example if present */}
                                                {currentExplanation.codeExample && (
                                                    <div className="mt-4 rounded-xl bg-gray-900 text-gray-100 p-4 overflow-x-auto">
                                                        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-700">
                                                            <span className="w-3 h-3 rounded-full bg-red-400" />
                                                            <span className="w-3 h-3 rounded-full bg-yellow-400" />
                                                            <span className="w-3 h-3 rounded-full bg-green-400" />
                                                            <span className="ml-2 text-xs text-gray-400 font-mono">example.py</span>
                                                        </div>
                                                        <pre className="text-sm font-mono leading-relaxed whitespace-pre">
                                                            {currentExplanation.codeExample}
                                                        </pre>
                                                    </div>
                                                )}
                                            </>
                                        ) : (
                                            <div className="text-center py-8 text-gray-400">
                                                <p className="text-sm">No explanation available for this style yet.</p>
                                            </div>
                                        )}
                                    </div>
                                </GlassCard>
                            </motion.div>
                        </AnimatePresence>

                        {/* Confidence Slider */}
                        <ConfidenceSlider
                            value={confidence}
                            onChange={setConfidence}
                            topicId={topicId ? parseInt(topicId) : undefined}
                            topicTitle={topicTitle}
                            onSave={handleSaveUnderstanding}
                        />
                    </motion.div>

                    {/* ═══ SECTION 2: Watch the Video ═══ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
                        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                            <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">2</span>
                            Watch the Video
                        </h2>
                        {videoUrl ? (
                            <>
                                <VideoTrackerUI
                                    url={videoUrl}
                                    onProgress={(played) => setVideoProgress(played)}
                                    onEnded={() => setVideoEnded(true)}
                                />
                                {/* Video progress indicator */}
                                <div className="flex items-center gap-3">
                                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-brand rounded-full transition-all duration-300"
                                            style={{ width: `${Math.min(videoProgress, 100)}%` }}
                                        />
                                    </div>
                                    <span className="text-sm font-medium text-gray-500">{Math.round(videoProgress)}% watched</span>
                                </div>

                                {/* Get Fresh Videos Button */}
                                <div className="flex gap-3 pt-2">
                                    <button
                                        onClick={handleFreshVideos}
                                        disabled={isFetchingFreshVideos}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg active:scale-95"
                                    >
                                        {isFetchingFreshVideos ? (
                                            <>
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                Fetching...
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="w-4 h-4" />
                                                Get Fresh Videos
                                            </>
                                        )}
                                    </button>
                                </div>

                                {freshVideosError && (
                                    <div className="mt-2 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
                                        {freshVideosError}
                                    </div>
                                )}
                            </>
                        ) : (
                            <GlassCard className="p-8 flex flex-col items-center justify-center gap-4 text-center">
                                <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center">
                                    <svg className="w-8 h-8 text-red-500" viewBox="0 0 24 24" fill="currentColor"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0C.488 3.45.029 5.804 0 12c.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0C23.512 20.55 23.971 18.196 24 12c-.029-6.185-.484-8.549-4.385-8.816zM9 16V8l8 4-8 4z"/></svg>
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-gray-700">No video available for this topic yet</p>
                                    <p className="text-xs text-gray-400 mt-1">Search YouTube for a relevant tutorial</p>
                                </div>
                                <a
                                    href={`https://www.youtube.com/results?search_query=${encodeURIComponent(topicTitle + ' tutorial')}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-red-500 hover:bg-red-600 transition-all shadow-md"
                                >
                                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0C.488 3.45.029 5.804 0 12c.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0C23.512 20.55 23.971 18.196 24 12c-.029-6.185-.484-8.549-4.385-8.816zM9 16V8l8 4-8 4z"/></svg>
                                    Search on YouTube
                                </a>
                            </GlassCard>
                        )}
                    </motion.div>

                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="space-y-3">
                        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                            <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">3</span>
                            Study Materials
                        </h2>

                        {/* Tab Switcher */}
                        <div className="flex gap-2 mb-4">
                            <button
                                onClick={() => setActiveTab('pdf')}
                                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                                    activeTab === 'pdf'
                                        ? 'bg-brand text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                            >
                                <FileText className="w-4 h-4" /> Learning PDF
                            </button>
                            <button
                                onClick={() => setActiveTab('notes')}
                                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                                    activeTab === 'notes'
                                        ? 'bg-brand text-white shadow-md'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                            >
                                <StickyNote className="w-4 h-4" /> Notes
                            </button>
                        </div>

                        {/* PDF and Notes Content — side by side on large screens */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* PDF Viewer */}
                            <GlassCard className={`p-0 overflow-hidden ${activeTab !== 'pdf' ? 'hidden lg:block' : ''}`}>
                                <div className="bg-gray-100 px-4 py-3 border-b border-gray-200 flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-brand" />
                                    <span className="text-sm font-semibold text-gray-700 truncate">Study Material</span>
                                </div>
                                {hasStudyMaterial ? (
                                    <div className="w-full p-6 flex flex-col items-center justify-center gap-5" style={{ minHeight: '360px' }}>
                                        <div className="w-24 h-28 bg-white rounded-xl border-2 border-brand/20 shadow-sm flex flex-col items-center justify-center relative">
                                            <div className="absolute -top-2 -right-2 w-7 h-5 bg-brand rounded-md flex items-center justify-center">
                                                <span className="text-[8px] font-bold text-white tracking-wider">VIEW</span>
                                            </div>
                                            <FileText className="w-10 h-10 text-brand/60" />
                                            <div className="w-12 h-[2px] bg-gray-200 mt-1.5 rounded" />
                                            <div className="w-10 h-[2px] bg-gray-200 mt-1 rounded" />
                                            <div className="w-8 h-[2px] bg-gray-200 mt-1 rounded" />
                                        </div>
                                        <div className="text-center max-w-[280px]">
                                            <h3 className="text-base font-bold text-gray-800 leading-snug">{topicTitle} — Study Material</h3>
                                            <p className="text-xs text-gray-400 mt-1.5">Opens in a full-screen reading view</p>
                                        </div>
                                        <Link
                                            to={`/study-material?topicId=${encodeURIComponent(topicId)}`}
                                            className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-brand hover:bg-brand/90 transition-all shadow-md hover:shadow-lg active:scale-95"
                                        >
                                            <Eye className="w-4 h-4" /> View Study Material
                                        </Link>
                                    </div>
                                ) : (
                                    <div className="w-full h-[300px] flex items-center justify-center text-gray-400">
                                        <div className="text-center">
                                            <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" />
                                            <p className="text-sm">No study material available yet</p>
                                        </div>
                                    </div>
                                )}
                            </GlassCard>

                            {/* Notes Viewer */}
                            <GlassCard className={`p-0 overflow-hidden ${activeTab !== 'notes' ? 'hidden lg:block' : ''}`}>
                                <div className="bg-gray-100 px-4 py-3 border-b border-gray-200 flex items-center gap-2">
                                    <StickyNote className="w-4 h-4 text-brand" />
                                    <span className="text-sm font-semibold text-gray-700">Topic Notes</span>
                                    <select
                                        value={notesLang}
                                        onChange={async (e) => {
                                            const lang = e.target.value;
                                            setNotesLang(lang);
                                            if (lang === 'en') {
                                                setTranslatedNotes('');
                                                return;
                                            }
                                            if (!topicNotes) return;
                                            setIsTranslatingNotes(true);
                                            try {
                                                const res = await fetch(
                                                    `https://api.mymemory.translated.net/get?q=${encodeURIComponent(topicNotes.slice(0, 500))}&langpair=en|${lang}`
                                                );
                                                const data = await res.json();
                                                if (data.responseData?.translatedText) {
                                                    setTranslatedNotes(data.responseData.translatedText);
                                                }
                                            } catch { /* ignore */ }
                                            setIsTranslatingNotes(false);
                                        }}
                                        className="ml-auto text-xs border border-gray-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-brand/30"
                                    >
                                        {LANGUAGES.map(l => (
                                            <option key={l.code} value={l.code}>{l.flag} {l.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="p-6 h-[500px] overflow-y-auto space-y-6">
                                    {isTranslatingNotes && (
                                        <div className="flex items-center gap-2 text-xs text-blue-500 mb-3">
                                            <Loader2 className="w-3 h-3 animate-spin" /> Translating notes...
                                        </div>
                                    )}
                                    {(() => {
                                        const noteText = translatedNotes && notesLang !== 'en' ? translatedNotes : topicNotes;
                                        if (!noteText) {
                                            return <p className="text-gray-400 text-center mt-8">No notes available for this topic.</p>;
                                        }

                                        // Extract key points from overview text
                                        const sentences = noteText.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 10);
                                        const keyPoints = sentences.slice(0, 4).map(sentence => {
                                            // Clean up sentence
                                            return sanitizeExplanationText(sentence)
                                                .replace(/^[•\-]\s*/, '')
                                                .replace(/^[\d+\.]\s*/, '')
                                                .trim();
                                        }).filter(p => p.length > 0);

                                        // Extract technical terms (capitalized words or jargon patterns)
                                        const importantTerms = [...new Set(
                                            noteText.match(/\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b/g) || []
                                        )].slice(0, 8);

                                        return (
                                            <div className="space-y-6">
                                                {/* Overview Section */}
                                                <div>
                                                    <h3 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
                                                        <Lightbulb className="w-4 h-4 text-brand" />
                                                        Overview
                                                    </h3>
                                                    <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
                                                        {sanitizeExplanationText(noteText)}
                                                    </p>
                                                </div>

                                                {/* Key Points Section */}
                                                {keyPoints.length > 0 && (
                                                    <div>
                                                        <h3 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
                                                            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                                                            Key Points
                                                        </h3>
                                                        <ul className="space-y-2">
                                                            {keyPoints.map((point, idx) => (
                                                                <li key={idx} className="flex gap-2 text-xs text-gray-600">
                                                                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand flex-shrink-0 mt-1.5" />
                                                                    <span>{point}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {/* Important Concepts */}
                                                {importantTerms.length > 0 && (
                                                    <div>
                                                        <h3 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
                                                            <Brain className="w-4 h-4 text-purple-600" />
                                                            Key Concepts
                                                        </h3>
                                                        <div className="flex flex-wrap gap-1.5">
                                                            {importantTerms.map((term, idx) => (
                                                                <span
                                                                    key={idx}
                                                                    className="inline-block px-2.5 py-1 bg-purple-50 text-purple-700 text-xs font-medium rounded-lg border border-purple-100"
                                                                >
                                                                    {term}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Full Text with Markdown Support */}
                                                <div className="pt-4 border-t border-gray-200">
                                                    <h3 className="text-xs font-bold text-gray-600 mb-3 uppercase tracking-wider">Full Notes</h3>
                                                    <div className="prose prose-sm max-w-none text-gray-700 text-xs space-y-2">
                                                        {noteText.split('\n').map((line: string, i: number) => {
                                                            const cleanLine = sanitizeExplanationText(line);
                                                            if (cleanLine.startsWith('## ')) return <h4 key={i} className="text-sm font-bold text-gray-800 mt-2">{cleanLine.replace('## ', '')}</h4>;
                                                            if (cleanLine.startsWith('**') && cleanLine.endsWith('**')) return <p key={i} className="font-semibold text-gray-700">{cleanLine.replace(/\*\*/g, '')}</p>;
                                                            if (cleanLine.startsWith('• ') || cleanLine.startsWith('- ')) return <p key={i} className="pl-3 text-gray-600">{cleanLine}</p>;
                                                            if (cleanLine.startsWith('```')) return <div key={i} className="my-1" />;
                                                            if (cleanLine.trim() === '') return null;
                                                            return <p key={i} className="text-gray-600 leading-relaxed">{cleanLine}</p>;
                                                        })}
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>
                            </GlassCard>
                        </div>
                    </motion.div>

                    {/* ═══ SECTION 4: Complete & Take Test ═══ */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 pb-4 border-t border-pink-100"
                    >
                        {/* Complete Button */}
                        <div className="flex items-center gap-3">
                            {isCompleted ? (
                                <div className="flex items-center gap-2 px-5 py-3 bg-green-50 border border-green-200 rounded-xl text-green-700 font-semibold">
                                    <CheckCircle2 className="w-5 h-5" />
                                    Topic Completed!
                                </div>
                            ) : (
                                <button
                                    onClick={handleComplete}
                                    disabled={!hasWatchedFull}
                                    className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold transition-all ${
                                        hasWatchedFull
                                            ? 'bg-green-500 text-white hover:bg-green-600 shadow-md cursor-pointer'
                                            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    }`}
                                >
                                    <CheckCircle2 className="w-5 h-5" />
                                    {hasWatchedFull ? 'Mark Complete' : 'Watch full video to complete'}
                                </button>
                            )}
                        </div>

                        {/* Take Mock Test / Test Result */}
                        {hasAttemptedTest && testResult ? (
                            <GlassCard className="p-6 bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200">
                                <div className="flex items-center gap-4">
                                    <div className="flex-shrink-0 w-16 h-16 rounded-full bg-gradient-to-br from-emerald-300 to-teal-400 flex items-center justify-center">
                                        <CheckCircle2 className="w-8 h-8 text-white" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="text-lg font-bold text-emerald-900">Test Completed!</h3>
                                        <div className="flex items-center gap-4 mt-2">
                                            <div>
                                                <p className="text-xs text-emerald-600 font-medium">Score</p>
                                                <p className="text-2xl font-bold text-emerald-700">{testResult.score}/{testResult.total}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-emerald-600 font-medium">Percentage</p>
                                                <p className={`text-2xl font-bold ${
                                                    testResult.percentage >= 80 ? 'text-green-600' : 
                                                    testResult.percentage >= 50 ? 'text-yellow-600' : 'text-red-500'
                                                }`}>{Math.round(testResult.percentage)}%</p>
                                            </div>
                                        </div>
                                        <p className="text-xs text-emerald-600 mt-2">This is your final result. Only one attempt allowed.</p>
                                    </div>
                                    <button
                                        onClick={() => navigate('/mock-test-results')}
                                        className="flex-shrink-0 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium text-sm transition-colors"
                                    >
                                        View Details
                                    </button>
                                </div>
                            </GlassCard>
                        ) : (
                            <Link to={`/mock-test?topicId=${topicId}&topic=${encodeURIComponent(topicTitle)}`}>
                                <GradientButton className="group text-lg px-8 py-4">
                                    Take Mock Test
                                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                                </GradientButton>
                            </Link>
                        )}
                    </motion.div>

                    {/* ═══ SECTION 5: Navigation & AI Chat ═══ */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                        className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-12"
                    >
                        {/* Go Back */}
                        <Link to="/videos">
                            <button className="flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-sm bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors">
                                <ArrowLeft className="w-4 h-4" /> Back to All Topics
                            </button>
                        </Link>

                        {/* Ask AI Tutor About This Topic */}
                        <Link to={`/chat?topic=${encodeURIComponent(topicTitle)}`}>
                            <button className="flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-sm bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border border-emerald-200 transition-colors">
                                <Bot className="w-4 h-4" /> Ask AI Tutor About This Topic
                            </button>
                        </Link>
                    </motion.div>
                    </motion.div>

                </div>
            </PageWrapper>
        </>
    );
};
