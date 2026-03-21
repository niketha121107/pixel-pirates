import { useState, useRef } from 'react';
import ReactPlayer from 'react-player';
import { GlassCard } from '../ui/GlassCard';

interface VideoTrackerUIProps {
    url: string;
    onProgress?: (played: number) => void;
    onEnded?: () => void;
}

export const VideoTrackerUI = ({ url, onProgress: onProgressCallback, onEnded }: VideoTrackerUIProps) => {
    const [progress, setProgress] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isReady, setIsReady] = useState(false);
    const [hasError, setHasError] = useState(false);
    const playerRef = useRef<any>(null);

    const Player = ReactPlayer as any;

    // Extract YouTube ID and convert to embed format
    const getEmbedUrl = (playerUrl: string) => {
        if (!playerUrl) return '';
        
        // Extract video ID from various YouTube URL formats
        let videoId = '';
        
        if (playerUrl.includes('youtube.com/watch')) {
            const match = playerUrl.match(/v=([a-zA-Z0-9_-]{11})/);
            videoId = match ? match[1] : '';
        } else if (playerUrl.includes('youtu.be/')) {
            const match = playerUrl.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
            videoId = match ? match[1] : '';
        } else if (playerUrl.includes('youtube.com/embed/')) {
            const match = playerUrl.match(/embed\/([a-zA-Z0-9_-]{11})/);
            videoId = match ? match[1] : '';
        } else if (/^[a-zA-Z0-9_-]{11}$/.test(playerUrl)) {
            // Direct video ID
            videoId = playerUrl;
        }
        
        if (!videoId) return playerUrl;
        
        // Use embed format which is more reliable
        return `https://www.youtube.com/embed/${videoId}?enablejsapi=1`;
    };

    const embedUrl = getEmbedUrl(url);

    const handleProgress = (state: any) => {
        const played = (state.played * 100);
        setProgress(Math.min(played, 100));
        onProgressCallback?.(Math.min(played, 100));
    };

    const handleEnded = () => {
        setProgress(100);
        setIsPlaying(false);
        onProgressCallback?.(100);
        onEnded?.();
    };

    const handleError = (error: any) => {
        console.error('❌ Video player error:', error);
        console.error('URL attempted:', embedUrl);
        setHasError(true);
        setIsReady(true);
    };

    if (hasError) {
        return (
            <GlassCard className="p-0 overflow-hidden">
                <div className="relative aspect-video bg-gray-900 rounded-xl overflow-hidden flex items-center justify-center">
                    <div className="text-center text-white">
                        <p className="text-sm mb-2">⚠️ Video cannot be loaded</p>
                        <p className="text-xs text-gray-400">YouTube video may not be available in your region</p>
                    </div>
                </div>
            </GlassCard>
        );
    }

    return (
        <GlassCard className="p-0 overflow-hidden">
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                {!isReady && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/90 z-10">
                        <div className="text-white text-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-3" />
                            <p className="text-sm">Loading video...</p>
                        </div>
                    </div>
                )}
                <Player
                    ref={playerRef}
                    url={embedUrl}
                    width="100%"
                    height="100%"
                    controls={true}
                    playing={isPlaying}
                    onReady={() => {
                        console.log('✅ Video ready');
                        setIsReady(true);
                    }}
                    onPlay={() => {
                        console.log('▶ Playing');
                        setIsPlaying(true);
                    }}
                    onPause={() => {
                        console.log('⏸ Paused');
                        setIsPlaying(false);
                    }}
                    onProgress={handleProgress}
                    onEnded={handleEnded}
                    onError={handleError}
                    progressInterval={500}
                    config={{
                        youtube: {
                            playerVars: {
                                autoplay: 0,
                                controls: 1,
                                modestbranding: 1,
                                rel: 0,
                                fs: 1,
                                iv_load_policy: 3,
                                allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
                            },
                        },
                        file: {
                            attributes: {
                                controlsList: 'nodownload',
                                allowFullScreen: true,
                                crossOrigin: 'anonymous',
                            },
                        },
                    }}
                />
            </div>
        </GlassCard>
    );
};
