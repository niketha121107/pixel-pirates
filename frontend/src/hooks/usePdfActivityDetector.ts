import { useState, useEffect, useRef, useCallback } from 'react';

interface UsePdfActivityDetectorOptions {
    inactivityTimeout?: number; // ms after which we consider viewing ended (default: 30s)
}

/**
 * Detects when user is actively viewing/interacting with PDF viewer.
 * Returns true if user is actively reading/scrolling, false otherwise.
 */
export function usePdfActivityDetector(options: UsePdfActivityDetectorOptions = {}) {
    const { inactivityTimeout = 30000 } = options;
    const [isViewingPdf, setIsViewingPdf] = useState(false);
    const inactivityTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const lastActivityRef = useRef<number>(0);

    const handlePdfActivity = useCallback(() => {
        lastActivityRef.current = Date.now();
        setIsViewingPdf(true);

        // Clear existing timeout
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
        }

        // Set new timeout - if no activity for inactivityTimeout ms, stop viewing
        inactivityTimerRef.current = setTimeout(() => {
            const timeSinceLastActivity = Date.now() - lastActivityRef.current;
            if (timeSinceLastActivity >= inactivityTimeout) {
                setIsViewingPdf(false);
                console.log('[PDF Detector] User stopped viewing PDF (inactivity timeout)');
            }
        }, inactivityTimeout);
    }, [inactivityTimeout]);

    // Detect PDF scroll events
    useEffect(() => {
        // Find PDF viewer container - common selectors
        const pdfViewerSelectors = [
            '.pdf-viewer',
            '[class*="pdf"]',
            '[class*="viewer"]',
            'iframe[src*="pdf"]',
        ];

        const detectScroll = (e: Event) => {
            handlePdfActivity();
            console.log('[PDF Detector] Scroll detected');
        };

        const detectClick = (e: Event) => {
            const target = e.target as HTMLElement;
            // Check if click is within PDF viewer area
            if (target?.closest('[class*="pdf"], [class*="viewer"], .pdf-viewer')) {
                handlePdfActivity();
                console.log('[PDF Detector] Click detected on PDF');
            }
        };

        const detectWheel = (e: WheelEvent) => {
            const target = e.target as HTMLElement;
            if (target?.closest('[class*="pdf"], [class*="viewer"], .pdf-viewer')) {
                handlePdfActivity();
                console.log('[PDF Detector] Wheel/zoom detected on PDF');
            }
        };

        // Attach listeners
        document.addEventListener('scroll', detectScroll, true);
        document.addEventListener('click', detectClick, true);
        document.addEventListener('wheel', detectWheel, true);

        return () => {
            document.removeEventListener('scroll', detectScroll, true);
            document.removeEventListener('click', detectClick, true);
            document.removeEventListener('wheel', detectWheel, true);
            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
            }
        };
    }, [handlePdfActivity]);

    return isViewingPdf;
}
