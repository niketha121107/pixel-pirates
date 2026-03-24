import { useState, useRef, useEffect, useCallback } from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Play, Pause, RotateCcw, RotateCw, Subtitles, AlertTriangle, Loader2 } from 'lucide-react';

interface VideoTrackerUIProps {
    url: string;
    onProgress?: (played: number) => void;
    onEnded?: () => void;
}

// Global declaration for YouTube Iframe API
declare global {
    interface Window {
        YT: any;
        onYouTubeIframeAPIReady: () => void;
    }
}

export const VideoTrackerUI = ({ url, onProgress: onProgressCallback, onEnded }: VideoTrackerUIProps) => {
    const [isReady, setIsReady] = useState(false);
    const [hasError, setHasError] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [duration, setDuration] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const [isCaptionsOn, setIsCaptionsOn] = useState(false);
    
    const containerRef = useRef<HTMLDivElement>(null);
    const playerRef = useRef<any>(null);
    const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Keep callbacks in refs to avoid re-triggering useEffect when functions are recreated in parent
    const callbacksRef = useRef({ onProgress: onProgressCallback, onEnded });
    useEffect(() => {
        callbacksRef.current = { onProgress: onProgressCallback, onEnded };
    }, [onProgressCallback, onEnded]);

    // Extract YouTube video ID
    const getVideoId = useCallback((playerUrl: string): string => {
        if (!playerUrl) return '';

        if (playerUrl.includes('youtube.com/watch')) {
            const match = playerUrl.match(/v=([a-zA-Z0-9_-]{11})/);
            return match ? match[1] : '';
        } else if (playerUrl.includes('youtu.be/')) {
            const match = playerUrl.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
            return match ? match[1] : '';
        } else if (playerUrl.includes('youtube.com/embed/')) {
            const match = playerUrl.match(/embed\/([a-zA-Z0-9_-]{11})/);
            return match ? match[1] : '';
        } else if (/^[a-zA-Z0-9_-]{11}$/.test(playerUrl)) {
            return playerUrl;
        }

        return '';
    }, []);

    const videoId = getVideoId(url);

    useEffect(() => {
        if (!videoId || !containerRef.current) return;

        // Cleanup before starting
        if (playerRef.current) {
            try {
                if (progressIntervalRef.current) {
                    clearInterval(progressIntervalRef.current);
                }
                playerRef.current.destroy();
                playerRef.current = null;
            } catch (e) {
                console.error("Error destroying YT player:", e);
            }
        }

        setIsReady(false);
        setHasError(false);
        setIsPlaying(false);
        setCurrentTime(0);

        const initPlayer = () => {
            if (!containerRef.current) return;

            // Create target directly inside container
            const targetDiv = document.createElement('div');
            targetDiv.id = `yt-player-target-${Date.now()}`;
            targetDiv.style.width = '100%';
            targetDiv.style.height = '100%';
            containerRef.current.innerHTML = '';
            containerRef.current.appendChild(targetDiv);

            playerRef.current = new window.YT.Player(targetDiv.id, {
                videoId: videoId,
                playerVars: {
                    controls: 0,           // Hide all default YouTube controls
                    disablekb: 1,          // Disable keyboard controls to prevent default shortcuts
                    modestbranding: 1,     // Reduce YouTube branding
                    rel: 0,                // Do not show related videos from other channels
                    showinfo: 0,           // Deprecated but still used sometimes; hides video title
                    iv_load_policy: 3,     // Hide video annotations
                    fs: 0,                 // Hide fullscreen button
                    cc_load_policy: 0,     // Closed captions off by default
                    playsinline: 1         // Play inline on mobile
                },
                events: {
                    onReady: (event: any) => {
                        setIsReady(true);
                        setDuration(event.target.getDuration());
                    },
                    onStateChange: (event: any) => {
                        const State = window.YT.PlayerState;
                        
                        if (event.data === State.PLAYING) {
                            setIsPlaying(true);
                            
                            if (progressIntervalRef.current) {
                                clearInterval(progressIntervalRef.current);
                            }
                            
                            progressIntervalRef.current = setInterval(() => {
                                if (playerRef.current && typeof playerRef.current.getCurrentTime === 'function') {
                                    const time = playerRef.current.getCurrentTime();
                                    const dur = playerRef.current.getDuration();
                                    setCurrentTime(time);
                                    
                                    if (dur > 0) {
                                        const percentage = (time / dur) * 100;
                                        callbacksRef.current.onProgress?.(Math.min(percentage, 100));
                                    }
                                }
                            }, 500);
                            
                        } else {
                            setIsPlaying(false);
                            if (progressIntervalRef.current) {
                                clearInterval(progressIntervalRef.current);
                            }
                        }

                        if (event.data === State.ENDED) {
                            setCurrentTime(event.target.getDuration());
                            callbacksRef.current.onProgress?.(100);
                            callbacksRef.current.onEnded?.();
                        }
                    },
                    onError: (e: any) => {
                        console.error('YouTube player error:', e);
                        setHasError(true);
                        setIsReady(true);
                    }
                }
            });
        };

        if (!window.YT) {
            const scriptTarget = document.createElement('script');
            scriptTarget.src = 'https://www.youtube.com/iframe_api';
            const firstScript = document.getElementsByTagName('script')[0];
            
            if (firstScript && firstScript.parentNode) {
                firstScript.parentNode.insertBefore(scriptTarget, firstScript);
            } else {
                document.head.appendChild(scriptTarget);
            }
            
            window.onYouTubeIframeAPIReady = () => {
                initPlayer();
            };
        } else {
            // Run on next tick to ensure container DOM is ready
            setTimeout(() => {
                initPlayer();
            }, 10);
        }

        return () => {
            if (progressIntervalRef.current) {
                clearInterval(progressIntervalRef.current);
            }
            if (playerRef.current) {
                try {
                    playerRef.current.destroy();
                    playerRef.current = null;
                } catch (e) {
                    // Ignore on unmount
                }
            }
        };
    }, [videoId]); // Only depends on videoId, avoiding infinite re-renders!

    /* Custom Control Handlers */
    
    const handlePlayPause = () => {
        if (!playerRef.current || !isReady) return;
        
        if (isPlaying) {
            playerRef.current.pauseVideo();
        } else {
            playerRef.current.playVideo();
        }
    };

    const handleBackward = () => {
        if (!playerRef.current || !isReady) return;
        const newTime = Math.max(playerRef.current.getCurrentTime() - 5, 0);
        playerRef.current.seekTo(newTime, true);
        setCurrentTime(newTime);
    };

    const handleForward = () => {
        if (!playerRef.current || !isReady) return;
        const newTime = Math.min(playerRef.current.getCurrentTime() + 5, duration);
        playerRef.current.seekTo(newTime, true);
        setCurrentTime(newTime);
    };

    const handleToggleCaptions = () => {
        if (!playerRef.current || !isReady) return;
        
        const newState = !isCaptionsOn;
        setIsCaptionsOn(newState);
        
        if (newState) {
            playerRef.current.loadModule('captions');
            // Try to set English by default, fallback to whatever is available
            try {
                playerRef.current.setOption('captions', 'track', { languageCode: 'en' });
            } catch (e) {
                console.error("Toggle captions error", e);
            }
        } else {
            playerRef.current.unloadModule('captions');
        }
    };
    
    const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!playerRef.current || !isReady || duration === 0) return;
        
        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percentage = Math.max(0, Math.min(1, clickX / rect.width));
        const newTime = percentage * duration;
        
        playerRef.current.seekTo(newTime, true);
        setCurrentTime(newTime);
    };

    // Format time helpers (e.g., 01:23)
    const formatTime = (timeInSeconds: number) => {
        if (!timeInSeconds || isNaN(timeInSeconds)) return "0:00";
        const m = Math.floor(timeInSeconds / 60);
        const s = Math.floor(timeInSeconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    };

    if (!videoId) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-gray-900 rounded-xl overflow-hidden flex flex-col items-center justify-center text-gray-400">
                    <AlertTriangle className="w-8 h-8 mb-2 opacity-50" />
                    <p className="text-sm font-medium text-white mb-1">No video available</p>
                    <p className="text-xs text-gray-400">Try clicking "Get Fresh Videos" below</p>
                </div>
            </GlassCard>
        );
    }

    if (hasError) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-gray-900 rounded-xl overflow-hidden flex flex-col items-center justify-center text-gray-400">
                    <AlertTriangle className="w-8 h-8 mb-2 opacity-50 text-red-500" />
                    <p className="text-sm font-medium text-white mb-1">Video failed to load</p>
                    <p className="text-xs text-gray-400">YouTube video may not be available or restricted by the owner</p>
                </div>
            </GlassCard>
        );
    }

    const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

    return (
        <GlassCard className="p-0 overflow-hidden group">
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                
                {/* 
                   Render YouTube iframe.
                   Pointer-events are disabled so users cannot interact with the iframe directly.
                   We scale it up slightly (e.g. scale-105 or w-[110%]) to push unwanted YouTube edges out of frame. 
                */}
                <div 
                    className="absolute inset-[-5%] w-[110%] h-[110%] pointer-events-none"
                    ref={containerRef} 
                />

                {/* Loading State Overlay */}
                {!isReady && (
                    <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-gray-900 text-white">
                        <Loader2 className="w-8 h-8 mb-3 animate-spin text-primary" />
                        <span className="text-sm font-medium text-gray-300">Connecting to player...</span>
                    </div>
                )}

                {/* Custom UI Controls Overlay */}
                <div 
                    className={`absolute inset-0 z-20 flex flex-col justify-end transition-opacity duration-300
                                ${!isPlaying ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}
                                bg-gradient-to-t from-black/90 via-black/20 to-transparent`}
                >
                    {/* Interactive Play/Pause invisible click area on the entire video */}
                    <div className="flex-1 cursor-pointer" onClick={handlePlayPause} />

                    {/* Controls Footer */}
                    <div className="w-full pb-2">
                        {/* Custom Progress Bar */}
                        <div 
                            className="w-full h-1.5 bg-gray-700/80 cursor-pointer relative mb-3 hover:h-2 transition-all"
                            onClick={handleSeek}
                        >
                            <div 
                                className="absolute top-0 left-0 h-full bg-primary transition-all duration-200"
                                style={{ width: `${progressPercent}%` }}
                            />
                            {/* Scrubber Dot */}
                            <div 
                                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow border-2 border-primary transform -ml-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
                                style={{ left: `${progressPercent}%` }}
                            />
                        </div>

                        {/* Control Buttons */}
                        <div className="flex items-center justify-between px-4 pb-2">
                            {/* Left Controls */}
                            <div className="flex items-center space-x-5">
                                <button 
                                    onClick={handlePlayPause} 
                                    className="text-white hover:text-primary transition-colors focus:outline-none"
                                >
                                    {isPlaying ? (
                                        <Pause className="w-6 h-6 fill-current" />
                                    ) : (
                                        <Play className="w-6 h-6 fill-current ml-0.5" />
                                    )}
                                </button>
                                
                                <button 
                                    onClick={handleBackward} 
                                    className="text-gray-200 hover:text-white transition-colors focus:outline-none"
                                    title="Backward 5 seconds"
                                >
                                    <RotateCcw className="w-5 h-5" />
                                </button>
                                
                                <button 
                                    onClick={handleForward} 
                                    className="text-gray-200 hover:text-white transition-colors focus:outline-none"
                                    title="Forward 5 seconds"
                                >
                                    <RotateCw className="w-5 h-5" />
                                </button>

                                <span className="text-xs font-medium text-gray-200 ml-2 tabular-nums">
                                    {formatTime(currentTime)} / {formatTime(duration)}
                                </span>
                            </div>

                            {/* Right Controls */}
                            <div className="flex items-center space-x-4">
                                <button 
                                    onClick={handleToggleCaptions} 
                                    className={`transition-colors focus:outline-none border-b-2 
                                        ${isCaptionsOn ? 'text-primary border-primary' : 'text-gray-300 border-transparent hover:text-white'}`}
                                    title="Toggle Captions"
                                >
                                    <Subtitles className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </GlassCard>
    );
};
