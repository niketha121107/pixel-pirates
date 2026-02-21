import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from './Navbar';

export default function Layout() {
    return (
        <div className="min-h-screen bg-surface relative overflow-hidden">
            {/* Animated Mesh Background */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[100px] animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent/20 blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
                <div className="absolute top-[40%] left-[30%] w-[30%] h-[30%] rounded-full bg-fuchsia-500/10 blur-[90px] animate-pulse" style={{ animationDelay: '4s' }} />
            </div>

            <div className="relative z-10 flex flex-col min-h-screen">
                <Navbar />
                <motion.main
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8"
                >
                    <Outlet />
                </motion.main>
            </div>
        </div>
    );
}
