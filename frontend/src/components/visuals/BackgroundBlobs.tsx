import { useUserPreferences } from '../../context/UserPreferencesContext';

export const BackgroundBlobs = () => {
    const { preferences } = useUserPreferences();
    const { wallpaper } = preferences;
    const blobColors = wallpaper.blobColors;
    const hasImage = !!wallpaper.imageUrl;

    // For full-screen display, request a larger image from Unsplash
    const fullScreenUrl = wallpaper.imageUrl
        ? wallpaper.imageUrl.replace(/[?&]w=\d+/, '?w=1920').replace(/[?&]h=\d+/, '&h=1080')
        : undefined;

    return (
        <div
            className="fixed inset-0 overflow-hidden pointer-events-none -z-10 transition-all duration-700"
            style={{ background: hasImage ? undefined : wallpaper.gradient }}
        >
            {/* Full-screen wallpaper image for aesthetic themes */}
            {hasImage && fullScreenUrl && (
                <img
                    src={fullScreenUrl}
                    alt=""
                    className="absolute inset-0 w-full h-full object-cover"
                />
            )}

            {/* Blobs only shown for non-image wallpapers */}
            {!hasImage && (
                <>
                    <div className={`absolute top-[-20%] left-[-10%] w-[50%] h-[50%] ${blobColors[0] || 'bg-pink-200/40'} rounded-full blur-[120px] animate-blob`} />
                    <div className={`absolute top-[30%] right-[-20%] w-[60%] h-[60%] ${blobColors[1] || 'bg-orange-200/30'} rounded-full blur-[150px] animate-blob animation-delay-2000`} />
                    <div className={`absolute bottom-[-20%] left-[20%] w-[70%] h-[70%] ${blobColors[2] || 'bg-emerald-200/25'} rounded-full blur-[130px] animate-blob animation-delay-4000`} />
                </>
            )}
        </div>
    );
};
