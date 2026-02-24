import { useState } from 'react';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { VideoTrackerUI } from '../components/learning/VideoTrackerUI';
import { ConfidenceSlider } from '../components/learning/ConfidenceSlider';
import { GradientButton } from '../components/ui/GradientButton';
import { GlassCard } from '../components/ui/GlassCard';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, FileText, StickyNote, CheckCircle2, Eye, Lightbulb, Workflow, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUnderstanding } from '../context/UnderstandingContext';
import { useNotifications } from '../context/NotificationContext';

// ─── 4 Explanation Types — The Core Feature ──────────────────────────
type ExplanationType = 'simplified' | 'logical' | 'visual' | 'analogy';

interface ExplanationContent {
    title: string;
    body: string[];
    highlight: string;
    codeExample?: string;
}

const explanationData: Record<ExplanationType, ExplanationContent> = {
    simplified: {
        title: '🟢 Simplified Explanation',
        highlight: 'In plain, everyday language — no jargon.',
        body: [
            'A **generator** is like a special function that can pause and resume.',
            'Instead of computing everything at once and returning a big list, it gives you **one item at a time** whenever you ask for the next one.',
            'You create one using the **yield** keyword instead of return.',
            'Think of it as a **lazy worker** — it only does the next bit of work when you tell it to.',
            'This saves memory because you don\'t have to hold everything in memory at once.',
        ],
        codeExample: `# Simple generator\ndef count_up(n):\n    i = 1\n    while i <= n:\n        yield i    # pauses here, gives you i\n        i += 1\n\n# Use it:\nfor num in count_up(5):\n    print(num)  # prints 1, 2, 3, 4, 5`,
    },
    logical: {
        title: '🔵 Logical / Step-by-Step Explanation',
        highlight: 'A precise, structured walkthrough of how it works internally.',
        body: [
            '**Step 1:** When Python sees `yield` in a function, it marks that function as a generator function.',
            '**Step 2:** Calling the function does NOT execute the body. Instead, it returns a **generator object** (an iterator).',
            '**Step 3:** Each call to `next()` on the generator executes the function body up to the next `yield` statement.',
            '**Step 4:** The `yield` expression returns the value AND **suspends** the function\'s state (local variables, instruction pointer).',
            '**Step 5:** On the next `next()` call, execution **resumes** right after the `yield`, with all local state intact.',
            '**Step 6:** When the function body ends (or hits `return`), a `StopIteration` exception is raised, signaling exhaustion.',
        ],
        codeExample: `def gen():\n    print("A")\n    yield 1\n    print("B")\n    yield 2\n    print("C")\n\ng = gen()         # Nothing printed yet\nprint(next(g))    # Prints "A", returns 1\nprint(next(g))    # Prints "B", returns 2\nprint(next(g))    # Prints "C", raises StopIteration`,
    },
    visual: {
        title: '🟣 Visual / Diagram Explanation',
        highlight: 'See how data flows through the generator, step by step.',
        body: [
            '**Execution Flow Diagram:**',
            '',
            '┌─── call gen() ───────────────────────────┐',
            '│  Creates generator object (no execution)  │',
            '└────────────────────────────────────────────┘',
            '         │',
            '         ▼  next()',
            '┌────────────────────────────┐',
            '│  Execute until yield 1     │ ──→ returns 1',
            '│  ⏸️  PAUSED (state saved)   │',
            '└────────────────────────────┘',
            '         │',
            '         ▼  next()',
            '┌────────────────────────────┐',
            '│  Resume → execute → yield 2│ ──→ returns 2',
            '│  ⏸️  PAUSED (state saved)   │',
            '└────────────────────────────┘',
            '         │',
            '         ▼  next()',
            '┌────────────────────────────┐',
            '│  Resume → function ends    │ ──→ StopIteration',
            '│  ❌  EXHAUSTED             │',
            '└────────────────────────────┘',
            '',
            '**Memory comparison:**',
            '  List:      [██████████████████████] All in RAM',
            '  Generator: [██]→[██]→[██]→...      One at a time',
        ],
    },
    analogy: {
        title: '🟡 Analogy-Based Explanation',
        highlight: 'Understand through real-world comparisons.',
        body: [
            '**🏭 The Factory Analogy:**',
            'Imagine a factory with a conveyor belt. A **regular function** is like a factory that builds ALL the products, boxes them up, and delivers the entire shipment at once. You need a huge warehouse to store everything.',
            '',
            'A **generator** is like a factory with a **just-in-time** conveyor belt. It builds ONE product at a time and hands it to you directly. No warehouse needed!',
            '',
            '**📖 The Bookmark Analogy:**',
            'Reading a book with `return` is like reading the entire book, writing a summary, and handing it over. Reading with `yield` is like using a **bookmark** — you read one chapter, place the bookmark, and come back later to continue exactly where you left off.',
            '',
            '**🎰 The Vending Machine Analogy:**',
            'A generator is like a vending machine. It has many items inside, but it gives you **one item per button press**. It remembers which slot is next. You don\'t get all the snacks dumped on you at once!',
            '',
            '**Key takeaway:** Generators = lazy, on-demand, memory-efficient sequences.',
        ],
    },
};

