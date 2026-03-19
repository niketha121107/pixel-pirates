import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { topicsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, BookOpen, Loader2, Code2, CheckCircle2, XCircle, AlertTriangle, Lightbulb } from 'lucide-react';
import { sanitizeMojibakePreserveLines, sanitizeMojibakeText } from '../lib/text';
import type { NoteImportance } from '../components/profile/NoteSection';

interface StudyMaterialData {
    title?: string;
    overview?: string;
    syntax?: string;
    codeExample?: string;
    explanation?: string;
    implementation?: string[];
    advantages?: string[];
    disadvantages?: string[];
    keyPoints?: string[];
    commonMistakes?: string[];
}

export const StudyMaterial = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const topicId = searchParams.get('topicId') || '';

    const [loading, setLoading] = useState(true);
    const [topicName, setTopicName] = useState('');
    const [language, setLanguage] = useState('');
    const [material, setMaterial] = useState<StudyMaterialData | null>(null);
    const [selectedSnippet, setSelectedSnippet] = useState('');
    const [noteImportance, setNoteImportance] = useState<NoteImportance>('medium');
    const [selectionAnchor, setSelectionAnchor] = useState<{ x: number; y: number } | null>(null);

    useEffect(() => {
        if (!topicId) { setLoading(false); return; }
        topicsAPI.getById(topicId)
            .then(res => {
                const topic = res.data?.data?.topic;
                if (topic) {
                    setTopicName(topic.topicName || '');
                    setLanguage(topic.language || '');
                    if (topic.studyMaterial && Object.keys(topic.studyMaterial).length > 0) {
                        setMaterial(topic.studyMaterial);
                    }
                }
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [topicId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-brand animate-spin" />
            </div>
        );
    }

    if (!material) {
        return (
            <div className="min-h-screen bg-gray-100 flex flex-col">
                <div className="bg-white border-b px-4 py-3 flex items-center gap-3 shadow-sm">
                    <button onClick={() => navigate(-1)} className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200">
                        <ArrowLeft className="w-4 h-4" /> Back
                    </button>
                </div>
                <div className="flex-1 flex items-center justify-center text-gray-400">
                    <p>Study material not available for this topic yet.</p>
                </div>
            </div>
        );
    }

    const handleTextSelection = (e: React.MouseEvent) => {
        const selected = window.getSelection()?.toString().trim() || '';
        if (selected.length < 8) {
            setSelectedSnippet('');
            setSelectionAnchor(null);
            return;
        }
        setSelectedSnippet(sanitizeMojibakeText(selected));
        setSelectionAnchor({ x: e.clientX, y: e.clientY });
    };

    const saveSelectionAsNote = () => {
        if (!selectedSnippet) return;
        // Use user-specific key to isolate notes per user
        const userKey = `edutwin-notes_${user?.id || 'guest'}`;
        const stored = localStorage.getItem(userKey);
        const notes = stored ? JSON.parse(stored) : [];
        notes.unshift({
            id: Date.now().toString(),
            title: `${topicName} highlight`,
            content: selectedSnippet,
            importance: noteImportance,
            topic: topicName,
            pinned: false,
            highlighted: true,
            createdAt: new Date().toISOString().split('T')[0],
            color: '#fef08a',
        });
        localStorage.setItem(userKey, JSON.stringify(notes));
        setSelectedSnippet('');
        setSelectionAnchor(null);
        window.getSelection()?.removeAllRanges();
    };

    let sectionNum = 0;
    const nextSection = () => ++sectionNum;

    return (
        <div className="h-screen overflow-y-auto bg-gray-200">
            {/* Fixed Header */}
            <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 shadow-sm">
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <div className="flex items-center gap-2 flex-1 min-w-0">
                    <BookOpen className="w-5 h-5 text-brand flex-shrink-0" />
                    <h1 className="text-lg font-bold text-gray-800 truncate">{topicName}</h1>
                    {language && <span className="text-xs font-medium text-brand bg-brand/10 px-2 py-0.5 rounded-full flex-shrink-0">{language}</span>}
                </div>
            </div>

            {/* Document Content */}
            <div className="max-w-4xl mx-auto py-8 px-4" onMouseUp={handleTextSelection}>
                <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                    {/* Document Header */}
                    <div className="bg-gradient-to-r from-brand/90 to-pink-500 px-8 py-10 text-white">
                        <div className="flex items-center gap-2 text-white/70 text-sm mb-3">
                            <BookOpen className="w-4 h-4" />
                            <span>{language}</span>
                        </div>
                        <h1 className="text-3xl font-bold">{material.title || topicName}</h1>
                        <p className="text-white/80 mt-2 text-sm">Complete Study Material &bull; {language}</p>
                    </div>

                    <div className="px-8 py-8 space-y-8">
                        {/* Overview */}
                        {material.overview && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Overview
                                </h2>
                                <div className="bg-gray-50 rounded-xl p-5 border border-gray-100">
                                    <p className="text-gray-700 leading-relaxed text-[15px] whitespace-pre-line">{sanitizeMojibakePreserveLines(material.overview)}</p>
                                </div>
                            </section>
                        )}

                        {/* Explanation */}
                        {material.explanation && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Detailed Explanation
                                </h2>
                                <div className="rounded-xl p-5 border bg-emerald-50 border-emerald-200">
                                    <div className="space-y-2">
                                        {sanitizeMojibakePreserveLines(material.explanation).split('\n').filter(Boolean).map((line: string, i: number) => (
                                            <p key={i} className="text-gray-700 leading-relaxed text-[15px]">{line}</p>
                                        ))}
                                    </div>
                                </div>
                            </section>
                        )}

                        {/* Syntax */}
                        {material.syntax && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Syntax
                                </h2>
                                <div className="rounded-xl p-5 border bg-blue-50 border-blue-200">
                                    <pre className="bg-gray-900 text-green-300 rounded-xl p-4 text-sm font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                        {sanitizeMojibakePreserveLines(material.syntax)}
                                    </pre>
                                </div>
                            </section>
                        )}

                        {/* Code Example */}
                        {material.codeExample && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Code Example
                                </h2>
                                <div className="rounded-xl p-5 border bg-purple-50 border-purple-200">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Code2 className="w-4 h-4 text-gray-500" />
                                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Runnable Example</span>
                                    </div>
                                    <pre className="bg-gray-900 text-green-300 rounded-xl p-4 text-sm font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                                        {sanitizeMojibakePreserveLines(material.codeExample)}
                                    </pre>
                                </div>
                            </section>
                        )}

                        {/* Where Implemented */}
                        {material.implementation && material.implementation.length > 0 && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Where This Is Used
                                </h2>
                                <div className="rounded-xl p-5 border bg-amber-50 border-amber-200">
                                    <ul className="space-y-2">
                                        {material.implementation.map((item, idx) => (
                                            <li key={idx} className="text-gray-700 leading-relaxed text-[15px] flex gap-2">
                                                <span className="text-brand">•</span>{sanitizeMojibakeText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}

                        {/* Key Points */}
                        {material.keyPoints && material.keyPoints.length > 0 && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Key Takeaways
                                </h2>
                                <div className="rounded-xl p-5 border bg-indigo-50 border-indigo-200">
                                    <ul className="space-y-2">
                                        {material.keyPoints.map((item, idx) => (
                                            <li key={idx} className="text-gray-700 leading-relaxed text-[15px] flex gap-2">
                                                <Lightbulb className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
                                                {sanitizeMojibakeText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}

                        {/* Advantages */}
                        {material.advantages && material.advantages.length > 0 && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Advantages
                                </h2>
                                <div className="rounded-xl p-5 border bg-emerald-50 border-emerald-200">
                                    <ul className="space-y-2">
                                        {material.advantages.map((item, idx) => (
                                            <li key={idx} className="text-gray-700 leading-relaxed text-[15px] flex gap-2">
                                                <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                                                {sanitizeMojibakeText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}

                        {/* Disadvantages */}
                        {material.disadvantages && material.disadvantages.length > 0 && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Disadvantages
                                </h2>
                                <div className="rounded-xl p-5 border bg-rose-50 border-rose-200">
                                    <ul className="space-y-2">
                                        {material.disadvantages.map((item, idx) => (
                                            <li key={idx} className="text-gray-700 leading-relaxed text-[15px] flex gap-2">
                                                <XCircle className="w-4 h-4 text-rose-500 mt-0.5 flex-shrink-0" />
                                                {sanitizeMojibakeText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}

                        {/* Common Mistakes */}
                        {material.commonMistakes && material.commonMistakes.length > 0 && (
                            <section>
                                <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <span className="w-8 h-8 bg-brand/10 rounded-lg flex items-center justify-center text-brand text-sm font-bold">{nextSection()}</span>
                                    Common Mistakes to Avoid
                                </h2>
                                <div className="rounded-xl p-5 border bg-orange-50 border-orange-200">
                                    <ul className="space-y-2">
                                        {material.commonMistakes.map((item, idx) => (
                                            <li key={idx} className="text-gray-700 leading-relaxed text-[15px] flex gap-2">
                                                <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                                                {sanitizeMojibakeText(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </section>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="border-t border-gray-100 px-8 py-4 bg-gray-50 flex items-center justify-between">
                        <span className="text-xs text-gray-400">EduTwin &bull; {topicName}</span>
                        <span className="text-xs text-gray-400">{language}</span>
                    </div>
                </div>
            </div>

            {selectionAnchor && selectedSnippet && (
                <div
                    className="fixed z-50 bg-white border border-gray-200 rounded-xl shadow-xl p-3 w-64"
                    style={{ top: Math.min(selectionAnchor.y + 12, window.innerHeight - 180), left: Math.max(16, Math.min(selectionAnchor.x - 120, window.innerWidth - 280)) }}
                >
                    <p className="text-xs text-gray-500 mb-2">Save selected text to notes</p>
                    <p className="text-xs text-gray-700 bg-gray-50 rounded-lg p-2 line-clamp-3">{selectedSnippet}</p>
                    <div className="mt-2">
                        <label className="text-[11px] font-medium text-gray-600">Importance</label>
                        <select
                            value={noteImportance}
                            onChange={(e) => setNoteImportance(e.target.value as NoteImportance)}
                            className="mt-1 w-full text-xs border border-gray-200 rounded-lg px-2 py-1.5"
                        >
                            <option value="critical">Critical</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                    <div className="mt-3 flex gap-2 justify-end">
                        <button onClick={() => { setSelectionAnchor(null); setSelectedSnippet(''); }} className="text-xs px-2.5 py-1.5 rounded-lg bg-gray-100 text-gray-600">Cancel</button>
                        <button onClick={saveSelectionAsNote} className="text-xs px-2.5 py-1.5 rounded-lg bg-brand text-white">Add Note</button>
                    </div>
                </div>
            )}
        </div>
    );
};
