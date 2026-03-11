import { useState, useCallback, useRef, useEffect } from 'react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SpeechRecognitionType = any;

interface UseVoiceSearchReturn {
    isListening: boolean;
    transcript: string;
    startListening: () => void;
    stopListening: () => void;
    isSupported: boolean;
    error: string | null;
}

export function useVoiceSearch(onResult?: (text: string) => void): UseVoiceSearchReturn {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [error, setError] = useState<string | null>(null);
    const recognitionRef = useRef<SpeechRecognitionType | null>(null);

    const isSupported = typeof window !== 'undefined' && 
        ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

    useEffect(() => {
        if (!isSupported) return;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SR();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: { resultIndex: number; results: { isFinal: boolean; 0: { transcript: string } }[] }) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                if (result.isFinal) {
                    finalTranscript += result[0].transcript;
                } else {
                    interimTranscript += result[0].transcript;
                }
            }

            const text = finalTranscript || interimTranscript;
            setTranscript(text);

            if (finalTranscript && onResult) {
                onResult(finalTranscript);
            }
        };

        recognition.onerror = (event: { error: string }) => {
            setError(`Speech recognition error: ${event.error}`);
            setIsListening(false);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognitionRef.current = recognition;

        return () => {
            recognition.abort();
        };
    }, [isSupported, onResult]);

    const startListening = useCallback(() => {
        if (!recognitionRef.current) return;
        setError(null);
        setTranscript('');
        try {
            recognitionRef.current.start();
            setIsListening(true);
        } catch (_e) {
            setError('Could not start voice recognition');
        }
    }, []);

    const stopListening = useCallback(() => {
        if (!recognitionRef.current) return;
        recognitionRef.current.stop();
        setIsListening(false);
    }, []);

    return {
        isListening,
        transcript,
        startListening,
        stopListening,
        isSupported,
        error,
    };
}
