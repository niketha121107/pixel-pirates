import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { useAuth } from './AuthContext';
import { usersAPI } from '../services/api';

interface AntiCheatContextType {
    warnings: number;
    maxWarnings: number;
    isBlocked: boolean;
    blockUntil: string | null;
    addWarning: (reason: string) => Promise<void>;
    isTestActive: boolean;
    setTestActive: (active: boolean) => void;
    tabSwitchWarnings: number;
    savePageState: (pageName: string, state: any) => void;
    getPageState: (pageName: string) => any;
}

const AntiCheatContext = createContext<AntiCheatContextType | undefined>(undefined);

const MAX_WARNINGS = 5;

export function AntiCheatProvider({ children }: { children: ReactNode }) {
    const { logout, user } = useAuth();
    const [warnings, setWarnings] = useState(0);
    const [maxWarnings, setMaxWarnings] = useState(MAX_WARNINGS);
    const [isBlocked, setIsBlocked] = useState(false);
    const [blockUntil, setBlockUntil] = useState<string | null>(null);
    const [showBlockedModal, setShowBlockedModal] = useState(true);
    const [isTestActive, setTestActive] = useState(false);
    const [warningMessage, setWarningMessage] = useState<string | null>(null);
    const [tabSwitchWarnings, setTabSwitchWarnings] = useState(0);
    const [showTabSwitchModal, setShowTabSwitchModal] = useState(false);
    const [pageStates, setPageStates] = useState<Record<string, any>>({});
    const warningTimeoutRef = useRef<number | null>(null);
    const tabSwitchTimeoutRef = useRef<number | null>(null);
    const lastVisibilityRef = useRef<boolean>(false);

    const showTimedWarning = useCallback((message: string) => {
        setWarningMessage(message);
        if (warningTimeoutRef.current) {
            window.clearTimeout(warningTimeoutRef.current);
        }
        warningTimeoutRef.current = window.setTimeout(() => {
            setWarningMessage(null);
            warningTimeoutRef.current = null;
        }, 5000);
    }, []);

    const applyIntegrityStatus = useCallback((data?: Record<string, unknown>) => {
        const warningsValue = typeof data?.warnings === 'number' ? data.warnings : 0;
        const maxWarningsValue = typeof data?.maxWarnings === 'number' ? data.maxWarnings : MAX_WARNINGS;
        const suspendedUntilValue = typeof data?.suspendedUntil === 'string' ? data.suspendedUntil : null;

        setWarnings(warningsValue);
        setMaxWarnings(maxWarningsValue);
        setBlockUntil(suspendedUntilValue);
        setIsBlocked(Boolean(suspendedUntilValue));
        setShowBlockedModal(Boolean(suspendedUntilValue));
    }, []);

    const handleSuspension = useCallback((data?: Record<string, unknown>) => {
        applyIntegrityStatus(data);
        const suspendedUntilValue = typeof data?.suspendedUntil === 'string' ? data.suspendedUntil : null;
        const fallbackMessage = suspendedUntilValue
            ? `Account suspended until ${new Date(suspendedUntilValue).toLocaleString()} (5 hours) for repeated prohibited actions during the mock test.`
            : 'Account suspended for 5 hours due to repeated prohibited actions during the mock test.';
        const message = typeof data?.message === 'string' ? data.message : fallbackMessage;
        setWarningMessage(message);
    }, [applyIntegrityStatus]);

    useEffect(() => {
        if (!user) {
            setWarnings(0);
            setMaxWarnings(MAX_WARNINGS);
            setIsBlocked(false);
            setBlockUntil(null);
            setShowBlockedModal(false);
            return;
        }

        usersAPI.getMockTestIntegrity()
            .then((res) => {
                applyIntegrityStatus(res.data?.data);
            })
            .catch((error: { response?: { status?: number; data?: { detail?: Record<string, unknown> } } }) => {
                if (error.response?.status === 423) {
                    handleSuspension(error.response.data?.detail);
                }
            });
    }, [user, applyIntegrityStatus, handleSuspension]);

    useEffect(() => {
        return () => {
            if (warningTimeoutRef.current) {
                window.clearTimeout(warningTimeoutRef.current);
            }
            if (tabSwitchTimeoutRef.current) {
                window.clearTimeout(tabSwitchTimeoutRef.current);
            }
        };
    }, []);

    // Reset tab switch warnings when test starts
    useEffect(() => {
        if (isTestActive) {
            setTabSwitchWarnings(0);
            setShowTabSwitchModal(false);
        }
    }, [isTestActive]);

    // Page state management
    const savePageState = useCallback((pageName: string, state: any) => {
        setPageStates(prev => ({
            ...prev,
            [pageName]: {
                ...state,
                timestamp: Date.now(),
                scrollPosition: window.scrollY,
            }
        }));
    }, []);

    const getPageState = useCallback((pageName: string) => {
        return pageStates[pageName] || null;
    }, [pageStates]);

    // Global tab switch detection (all pages except chatbot)
    useEffect(() => {
        const handleVisibilityChangeGlobal = () => {
            const currentlyHidden = document.hidden;
            
            if (currentlyHidden && lastVisibilityRef.current === false && !isTestActive) {
                // Tab switched away (not in mock test)
                showTimedWarning('⚠️ Tab switch detected - do not leave your current work');
                        
                // Try to refocus
                setTimeout(() => {
                    if (document.hidden) {
                        window.focus();
                    }
                }, 100);
            }
            
            lastVisibilityRef.current = currentlyHidden;
        };

        document.addEventListener('visibilitychange', handleVisibilityChangeGlobal);
        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChangeGlobal);
        };
    }, [isTestActive]);

    const addWarning = useCallback(async (reason: string) => {
        if (!user || !isTestActive) return;

        try {
            const res = await usersAPI.reportMockTestViolation(reason);
            const data = res.data?.data;

            if (data?.isSuspended) {
                handleSuspension(data);
                return;
            }

            applyIntegrityStatus(data);
            showTimedWarning(res.data?.message || data?.message || `Warning: ${reason}`);
        } catch (error) {
            const apiError = error as {
                response?: {
                    status?: number;
                    data?: {
                        detail?: Record<string, unknown>;
                        message?: string;
                    };
                };
            };

            if (apiError.response?.status === 423) {
                handleSuspension(apiError.response.data?.detail);
                return;
            }

            showTimedWarning(apiError.response?.data?.message || 'Unable to record mock test warning.');
        }
    }, [user, isTestActive, applyIntegrityStatus, handleSuspension, showTimedWarning]);

    // Anti copy/paste during tests and screen recording detection
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
            if (e.key === 'PrintScreen' || e.key === 'F12' || e.key === 'F11') {
                e.preventDefault();
                addWarning('Screenshot/DevTools attempt detected during test');
            }
            // Prevent Windows+Shift+S (Snipping Tool)
            if (e.metaKey && e.shiftKey && e.key.toLowerCase() === 's') {
                e.preventDefault();
                addWarning('Screenshot shortcut (Win+Shift+S) detected during test');
            }
            // Prevent Shift+PrintScreen
            if (e.shiftKey && e.key === 'PrintScreen') {
                e.preventDefault();
                addWarning('Screenshot shortcut (Shift+PrintScreen) detected during test');
            }
        };

        const handleContextMenu = (e: MouseEvent) => {
            e.preventDefault();
            addWarning('Right-click context menu detected during test');
        };

        const handleVisibilityChange = () => {
            if (document.hidden && isTestActive) {
                // Add warning for tab switch IMMEDIATELY with visual feedback
                showTimedWarning('🚨 STOP! Tab switch detected during test - RETURN IMMEDIATELY');
                addWarning('Tab switch detected during test - return to test immediately');
                
                // Aggressively try to refocus
                setTimeout(() => {
                    window.focus();
                    document.body.focus();
                }, 50);
                
                setTimeout(() => {
                    window.focus();
                    document.body.focus();
                }, 200);
                
                // Track tab switches
                setTabSwitchWarnings(prev => {
                    const newCount = prev + 1;
                    if (newCount >= 2) {
                        // Show prominent modal after 2 switches
                        setShowTabSwitchModal(true);
                        if (tabSwitchTimeoutRef.current) clearTimeout(tabSwitchTimeoutRef.current);
                        tabSwitchTimeoutRef.current = window.setTimeout(() => {
                            setShowTabSwitchModal(false);
                        }, 10000);
                    }
                    return newCount;
                });
            } else if (!document.hidden && isTestActive && tabSwitchWarnings > 0) {
                // User returns to test tab - show warning modal
                setShowTabSwitchModal(true);
                showTimedWarning('You switched tabs! This has been recorded as a violation');
                if (tabSwitchTimeoutRef.current) clearTimeout(tabSwitchTimeoutRef.current);
                tabSwitchTimeoutRef.current = window.setTimeout(() => {
                    setShowTabSwitchModal(false);
                }, 8000);
            }
        };

        // Block screenshot-related APIs
        const originalCanvas = (window as any).HTMLCanvasElement?.prototype?.toDataURL;
        
        if (originalCanvas) {
            (window as any).HTMLCanvasElement.prototype.toDataURL = function() {
                addWarning('Canvas screenshot attempt detected during test');
                throw new Error('Canvas operations are not allowed during test');
            };
        }

        // Block screen recording API (MediaRecorder)
        const originalMediaRecorder = (window as any).MediaRecorder;
        if (originalMediaRecorder) {
            (window as any).MediaRecorder = class extends originalMediaRecorder {
                constructor(...args: any[]) {
                    super(...args);
                    addWarning('Screen recording attempt detected during test');
                    throw new Error('Screen recording is not allowed during test');
                }
            };
        }

        // Block screen capture API (getDisplayMedia)
        if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {
            navigator.mediaDevices.getDisplayMedia = async function() {
                await addWarning('Screen capture attempt detected during test');
                throw new Error('Screen capture is not allowed during test');
            };
        }

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
            maxWarnings,
            isBlocked,
            blockUntil,
            addWarning,
            isTestActive,
            setTestActive,
            tabSwitchWarnings,
            savePageState,
            getPageState,
        }}>
            {children}
            
            {/* Tab Switch Warning Modal (During Test) */}
            {showTabSwitchModal && isTestActive && (
                <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 animate-bounce">
                        <div className="flex justify-center mb-4">
                            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                                <AlertTriangle className="w-8 h-8 text-red-600 animate-pulse" />
                            </div>
                        </div>
                        <h3 className="text-center font-bold text-red-900 text-lg mb-2">Tab Switch Detected!</h3>
                        <p className="text-center text-sm text-gray-700 mb-4">
                            You switched away from the test tab. This is not allowed and has been recorded as a violation.
                        </p>
                        <p className="text-center text-xs text-gray-600 mb-4">
                            Tab switches: <span className="font-bold text-red-600">{tabSwitchWarnings}</span>
                        </p>
                        <p className="text-center text-xs text-amber-600 font-semibold">
                            ⚠️ More violations will result in test termination
                        </p>
                    </div>
                </div>
            )}
            
            {/* Warning Toast - Improved visibility */}
            {warningMessage && (
                <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] bg-red-600 text-white px-6 py-4 rounded-xl shadow-2xl text-sm font-semibold animate-bounce max-w-lg text-center border-2 border-red-700">
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
                            Please reattempt after: {blockUntil ? new Date(blockUntil).toLocaleString() : '2 hours'}
                        </p>
                        <button
                            onClick={() => {
                                setShowBlockedModal(false);
                                logout();
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
