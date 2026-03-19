import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAntiCheat } from '../context/AntiCheatContext';

/**
 * Hook that blocks all navigation when a mock test is active
 * Shows alert if user tries to navigate away during test
 */
export const useBlockNavigation = () => {
    const { isTestActive } = useAntiCheat();

    useEffect(() => {
        if (!isTestActive) return;

        // Block browser back button
        const handlePopState = (event: PopStateEvent) => {
            event.preventDefault();
            alert('❌ You cannot navigate away while a mock test is active. Please complete or quit the test first.');
            window.history.forward();
        };

        // Block page close/reload
        const handleBeforeUnload = (event: BeforeUnloadEvent) => {
            event.preventDefault();
            event.returnValue = '❌ You cannot leave while a mock test is active!';
            return '❌ You cannot leave while a mock test is active!';
        };

        window.addEventListener('popstate', handlePopState);
        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('popstate', handlePopState);
            window.removeEventListener('beforeunload', handleBeforeUnload);
        };
    }, [isTestActive]);
};

/**
 * Wrapper for navigate function to block navigation during test
 */
export const useProtectedNavigate = () => {
    const { isTestActive } = useAntiCheat();
    const navigationFn = useNavigate();

    return (path: string | number) => {
        if (isTestActive) {
            alert('❌ Cannot navigate during mock test. Please complete or quit the test first.');
            return;
        }
        if (typeof path === 'string') {
            navigationFn(path);
        } else {
            navigationFn(path);
        }
    };
};
