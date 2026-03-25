/**
 * Format seconds into human-readable time format
 * @param seconds - Total seconds to format
 * @returns Formatted time string (e.g., "5m 30s", "2h 15m", "45s")
 */
export const formatTime = (seconds: number): string => {
    if (seconds < 60) {
        return `${seconds}s`;
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }

    if (secs > 0) {
        return `${minutes}m ${secs}s`;
    }

    return `${minutes}m`;
};

/**
 * Format seconds for compact display
 * @param seconds - Total seconds to format
 * @returns Compact formatted time string (e.g., "5m 31s", "2h 15m")
 */
export const formatTimeCompact = (seconds: number): string => {
    return formatTime(seconds);
};

/**
 * Format seconds for detailed display
 * @param seconds - Total seconds to format
 * @returns Detailed formatted time string (e.g., "5 minutes 31 seconds")
 */
export const formatTimeDetailed = (seconds: number): string => {
    if (seconds < 60) {
        return `${seconds} second${seconds !== 1 ? 's' : ''}`;
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    const parts: string[] = [];

    if (hours > 0) {
        parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
    }

    if (minutes > 0) {
        parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
    }

    if (secs > 0) {
        parts.push(`${secs} second${secs !== 1 ? 's' : ''}`);
    }

    if (parts.length === 1) {
        return parts[0];
    }

    if (parts.length === 2) {
        return `${parts[0]} and ${parts[1]}`;
    }

    return `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`;
};

/**
 * Format seconds to HH:MM:SS format (required format without decimals)
 * @param seconds - Total seconds to format
 * @returns HH:MM:SS formatted string (e.g., "01:05:30", "00:00:14")
 */
export const formatTimeHHMMSS = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    const pad = (num: number) => String(num).padStart(2, '0');
    
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
};
