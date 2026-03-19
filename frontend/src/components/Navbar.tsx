import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAntiCheat } from '../context/AntiCheatContext';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navbar() {
    const { user, logout } = useAuth();
    const { isTestActive } = useAntiCheat();
    const navigate = useNavigate();
    const location = useLocation();
    const [menuOpen, setMenuOpen] = useState(false);

    const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, path: string) => {
        if (isTestActive) {
            e.preventDefault();
            e.stopPropagation();
            alert('❌ Cannot navigate during mock test. Please complete or quit the test first.');
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    const navLinks = [
        { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
        { to: '/dashboard', label: 'Topics', icon: '📚', hash: '#topics' },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <>
            {/* Test banner - shows when test is active */}
            {isTestActive && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="bg-gradient-to-r from-danger/15 to-warning/15 border-b border-danger/30 px-4 py-3"
                >
                    <div className="max-w-7xl mx-auto flex items-center gap-3 text-sm font-semibold">
                        <span className="text-lg">🚨</span>
                        <span className="text-danger">Mock Test in Progress - Navigation is Disabled</span>
                        <span className="text-lg animate-pulse">⏱️</span>
                    </div>
                </motion.div>
            )}
            <nav className="sticky top-0 z-50 bg-white/60 backdrop-blur-xl border-b border-white/20 shadow-[0_4px_30px_rgba(0,0,0,0.03)]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 sm:h-20">
                        {/* Logo */}
                        <Link 
                            to="/dashboard" 
                            className="flex items-center gap-2.5 group"
                            onClick={(e) => !isTestActive && handleNavClick(e, '/dashboard')}
                        >
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20 group-hover:scale-105 transition-transform duration-300">
                                <span className="text-white font-bold text-sm font-display tracking-wider">ET</span>
                            </div>
                            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-display tracking-tight">
                                EduTwin
                            </span>
                        </Link>
                        {/* Desktop Nav */}
                        <div className={`hidden md:flex items-center gap-2 ${isTestActive ? 'opacity-50 pointer-events-none' : ''}`}>
                            {navLinks.map(link => (
                                <Link
                                    key={link.label}
                                    to={link.to}
                                    onClick={(e) => handleNavClick(e, link.to)}
                                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300
                      ${isTestActive ? 'cursor-not-allowed opacity-50' : ''}
                      ${isActive(link.to) && !isTestActive
                                            ? 'bg-primary/10 text-primary shadow-inner shadow-white/50'
                                            : 'text-text-secondary hover:bg-slate-100/80 hover:text-text'}`}
                                >
                                    <span className="mr-2 text-lg align-middle">{link.icon}</span>
                                    {link.label}
                                </Link>
                            ))}
                        </div>

                        {/* User section */}
                        {user && (
                            <div className="hidden md:flex items-center gap-4">
                                <div className="flex items-center gap-3 px-1.5 py-1.5 rounded-full bg-slate-100/50 border border-slate-200/50 pr-4">
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-sm font-bold shadow-md shadow-primary/20">
                                        {user.name.charAt(0)}
                                    </div>
                                    <span className="text-sm font-semibold text-text">{user.name}</span>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className={`px-4 py-2 rounded-xl text-sm font-semibold text-slate-500 hover:text-danger hover:bg-danger/10 transition-all duration-300 cursor-pointer ${isTestActive ? 'opacity-50 pointer-events-none' : ''}`}
                                    disabled={isTestActive}
                                >
                                    Logout
                                </button>
                            </div>
                        )}
                        {/* Mobile menu button */}
                        <button
                            onClick={() => !isTestActive && setMenuOpen(!menuOpen)}
                            className="md:hidden p-2 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                            disabled={isTestActive}
                        >
                            <div className="w-5 h-5 flex flex-col justify-center gap-1">
                                <span className={`block h-0.5 w-5 bg-text transition-all duration-300 ${menuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
                                <span className={`block h-0.5 w-5 bg-text transition-all duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
                                <span className={`block h-0.5 w-5 bg-text transition-all duration-300 ${menuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
                            </div>
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                <AnimatePresence>
                    {menuOpen && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="md:hidden border-t border-slate-200 overflow-hidden bg-white"
                        >
                            <div className="px-4 py-3 space-y-1">
                                {navLinks.map(link => (
                                    <Link
                                        key={link.label}
                                        to={link.to}
                                        onClick={(e) => {
                                            handleNavClick(e, link.to);
                                            !isTestActive && setMenuOpen(false);
                                        }}
                                        className={`block px-4 py-2.5 rounded-xl text-sm font-medium ${
                                            isTestActive ? 'opacity-50 pointer-events-none text-slate-400' : 'text-text-secondary hover:bg-slate-100'
                                        }`}
                                    >
                                        <span className="mr-2">{link.icon}</span>
                                        {link.label}
                                    </Link>
                                ))}
                                {user && (
                                    <>
                                        <div className="flex items-center gap-2 px-4 py-2.5">
                                            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-xs font-bold">
                                                {user.name.charAt(0)}
                                            </div>
                                            <span className="text-sm font-medium">{user.name}</span>
                                        </div>
                                        <button
                                            onClick={handleLogout}
                                            disabled={isTestActive}
                                            className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer ${
                                                isTestActive 
                                                    ? 'opacity-50 text-slate-400 pointer-events-none' 
                                                    : 'text-danger hover:bg-danger/10'
                                            }`}
                                        >
                                            Logout
                                        </button>
                                    </>
                                )}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </nav>
        </>
    );
}
