import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import { useAuth } from './AuthContext';

interface AntiCheatContextType {
    warnings: number;
    maxWarnings: number;
    isBlocked: boolean;
    blockUntil: string | null;
    addWarning: (reason: string) => void;
    isTestActive: boolean;
    setTestActive: (active: boolean) => void;
}

const AntiCheatContext = createContext<AntiCheatContextType | undefined>(undefined);

const MAX_WARNINGS = 10;

export function AntiCheatProvider({ children }: { children: ReactNode }) {
    const { logout } = useAuth();
    const [warnings, setWarnings] = useState(0);
    const [isBlocked, setIsBlocked] = useState(false);
    const [blockUntil, setBlockUntil] = useState<string | null>(null);
    const [showBlockedModal, setShowBlockedModal] = useState(true);
    const [isTestActive, setTestActive] = useState(false);
    const [warningMessage, setWarningMessage] = useState<string | null>(null);

    // Check if user is blocked on mount
    useEffect(() => {
        const storedBlock = localStorage.getItem('anticheat_block_until');
        const storedWarnings = localStorage.getItem('anticheat_warnings');
        if (storedBlock) {
            const blockDate = new Date(storedBlock);
            if (blockDate > new Date()) {
                setIsBlocked(true);
                setBlockUntil(storedBlock);
                setShowBlockedModal(true);
            } else {
                localStorage.removeItem('anticheat_block_until');
                localStorage.removeItem('anticheat_warnings');
            }
        }
        if (storedWarnings) {
            setWarnings(parseInt(storedWarnings, 10));
        }
    }, []);

    const addWarning = useCallback((reason: string) => {
        setWarnings(prev => {
            const newCount = prev + 1;
            localStorage.setItem('anticheat_warnings', String(newCount));

            if (newCount > MAX_WARNINGS) {
                // Block user until next day
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                tomorrow.setHours(0, 0, 0, 0);
                const blockStr = tomorrow.toISOString();
                localStorage.setItem('anticheat_block_until', blockStr);
                setIsBlocked(true);
                setBlockUntil(blockStr);
                setShowBlockedModal(true);
                alert(`⛔ You have exceeded ${MAX_WARNINGS} warnings for illegal actions (${reason}). You are logged out. Please reattempt tomorrow.`);
                logout();
                return newCount;
            }

            setWarningMessage(`⚠️ Warning ${newCount}/${MAX_WARNINGS}: ${reason}. ${MAX_WARNINGS - newCount} warnings remaining before account suspension.`);
            setTimeout(() => setWarningMessage(null), 5000);
            return newCount;
        });
    }, [logout]);

    // Anti copy/paste during tests
    useEffect(() => {
        if (!isTestActive) return;

        const handleCopy = (e: ClipboardEvent) => {
            e.preventDefault();
            addWarning('Copy attempt detected during test');
        };

        const handleCut = (e: ClipboardEvent) => {
            e.preventDefault();
            addWarning('Cut attempt detected during test');
        };

        const handlePaste = (e: ClipboardEvent) => {
            e.preventDefault();
            addWarning('Paste attempt detected during test');
        };

        const handleKeyDown = (e: KeyboardEvent) => {
            // Prevent Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A, PrintScreen
            if (e.ctrlKey && ['c', 'v', 'x', 'a'].includes(e.key.toLowerCase())) {
                e.preventDefault();
                addWarning(`Keyboard shortcut (Ctrl+${e.key.toUpperCase()}) detected during test`);
            }
            if (e.key === 'PrintScreen' || e.key === 'F12') {
                e.preventDefault();
                addWarning('Screenshot/DevTools attempt detected during test');
            }
            // Prevent Windows+Shift+S (Snipping Tool)
            if (e.metaKey && e.shiftKey && e.key.toLowerCase() === 's') {
                e.preventDefault();
                addWarning('Screenshot shortcut detected during test');
            }
        };

        const handleContextMenu = (e: MouseEvent) => {
            e.preventDefault();
            addWarning('Right-click context menu detected during test');
        };

        const handleVisibilityChange = () => {
            if (document.hidden && isTestActive) {
                addWarning('Tab switch detected during test');
            }
        };

        document.addEventListener('copy', handleCopy);
        document.addEventListener('cut', handleCut);
        document.addEventListener('paste', handlePaste);
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('contextmenu', handleContextMenu);
        document.addEventListener('visibilitychange', handleVisibilityChange);

        return () => {
            document.removeEventListener('copy', handleCopy);
            document.removeEventListener('cut', handleCut);
            document.removeEventListener('paste', handlePaste);
            document.removeEventListener('keydown', handleKeyDown);
            document.removeEventListener('contextmenu', handleContextMenu);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
    }, [isTestActive, addWarning]);

    return (
        <AntiCheatContext.Provider value={{
            warnings,
            maxWarnings: MAX_WARNINGS,
            isBlocked,
            blockUntil,
            addWarning,
            isTestActive,
            setTestActive,
        }}>
            {children}
            {/* Warning Toast */}
            {warningMessage && (
                <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] bg-red-600 text-white px-6 py-3 rounded-xl shadow-2xl text-sm font-semibold animate-bounce max-w-lg text-center">
                    {warningMessage}
                </div>
            )}
            {/* Blocked Overlay */}
            {isBlocked && showBlockedModal && (
                <div className="fixed inset-0 z-[9999] bg-black/90 flex items-center justify-center">
                    <div className="bg-white rounded-2xl p-8 max-w-md text-center shadow-2xl">
                        <div className="text-6xl mb-4">🚫</div>
                        <h2 className="text-2xl font-bold text-red-600 mb-2">Account Suspended</h2>
                        <p className="text-gray-600 mb-4">
                            You have exceeded the maximum number of warnings for prohibited actions during tests.
                        </p>
                        <p className="text-gray-800 font-semibold">
                            Please reattempt after: {blockUntil ? new Date(blockUntil).toLocaleDateString() : 'tomorrow'}
                        </p>
                        <button
                            onClick={() => {
                                setShowBlockedModal(false);
                                window.location.assign('/signin');
                            }}
                            className="mt-6 inline-flex items-center justify-center px-6 py-2.5 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors"
                        >
                            OK
                        </button>
                    </div>
                </div>
            )}
        </AntiCheatContext.Provider>
    );
}

export function useAntiCheat() {
    const ctx = useContext(AntiCheatContext);
    if (!ctx) throw new Error('useAntiCheat must be used within AntiCheatProvider');
    return ctx;
}
