import { useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player';
import { GlassCard } from '../ui/GlassCard';

interface VideoTrackerUIProps {
    url: string;
    onProgress?: (played: number) => void;
    onEnded?: () => void;
}

export const VideoTrackerUI = ({ url, onProgress: onProgressCallback, onEnded }: VideoTrackerUIProps) => {
    const [progress, setProgress] = useState(0);
    const [loadEmbed, setLoadEmbed] = useState(false);
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval>>();

    // Extract YouTube video ID
    const getYouTubeId = (videoUrl: string) => {
        const match = videoUrl.match(/(?:v=|youtu\.be\/)([\w-]{11})/);
        return match ? match[1] : null;
    };

    const videoId = getYouTubeId(url);

    // For YouTube videos, track approximate progress via timer
    useEffect(() => {
        if (!videoId || !loadEmbed) return;
        // Simple timer-based progress estimation (since iframe API is complex)
        let elapsed = 0;
        const estimatedDuration = 600; // assume ~10 min
        intervalRef.current = setInterval(() => {
            elapsed += 1;
            const played = Math.min((elapsed / estimatedDuration) * 100, 99);
            setProgress(played);
            onProgressCallback?.(played);
        }, 1000);

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [videoId, loadEmbed]);

    // For YouTube URLs, use direct iframe embed (more reliable than react-player)
    if (videoId) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                    {!loadEmbed ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-gradient-to-br from-slate-900 to-slate-800 text-white px-4 text-center">
                            <p className="text-sm text-white/85">Video is ready to load.</p>
                            <button
                                onClick={() => setLoadEmbed(true)}
                                className="px-4 py-2 rounded-lg bg-brand text-white text-sm font-semibold hover:bg-brand/90 transition-colors"
                            >
                                Load Video
                            </button>
                        </div>
                    ) : (
                        <iframe
                            ref={iframeRef}
                            src={`https://www.youtube-nocookie.com/embed/${videoId}?rel=0&modestbranding=1&autoplay=0&enablejsapi=1`}
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                            className="absolute inset-0 w-full h-full"
                            title="Video lesson"
                        />
                    )}
                </div>
            </GlassCard>
        );
    }

    // Bypass faulty react-player TypeScript definitions
    const Player = ReactPlayer as any;

    // For non-YouTube URLs, use react-player
    return (
        <GlassCard className="p-0 overflow-hidden">
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                <Player
                    url={url}
                    width="100%"
                    height="100%"
                    controls
                    onProgress={(state: any) => {
                        const played = state.played * 100;
                        setProgress(played);
                        onProgressCallback?.(played);
                    }}
                    onEnded={onEnded}
                    config={{
                        youtube: {
                            playerVars: {
                                modestbranding: 1,
                                rel: 0,
                                origin: window.location.origin,
                            },
                        },
                    }}
                />
            </div>
        </GlassCard>
    );
};