const explanationMeta: { id: ExplanationType; label: string; icon: typeof Eye; color: string; bg: string; border: string; desc: string }[] = [
    { id: 'simplified', label: 'Simplified', icon: BookOpen, color: 'text-emerald-600', bg: 'bg-candy-mint/40', border: 'border-emerald-200', desc: 'Plain language, no jargon' },
    { id: 'logical', label: 'Logical', icon: Workflow, color: 'text-pink-600', bg: 'bg-candy-pink/40', border: 'border-pink-200', desc: 'Step-by-step breakdown' },
    { id: 'visual', label: 'Visual', icon: Eye, color: 'text-purple-600', bg: 'bg-candy-lavender/40', border: 'border-purple-200', desc: 'Diagrams & flow charts' },
    { id: 'analogy', label: 'Analogy', icon: Lightbulb, color: 'text-orange-600', bg: 'bg-candy-peach/40', border: 'border-orange-200', desc: 'Real-world comparisons' },
];

export const TopicView = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [videoProgress, setVideoProgress] = useState(0);
    const [videoEnded, setVideoEnded] = useState(false);
    const [isCompleted, setIsCompleted] = useState(false);
    const [activeTab, setActiveTab] = useState<'pdf' | 'notes'>('pdf');
    const [selectedExplanation, setSelectedExplanation] = useState<ExplanationType>('simplified');
    const [confidence, setConfidence] = useState(40);
    const { saveUnderstanding } = useUnderstanding();
    const { addNotification } = useNotifications();

    const TOPIC_ID = 6; // Current topic = "Advanced Iterators & Generators"
    const TOPIC_TITLE = 'Advanced Iterators & Generators';

    const handleSaveUnderstanding = (value: number, label: string) => {
        saveUnderstanding({ topicId: TOPIC_ID, topicTitle: TOPIC_TITLE, value, label });
    };

    const handleComplete = () => {
        if (hasWatchedFull) {
            setIsCompleted(true);
            addNotification({
                type: 'congrats',
                title: 'Congratulations! Topic completed 🎉',
                message: `Great job finishing "${TOPIC_TITLE}"! Keep up the awesome work.`,
                topicId: TOPIC_ID,
            });
        }
    };

    const hasWatchedFull = videoProgress >= 95 || videoEnded;
    const currentExplanation = explanationData[selectedExplanation];
    const currentMeta = explanationMeta.find(m => m.id === selectedExplanation)!;

    const sampleNotes = `## Python Generators & Iterators

**Key Concepts:**
• A generator function uses the \`yield\` keyword instead of \`return\`
• Generators produce items lazily — one at a time, on demand
• They maintain internal state between calls to \`next()\`

**Example:**
\`\`\`python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for num in countdown(5):
    print(num)
\`\`\`

**Benefits:**
- Memory efficient for large datasets
- Can represent infinite sequences
- Composable with other itertools

**When to use:**
Use generators when processing large files, streaming data, or building data pipelines.`;

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            <PageWrapper className="lg:pl-64">
                <div className="max-w-5xl mx-auto space-y-8">

                    {/* Header */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand/10 border border-brand/20 rounded-full text-brand text-xs font-bold mb-4">
                            <BookOpen className="w-3.5 h-3.5" /> Python Basics
                        </div>
                        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-2">Advanced Iterators & Generators</h1>
                        <p className="text-lg text-gray-500">Master memory-efficient looping structures using Python generators and the yield keyword.</p>
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
                                            <h3 className="font-bold text-gray-800 text-base">{currentExplanation.title}</h3>
                                            <p className="text-xs text-gray-500">{currentExplanation.highlight}</p>
                                        </div>
                                        <div className="ml-auto">
                                            <Sparkles className={`w-4 h-4 ${currentMeta.color} opacity-60`} />
                                        </div>
                                    </div>

                                    {/* Body */}
                                    <div className="p-6 space-y-3">
                                        {currentExplanation.body.map((line, i) => {
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
                                    </div>
                                </GlassCard>
                            </motion.div>
                        </AnimatePresence>

                        {/* Confidence Slider */}
                        <ConfidenceSlider
                            value={confidence}
                            onChange={setConfidence}
                            topicId={TOPIC_ID}
                            topicTitle={TOPIC_TITLE}
                            onSave={handleSaveUnderstanding}
                        />
                    </motion.div>

                    {/* ═══ SECTION 2: Watch the Video ═══ */}
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-3">
                        <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                            <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">2</span>
                            Watch the Video
                        </h2>
                        <VideoTrackerUI
                            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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
                    </motion.div>

                    {/* ═══ SECTION 3: Study Materials (PDF + Notes) ═══ */}
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
                                    <span className="text-sm font-semibold text-gray-700">Learning PDF</span>
                                    <span className="ml-auto text-xs text-gray-400">View only</span>
                                </div>
                                <iframe
                                    src="https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf#toolbar=0&navpanes=0&scrollbar=1"
                                    className="w-full h-[500px] border-0"
                                    title="Learning PDF"
                                />
                            </GlassCard>

                            {/* Notes Viewer */}
                            <GlassCard className={`p-0 overflow-hidden ${activeTab !== 'notes' ? 'hidden lg:block' : ''}`}>
                                <div className="bg-gray-100 px-4 py-3 border-b border-gray-200 flex items-center gap-2">
                                    <StickyNote className="w-4 h-4 text-brand" />
                                    <span className="text-sm font-semibold text-gray-700">Topic Notes</span>
                                    <span className="ml-auto text-xs text-gray-400">View only</span>
                                </div>
                                <div className="p-6 h-[500px] overflow-y-auto">
                                    <div className="prose prose-sm max-w-none text-gray-700">
                                        {sampleNotes.split('\n').map((line, i) => {
                                            if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold text-gray-800 mb-3">{line.replace('## ', '')}</h2>;
                                            if (line.startsWith('**') && line.endsWith('**')) return <p key={i} className="font-bold text-gray-800 mt-4 mb-2">{line.replace(/\*\*/g, '')}</p>;
                                            if (line.startsWith('• ') || line.startsWith('- ')) return <p key={i} className="pl-4 py-0.5 text-gray-600">{line}</p>;
                                            if (line.startsWith('```')) return <div key={i} className="my-1" />;
                                            if (line.trim() === '') return <br key={i} />;
                                            return <p key={i} className="text-gray-600 leading-relaxed">{line}</p>;
                                        })}
                                    </div>
                                </div>
                            </GlassCard>
                        </div>
                    </motion.div>

                    {/* ═══ SECTION 4: Complete & Take Test ═══ */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 pb-12 border-t border-pink-100"
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

                        {/* Take Mock Test */}
                        <Link to="/quiz">
                            <GradientButton className="group text-lg px-8 py-4">
                                Take Mock Test
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </GradientButton>
                        </Link>
                    </motion.div>

                </div>
            </PageWrapper>
        </>
    );
};
