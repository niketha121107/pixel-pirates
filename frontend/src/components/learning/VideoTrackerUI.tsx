import { useState } from 'react';
import ReactPlayer from 'react-player';
import { GlassCard } from '../ui/GlassCard';
import { Play, Pause, Volume2, Maximize } from 'lucide-react';

interface VideoTrackerUIProps {
    url: string;
    onProgress?: (played: number) => void;
    onEnded?: () => void;
}

export const VideoTrackerUI = ({ url, onProgress: onProgressCallback, onEnded }: VideoTrackerUIProps) => {
    const [playing, setPlaying] = useState(false);
    const [progress, setProgress] = useState(0);

    // Bypass faulty react-player TypeScript definitions
    const Player = ReactPlayer as any;

    const togglePlay = () => setPlaying(!playing);

    return (
        <GlassCard className="p-0 overflow-hidden group">
            <div className="relative aspect-video bg-black rounded-xl overflow-hidden">
                <Player
                    url={url}
                    width="100%"
                    height="100%"
                    playing={playing}
                    onProgress={(state: any) => {
                        setProgress(state.played * 100);
                        onProgressCallback?.(state.played * 100);
                    }}
                    onEnded={onEnded}
                    controls={false}
                    style={{ opacity: 0.9 }}
                />

                {/* Playback overlay UI */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={togglePlay}
                            className="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center hover:bg-brand-light hover:scale-105 transition-all shadow-glow"
                        >
                            {playing ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-1" />}
                        </button>

                        <div className="flex-1">
                            <div className="w-full h-1.5 bg-white/20 rounded-full overflow-hidden cursor-pointer">
                                <div
                                    className="h-full bg-brand-light rounded-full relative"
                                    style={{ width: `${progress}%` }}
                                >
                                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3 text-white">
                            <button className="hover:text-brand-light transition-colors"><Volume2 className="w-5 h-5" /></button>
                            <button className="hover:text-brand-light transition-colors"><Maximize className="w-5 h-5" /></button>
                        </div>
                    </div>
                </div>
            </div>
        </GlassCard>
    );
};
