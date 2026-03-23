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
            if (state === 1) {
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

    const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!playerRef.current || duration === 0) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const pct = x / rect.width;
        const seekTo = pct * duration;
        playerRef.current.seekTo(seekTo, true);
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
        } catch (e) {
            setShowCaptions(!showCaptions);
        }
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
                controls: 0,          // ← Hide ALL YouTube controls
                rel: 0,
                modestbranding: 1,
                fs: 0,
                iv_load_policy: 3,
                cc_load_policy: 0,
                playsinline: 1,
                disablekb: 1,
                showinfo: 0,
                autohide: 1,
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
                    if (state === 1) {
                        setIsPlaying(true);
                        try { event.target.setPlaybackRate(1); } catch (e) {}
                        startTracking();
                    }
                    if (state === 2) {
                        setIsPlaying(false);
                        stopTracking();
                    }
                    if (state === 0) {
                        setIsPlaying(false);
                        stopTracking();
                        setProgress(100);
                        onProgressCallback?.(100);
                        onEnded?.();
                    }
                },
                onPlaybackRateChange: (event: any) => {
                    try { event.target.setPlaybackRate(1); } catch (e) {}
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
        <GlassCard className="p-0 overflow-hidden">
            {/* Video Area */}
            <div className="relative aspect-video bg-black rounded-t-xl overflow-hidden">
                {!isLoaded && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/90 z-10 pointer-events-none">
                        <div className="text-white text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-3" />
                            <p className="text-sm">Loading video...</p>
                        </div>
                    </div>
                )}
                <div
                    ref={containerRef}
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
                />
                {/* Overlay to block YouTube click-through UI */}
                <div
                    className="absolute inset-0 z-10"
                    style={{ background: 'transparent' }}
                    onClick={handlePlayPause}
                />
            </div>

            {/* ── Custom Controls Bar ── */}
            <div className="bg-gray-900 rounded-b-xl px-4 py-3 flex flex-col gap-2">

                {/* Progress Bar */}
                <div
                    className="w-full h-2 bg-gray-700 rounded-full cursor-pointer relative"
                    onClick={handleProgressClick}
                >
                    <div
                        className="h-full bg-brand rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Controls Row */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">

                        {/* Rewind 5s */}
                        <button
                            onClick={() => handleSeek(-5)}
                            className="text-white hover:text-brand transition-colors flex flex-col items-center"
                            title="Rewind 5s"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
                                <text x="9" y="15" fontSize="5" fill="currentColor" fontWeight="bold">5</text>
                            </svg>
                        </button>

                        {/* Play / Pause */}
                        <button
                            onClick={handlePlayPause}
                            className="w-10 h-10 rounded-full bg-brand flex items-center justify-center text-white hover:bg-brand/80 transition-colors"
                            title={isPlaying ? 'Pause' : 'Play'}
                        >
                            {isPlaying ? (
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 ml-0.5" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M8 5v14l11-7z"/>
                                </svg>
                            )}
                        </button>

                        {/* Forward 5s */}
                        <button
                            onClick={() => handleSeek(5)}
                            className="text-white hover:text-brand transition-colors"
                            title="Forward 5s"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/>
                                <text x="9" y="15" fontSize="5" fill="currentColor" fontWeight="bold">5</text>
                            </svg>
                        </button>

                        {/* Time */}
                        <span className="text-xs text-gray-400 font-mono">
                            {formatTime(currentTime)} / {formatTime(duration)}
                        </span>
                    </div>

                    {/* Caption Toggle */}
                    <button
                        onClick={handleCaptionToggle}
                        className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                            showCaptions
                                ? 'bg-brand text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                        title="Toggle Captions"
                    >
                        CC
                    </button>
                </div>
            </div>
        </GlassCard>
    );
};
