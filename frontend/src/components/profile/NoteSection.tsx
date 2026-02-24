import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    StickyNote, Plus, Trash2, Pin, Highlighter,
    AlertTriangle, Star, Bookmark, Search, X
} from 'lucide-react';
import { GlassCard } from '../ui/GlassCard';

export type NoteImportance = 'critical' | 'high' | 'medium' | 'low';

export interface Note {
    id: string;
    title: string;
    content: string;
    importance: NoteImportance;
    topic: string;
    pinned: boolean;
    highlighted: boolean;
    createdAt: string;
    color: string;
}

const IMPORTANCE_CONFIG: Record<NoteImportance, { label: string; color: string; bg: string; border: string; icon: React.ReactNode }> = {
    critical: {
        label: 'Critical',
        color: 'text-red-700',
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: <AlertTriangle className="w-3.5 h-3.5" />,
    },
    high: {
        label: 'High',
        color: 'text-orange-700',
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        icon: <Star className="w-3.5 h-3.5" />,
    },
    medium: {
        label: 'Medium',
        color: 'text-blue-700',
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: <Bookmark className="w-3.5 h-3.5" />,
    },
    low: {
        label: 'Low',
        color: 'text-gray-600',
        bg: 'bg-gray-50',
        border: 'border-gray-200',
        icon: <StickyNote className="w-3.5 h-3.5" />,
    },
};

const HIGHLIGHT_COLORS = [
    { name: 'Yellow', value: '#fef08a', class: 'bg-yellow-200' },
    { name: 'Pink', value: '#fbb6ce', class: 'bg-pink-200' },
    { name: 'Green', value: '#a7f3d0', class: 'bg-emerald-200' },
    { name: 'Blue', value: '#bae6fd', class: 'bg-sky-200' },
    { name: 'Purple', value: '#ddd6fe', class: 'bg-violet-200' },
    { name: 'Orange', value: '#fcd5b5', class: 'bg-orange-200' },
];

const INITIAL_NOTES: Note[] = [
    {
        id: '1',
        title: 'Python Decorators Pattern',
        content: 'Decorators wrap a function, modifying its behavior. Use @decorator syntax above function definition. Key for understanding Flask routes and Django views.',
        importance: 'critical',
        topic: 'Python Functions & Scope',
        pinned: true,
        highlighted: true,
        createdAt: '2026-02-20',
        color: '#fef08a',
    },
    {
        id: '2',
        title: 'Big O Notation Summary',
        content: 'O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ). Always analyze worst-case. Space complexity matters too!',
        importance: 'high',
        topic: 'Data Structures Overview',
        pinned: true,
        highlighted: false,
        createdAt: '2026-02-18',
        color: '#fbb6ce',
    },
    {
        id: '3',
        title: 'SQL JOIN Types',
        content: 'INNER JOIN = matching rows. LEFT JOIN = all left + matching right. RIGHT JOIN = all right + matching left. FULL OUTER = all rows from both.',
        importance: 'medium',
        topic: 'SQL Fundamentals',
        pinned: false,
        highlighted: true,
        createdAt: '2026-02-15',
        color: '#a7f3d0',
    },
    {
        id: '4',
        title: 'Pointer Arithmetic in C',
        content: 'ptr++ moves to next element (not next byte). Array name is a pointer to first element. Use & for address, * for dereference.',
        importance: 'high',
        topic: 'C Pointers Introduction',
        pinned: false,
        highlighted: false,
        createdAt: '2026-02-12',
        color: '#bae6fd',
    },
];

interface NoteSectionProps {
    notes: Note[];
    onNotesChange: (notes: Note[]) => void;
}

