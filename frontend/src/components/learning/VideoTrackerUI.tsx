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
    const playerRef = useRef<any>(null);

    const Player = ReactPlayer as any;

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
                    url={url}
                    width="100%"
                    height="100%"
                    controls={true}
                    playing={isPlaying}
                    onReady={() => setIsReady(true)}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onProgress={handleProgress}
                    onEnded={handleEnded}
                    onError={(error: any) => {
                        console.error('Video player error:', error);
                        setIsReady(true);
                    }}
                    progressInterval={500}
                    config={{
                        youtube: {
                            playerVars: {
                                autoplay: 0,
                                controls: 1,
                                modestbranding: 1,
                                rel: 0,
                                fs: 1,
                                iv_load_policy: 3,  // Hide annotations
                            },
                        },
                        file: {
                            attributes: {
                                controlsList: 'nodownload',
                                crossOrigin: 'anonymous',
                            },
                        },
                    }}
                />
            </div>
        </GlassCard>
    );
};
