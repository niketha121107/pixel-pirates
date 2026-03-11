import type { ReactNode } from 'react';
import { BackgroundBlobs } from '../visuals/BackgroundBlobs';

interface PageWrapperProps {
    children: ReactNode;
    className?: string;
    withPadding?: boolean;
}

export const PageWrapper = ({ children, className = '', withPadding = true }: PageWrapperProps) => {
    return (
        <div className={`h-screen overflow-hidden relative flex flex-col ${className}`}>
            <BackgroundBlobs />
            <main className={`flex-1 overflow-y-auto z-10 ${withPadding ? 'pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full' : ''}`}>
                {children}
            </main>
        </div>
    );
};