export const NoteSection = ({ notes, onNotesChange }: NoteSectionProps) => {
    const [showAddNote, setShowAddNote] = useState(false);
    const [filterImportance, setFilterImportance] = useState<NoteImportance | 'all'>('all');
    const [searchQuery, setSearchQuery] = useState('');
    const [showHighlightedOnly, setShowHighlightedOnly] = useState(false);
    const [newNote, setNewNote] = useState({
        title: '',
        content: '',
        importance: 'medium' as NoteImportance,
        topic: '',
        color: '#fef08a',
    });

    const addNote = () => {
        if (!newNote.title.trim() || !newNote.content.trim()) return;
        const note: Note = {
            id: Date.now().toString(),
            ...newNote,
            pinned: false,
            highlighted: false,
            createdAt: new Date().toISOString().split('T')[0],
        };
        onNotesChange([note, ...notes]);
        setNewNote({ title: '', content: '', importance: 'medium', topic: '', color: '#fef08a' });
        setShowAddNote(false);
    };

    const togglePin = (id: string) => {
        onNotesChange(notes.map(n => n.id === id ? { ...n, pinned: !n.pinned } : n));
    };

    const toggleHighlight = (id: string) => {
        onNotesChange(notes.map(n => n.id === id ? { ...n, highlighted: !n.highlighted } : n));
    };

    const deleteNote = (id: string) => {
        onNotesChange(notes.filter(n => n.id !== id));
    };

    const changeNoteColor = (id: string, color: string) => {
        onNotesChange(notes.map(n => n.id === id ? { ...n, color } : n));
    };

    const filteredNotes = notes
        .filter(n => {
            const matchesImportance = filterImportance === 'all' || n.importance === filterImportance;
            const matchesSearch = n.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                n.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                n.topic.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesHighlight = !showHighlightedOnly || n.highlighted;
            return matchesImportance && matchesSearch && matchesHighlight;
        })
        .sort((a, b) => {
            if (a.pinned && !b.pinned) return -1;
            if (!a.pinned && b.pinned) return 1;
            const order: Record<NoteImportance, number> = { critical: 0, high: 1, medium: 2, low: 3 };
            return order[a.importance] - order[b.importance];
        });

    return (
        <GlassCard className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center">
                        <StickyNote className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-800">Study Notes</h3>
                        <p className="text-xs text-gray-500">{notes.length} notes · {notes.filter(n => n.highlighted).length} highlighted</p>
                    </div>
                </div>
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowAddNote(!showAddNote)}
                    className="flex items-center gap-1.5 px-3 py-2 bg-brand text-white rounded-xl text-sm font-medium shadow-sm hover:shadow-md transition-shadow"
                >
                    {showAddNote ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                    {showAddNote ? 'Cancel' : 'Add Note'}
                </motion.button>
            </div>

            {/* Add Note Form */}
            <AnimatePresence>
                {showAddNote && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden mb-5"
                    >
                        <div className="p-4 bg-pink-50/50 rounded-xl border border-pink-100 space-y-3">
                            <input
                                type="text"
                                placeholder="Note title..."
                                value={newNote.title}
                                onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
                                className="w-full bg-white border border-pink-100 rounded-lg px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30"
                            />
                            <textarea
                                placeholder="Write your note..."
                                value={newNote.content}
                                onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
                                rows={3}
                                className="w-full bg-white border border-pink-100 rounded-lg px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30 resize-none"
                            />
                            <div className="flex flex-wrap gap-3 items-center">
                                <input
                                    type="text"
                                    placeholder="Related topic..."
                                    value={newNote.topic}
                                    onChange={(e) => setNewNote({ ...newNote, topic: e.target.value })}
                                    className="flex-1 min-w-[140px] bg-white border border-pink-100 rounded-lg px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                />
                                <select
                                    value={newNote.importance}
                                    onChange={(e) => setNewNote({ ...newNote, importance: e.target.value as NoteImportance })}
                                    className="bg-white border border-pink-100 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand/30"
                                >
                                    <option value="critical">🔴 Critical</option>
                                    <option value="high">🟠 High</option>
                                    <option value="medium">🔵 Medium</option>
                                    <option value="low">⚪ Low</option>
                                </select>
                                {/* Color picker */}
                                <div className="flex gap-1.5">
                                    {HIGHLIGHT_COLORS.map(c => (
                                        <button
                                            key={c.value}
                                            onClick={() => setNewNote({ ...newNote, color: c.value })}
                                            className={`w-6 h-6 rounded-full border-2 transition-all ${c.class} ${
                                                newNote.color === c.value ? 'border-gray-600 scale-110' : 'border-transparent hover:border-gray-300'
                                            }`}
                                            title={c.name}
                                        />
                                    ))}
                                </div>
                            </div>
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={addNote}
                                disabled={!newNote.title.trim() || !newNote.content.trim()}
                                className="w-full py-2.5 bg-gradient-brand text-white rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Save Note
                            </motion.button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Filters */}
            <div className="flex flex-wrap gap-2 mb-4">
                <div className="relative flex-1 min-w-[180px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search notes..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-pink-50/30 border border-pink-100 rounded-lg py-2 pl-8 pr-3 text-xs text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand/30"
                    />
                </div>
                <div className="flex gap-1.5 items-center">
                    {(['all', 'critical', 'high', 'medium', 'low'] as const).map(imp => (
                        <button
                            key={imp}
                            onClick={() => setFilterImportance(imp)}
                            className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                                filterImportance === imp
                                    ? imp === 'all' ? 'bg-gray-800 text-white' : `${IMPORTANCE_CONFIG[imp].bg} ${IMPORTANCE_CONFIG[imp].color} ${IMPORTANCE_CONFIG[imp].border} border`
                                    : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                            }`}
                        >
                            {imp === 'all' ? 'All' : IMPORTANCE_CONFIG[imp].label}
                        </button>
                    ))}
                    <button
                        onClick={() => setShowHighlightedOnly(!showHighlightedOnly)}
                        className={`p-1.5 rounded-lg transition-all ${
                            showHighlightedOnly ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-50 text-gray-400 hover:bg-gray-100'
                        }`}
                        title="Show highlighted only"
                    >
                        <Highlighter className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Notes Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <AnimatePresence mode="popLayout">
                    {filteredNotes.map((note) => {
                        const config = IMPORTANCE_CONFIG[note.importance];
                        return (
                            <motion.div
                                key={note.id}
                                layout
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className={`relative rounded-xl border overflow-hidden transition-all ${
                                    note.highlighted ? 'ring-2 ring-yellow-300/50' : ''
                                }`}
                                style={{
                                    borderColor: note.color + '80',
                                    backgroundColor: note.color + '15',
                                }}
                            >
                                {/* Highlight strip */}
                                {note.highlighted && (
                                    <div className="h-1 w-full" style={{ backgroundColor: note.color }} />
                                )}

                                <div className="p-4">
                                    <div className="flex items-start justify-between gap-2 mb-2">
                                        <div className="flex items-center gap-2 flex-1 min-w-0">
                                            {note.pinned && <Pin className="w-3.5 h-3.5 text-brand flex-shrink-0 rotate-45" />}
                                            <h4 className="font-semibold text-gray-800 text-sm truncate">{note.title}</h4>
                                        </div>
                                        <span className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${config.bg} ${config.color} flex-shrink-0`}>
                                            {config.icon}
                                            {config.label}
                                        </span>
                                    </div>

                                    <p className="text-xs text-gray-600 leading-relaxed mb-3 line-clamp-3">{note.content}</p>

                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">{note.topic}</span>
                                            <span className="text-[10px] text-gray-400">{note.createdAt}</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {/* Color change dots */}
                                            <div className="flex gap-0.5 mr-1">
                                                {HIGHLIGHT_COLORS.slice(0, 4).map(c => (
                                                    <button
                                                        key={c.value}
                                                        onClick={() => changeNoteColor(note.id, c.value)}
                                                        className={`w-3 h-3 rounded-full ${c.class} border border-white/50 hover:scale-125 transition-transform`}
                                                    />
                                                ))}
                                            </div>
                                            <button
                                                onClick={() => togglePin(note.id)}
                                                className={`p-1 rounded-md transition-colors ${note.pinned ? 'text-brand bg-brand/10' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
                                                title="Pin note"
                                            >
                                                <Pin className="w-3.5 h-3.5" />
                                            </button>
                                            <button
                                                onClick={() => toggleHighlight(note.id)}
                                                className={`p-1 rounded-md transition-colors ${note.highlighted ? 'text-yellow-600 bg-yellow-100' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'}`}
                                                title="Highlight note"
                                            >
                                                <Highlighter className="w-3.5 h-3.5" />
                                            </button>
                                            <button
                                                onClick={() => deleteNote(note.id)}
                                                className="p-1 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                                                title="Delete note"
                                            >
                                                <Trash2 className="w-3.5 h-3.5" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </AnimatePresence>
            </div>

            {filteredNotes.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                    <StickyNote className="w-10 h-10 mx-auto mb-2 opacity-30" />
                    <p className="text-sm">No notes found</p>
                </div>
            )}
        </GlassCard>
    );
};

export { INITIAL_NOTES };
