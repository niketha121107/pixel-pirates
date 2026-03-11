import { useState } from 'react';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { NoteSection } from '../components/profile/NoteSection';
import type { Note } from '../components/profile/NoteSection';
import { StickyNote } from 'lucide-react';

export const Notes = () => {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [notes, setNotes] = useState<Note[]>(() => {
        const stored = localStorage.getItem('edutwin-notes');
        return stored ? JSON.parse(stored) : [];
    });

    const handleNotesChange = (updatedNotes: Note[]) => {
        setNotes(updatedNotes);
        localStorage.setItem('edutwin-notes', JSON.stringify(updatedNotes));
    };

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
            <PageWrapper className="lg:pl-64" withPadding={false}>
                <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 w-full max-w-6xl mx-auto space-y-6">
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <StickyNote className="w-8 h-8 text-brand" />
                            My Notes
                        </h1>
                        <p className="text-gray-500 mt-1">Organize your study notes, highlights, and important points</p>
                    </motion.div>

                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                        <NoteSection notes={notes} onNotesChange={handleNotesChange} />
                    </motion.div>
                </div>
            </PageWrapper>
        </>
    );
};
