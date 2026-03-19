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
    const [isPlaying, setIsPlaying] = useState(false);
    const playerRef = useRef<any>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // Extract YouTube video ID
    const getYouTubeId = (videoUrl: string) => {
        const match = videoUrl.match(/(?:v=|youtu\.be\/)([\w-]{11})/);
        return match ? match[1] : null;
    };

    const videoId = getYouTubeId(url);

    // Initialize YouTube Iframe API
    useEffect(() => {
        if (!videoId || !loadEmbed) return;

        // Load YouTube IFrame API
        if (!(window as any).YT) {
            const tag = document.createElement('script');
            tag.src = 'https://www.youtube.com/iframe_api';
            document.body.appendChild(tag);
        }

        // Wait for YT to be ready, then create player
        const checkYT = setInterval(() => {
            if ((window as any).YT && (window as any).YT.Player) {
                clearInterval(checkYT);
                
                const player = new (window as any).YT.Player('yt-player', {
                    videoId: videoId,
                    playerVars: {
                        autoplay: 0,
                        controls: 0,  // Disable default controls to prevent speed manipulation
                        modestbranding: 1,
                        rel: 0,
                        fs: 0,  // Disable fullscreen
                        showinfo: 0,  // Hide video info
                    },
                    events: {
                        onStateChange: (event: any) => {
                            // 1 = PLAYING, 0 = ENDED, 2 = PAUSED, -1 = UNSTARTED
                            const isPlayerPlaying = event.data === (window as any).YT.PlayerState.PLAYING;
                            setIsPlaying(isPlayerPlaying);
                        },
                        onEnded: () => {
                            setProgress(100);
                            setIsPlaying(false);
                            onProgressCallback?.(100);
                            onEnded?.();
                        },
                    },
                });

                playerRef.current = player;
            }
        }, 100);

        return () => clearInterval(checkYT);
    }, [videoId, loadEmbed]);

    // Track progress only when video is actually playing
    useEffect(() => {
        if (!isPlaying || !playerRef.current) return;

        const updateProgress = () => {
            try {
                if (playerRef.current && playerRef.current.getCurrentTime) {
                    const current = playerRef.current.getCurrentTime();
                    const duration = playerRef.current.getDuration();
                    if (duration > 0) {
                        const played = (current / duration) * 100;
                        setProgress(Math.min(played, 100));
                        onProgressCallback?.(Math.min(played, 100));
                    }
                }
            } catch (e) {
                // Player not fully ready yet
            }
        };

        intervalRef.current = setInterval(updateProgress, 500);

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [isPlaying]);

    // For YouTube videos, use YouTube Iframe API
    if (videoId) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                    {!loadEmbed ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-gradient-to-br from-slate-900 to-slate-800 text-white px-4 text-center rounded-xl z-10">
                            <p className="text-sm text-white/85">Video is ready to load.</p>
                            <button
                                onClick={() => setLoadEmbed(true)}
                                className="px-4 py-2 rounded-lg bg-brand text-white text-sm font-semibold hover:bg-brand/90 transition-colors"
                            >
                                Load Video
                            </button>
                        </div>
                    ) : null}
                    <div 
                        id="yt-player"
                        className="w-full h-full"
                    />
                </div>
            </GlassCard>
        );
    }

    // Bypass faulty react-player TypeScript definitions
    const Player = ReactPlayer as any;

    // For non-YouTube URLs, use react-player with playback rate disabled
    return (
        <GlassCard className="p-0 overflow-hidden">
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                <Player
                    ref={playerRef}
                    url={url}
                    width="100%"
                    height="100%"
                    controls
                    playing={isPlaying}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onProgress={(state: any) => {
                        // Only update progress if playing
                        if (isPlaying) {
                            const played = state.played * 100;
                            setProgress(played);
                            onProgressCallback?.(played);
                        }
                    }}
                    onEnded={() => {
                        setProgress(100);
                        setIsPlaying(false);
                        onProgressCallback?.(100);
                        onEnded?.();
                    }}
                    progressInterval={500}
                    config={{
                        youtube: {
                            playerVars: {
                                modestbranding: 1,
                                rel: 0,
                                origin: window.location.origin,
                                fs: 0,
                                controls: 0,
                            },
                        },
                        file: {
                            attributes: {
                                controlsList: 'nodownload',
                                onContextMenu: (e: any) => e.preventDefault(),
                            },
                        },
                    }}
                />
            </div>
        </GlassCard>
    );
};
