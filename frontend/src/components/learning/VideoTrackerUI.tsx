import { useState, useEffect, useRef } from 'react';
import { GlassCard } from '../ui/GlassCard';

interface VideoTrackerUIProps {
    url: string;
    onProgress?: (played: number) => void;
    onEnded?: () => void;
}

declare global {
    interface Window {
        YT: any;
        onYouTubeIframeAPIReady: () => void;
    }
}

export const VideoTrackerUI = ({ url, onProgress: onProgressCallback, onEnded }: VideoTrackerUIProps) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const [showCaptions, setShowCaptions] = useState(false);
    const playerRef = useRef<any>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const intervalRef = useRef<any>(null);
    const isMounted = useRef(true);

    const getYouTubeId = (videoUrl: string): string => {
        if (!videoUrl) return '';
        if (/^[a-zA-Z0-9_-]{11}$/.test(videoUrl)) return videoUrl;
        const watchMatch = videoUrl.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
        if (watchMatch) return watchMatch[1];
        const embedMatch = videoUrl.match(/embed\/([a-zA-Z0-9_-]{11})/);
        if (embedMatch) return embedMatch[1];
        const shortMatch = videoUrl.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
        if (shortMatch) return shortMatch[1];
        return '';
    };

    const videoId = getYouTubeId(url);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    };

    const startTracking = () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
        intervalRef.current = setInterval(() => {
            if (!playerRef.current || !isMounted.current) return;
            try {
                const cur = playerRef.current.getCurrentTime();
                const dur = playerRef.current.getDuration();
                if (dur > 0) {
                    const pct = Math.min((cur / dur) * 100, 100);
                    setCurrentTime(cur);
                    setDuration(dur);
                    setProgress(pct);
                    onProgressCallback?.(pct);
                }
            } catch (e) {}
        }, 1000);
    };

    const stopTracking = () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
    };

    const handlePlayPause = () => {
        if (!playerRef.current) return;
        try {
            const state = playerRef.current.getPlayerState();
            if (state === 1) { // playing
                playerRef.current.pauseVideo();
            } else {
                playerRef.current.playVideo();
            }
        } catch (e) {}
    };

    const handleSeek = (seconds: number) => {
        if (!playerRef.current) return;
        try {
            const cur = playerRef.current.getCurrentTime();
            playerRef.current.seekTo(Math.max(0, cur + seconds), true);
        } catch (e) {}
    };

    const handleCaptionToggle = () => {
        if (!playerRef.current) return;
        try {
            if (showCaptions) {
                playerRef.current.unloadModule('captions');
            } else {
                playerRef.current.loadModule('captions');
                playerRef.current.setOption('captions', 'track', { languageCode: 'en' });
            }
            setShowCaptions(!showCaptions);
        } catch (e) {}
    };

    const initPlayer = () => {
        if (!containerRef.current || !videoId) return;

        const divId = `yt-player-${videoId}`;
        let playerDiv = document.getElementById(divId);
        if (!playerDiv) {
            playerDiv = document.createElement('div');
            playerDiv.id = divId;
            containerRef.current.appendChild(playerDiv);
        }

        playerRef.current = new window.YT.Player(divId, {
            videoId,
            width: '100%',
            height: '100%',
            playerVars: {
                controls: 0,          // ← Hide ALL default YouTube controls (requested)
                rel: 0,               // ← Disable related videos
                modestbranding: 1,    // ← Use minimal branding
                iv_load_policy: 3,    // ← Hide overlays
                fs: 0,                // Disable fullscreen (cleans up UI)
                disablekb: 1,         // Disable keyboard to prevent native shortcuts
                showinfo: 0,
                autohide: 1,
                playsinline: 1,
            },
            events: {
                onReady: () => {
                    if (isMounted.current) {
                        setIsLoaded(true);
                        try {
                            setDuration(playerRef.current.getDuration());
                        } catch (e) {}
                    }
                },
                onStateChange: (event: any) => {
                    if (!isMounted.current) return;
                    const state = event.data;
                    if (state === 1) { // PLAYING
                        setIsPlaying(true);
                        startTracking();
                    }
                    if (state === 2) { // PAUSED
                        setIsPlaying(false);
                        stopTracking();
                    }
                    if (state === 0) { // ENDED
                        setIsPlaying(false);
                        stopTracking();
                        setProgress(100);
                        onProgressCallback?.(100);
                        onEnded?.();
                    }
                },
            },
        });
    };

    useEffect(() => {
        isMounted.current = true;

        const load = () => {
            if (window.YT && window.YT.Player) {
                initPlayer();
            } else {
                if (!document.getElementById('yt-api-script')) {
                    const script = document.createElement('script');
                    script.id = 'yt-api-script';
                    script.src = 'https://www.youtube.com/iframe_api';
                    document.body.appendChild(script);
                }
                window.onYouTubeIframeAPIReady = () => {
                    if (isMounted.current) initPlayer();
                };
            }
        };

        load();

        return () => {
            isMounted.current = false;
            stopTracking();
            try { playerRef.current?.destroy(); } catch (e) {}
        };
    }, [videoId]);

    if (!videoId) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-gray-900 rounded-xl flex items-center justify-center">
                    <div className="text-center text-white">
                        <p className="text-sm">⚠️ Invalid video URL</p>
                    </div>
                </div>
            </GlassCard>
        );
    }

    return (
        <GlassCard className="p-0 overflow-hidden border-2 border-brand/20">
            {/* Video Area */}
            <div className="relative aspect-video bg-black rounded-t-xl overflow-hidden">
                {!isLoaded && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/90 z-20 pointer-events-none">
                        <div className="text-white text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-3" />
                            <p className="text-sm">Loading video API...</p>
                        </div>
                    </div>
                )}
                
                {/* 
                  Clipping Container: 
                  We make the iframe even taller and shift it more to hide the persistent 
                  YouTube title bar (Share, Watch Later) and bottom logo.
                */}
                <div 
                    className="absolute inset-x-0 bottom-0 top-0 overflow-hidden"
                    style={{ pointerEvents: 'auto' }}
                >
                    <div
                        ref={containerRef}
                        style={{ 
                            position: 'absolute', 
                            top: '-50px',     // Increased to hide full title bar
                            left: 0, 
                            width: '100%', 
                            height: 'calc(100% + 100px)' 
                        }}
                    />
                </div>

                {/* Custom Overlay for Paused/Ended states (Hides "More videos" shelf) */}
                {isLoaded && !isPlaying && (
                    <div className="absolute inset-0 z-10 bg-black/60 backdrop-blur-[2px] flex items-center justify-center pointer-events-none transition-opacity duration-300">
                        <div className="w-20 h-20 rounded-full bg-brand/10 flex items-center justify-center border border-brand/30 animate-pulse">
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10 text-brand/80" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M8 5v14l11-7z"/>
                            </svg>
                        </div>
                    </div>
                )}
                
                {/* Interaction layer: transparent but blocks context menus and handles clicks */}
                <div 
                    className="absolute inset-0 z-20 cursor-pointer" 
                    onClick={handlePlayPause}
                    onContextMenu={(e) => e.preventDefault()}
                />
            </div>

            {/* ── Custom Control Bar ── */}
            <div className="bg-gray-950 px-5 py-4 flex flex-col gap-4 border-t border-brand/10">
                {/* Progress Bar */}
                <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden group">
                    <div 
                        className="h-full bg-brand rounded-full transition-all duration-300 shadow-[0_0_10px_rgba(var(--brand-rgb),0.5)]"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-6">
                        {/* Backward 5s */}
                        <button 
                            onClick={() => handleSeek(-5)}
                            className="text-gray-400 hover:text-white transition-colors p-1"
                            title="Rewind 5s"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/>
                                <text x="14" y="22" fontSize="6" fill="currentColor" stroke="none" fontWeight="bold">5s</text>
                            </svg>
                        </button>

                        {/* Play/Pause */}
                        <button 
                            onClick={handlePlayPause}
                            className="w-12 h-12 rounded-full bg-brand flex items-center justify-center text-white hover:scale-110 active:scale-95 transition-all shadow-lg shadow-brand/20"
                        >
                            {isPlaying ? (
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 ml-1" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M8 5v14l11-7z"/>
                                </svg>
                            )}
                        </button>

                        {/* Forward 5s */}
                        <button 
                            onClick={() => handleSeek(5)}
                            className="text-gray-400 hover:text-white transition-colors p-1"
                            title="Forward 5s"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M13 17l5-5-5-5M6 17l5-5-5-5"/>
                                <text x="2" y="22" fontSize="6" fill="currentColor" stroke="none" fontWeight="bold">5s</text>
                            </svg>
                        </button>

                        <div className="text-xs font-mono text-gray-500 tabular-nums">
                            {formatTime(currentTime)} / {formatTime(duration)}
                        </div>
                    </div>

                    {/* Captions Toggle */}
                    <button 
                        onClick={handleCaptionToggle}
                        className={`text-xs px-3 py-1.5 rounded-lg font-bold border transition-all ${
                            showCaptions 
                                ? 'bg-brand/20 border-brand text-brand' 
                                : 'bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-500'
                        }`}
                    >
                        CC
                    </button>
                </div>
            </div>
        </GlassCard>
    );
};
