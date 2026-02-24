import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import type { HTMLMotionProps } from 'framer-motion';

interface GlassCardProps extends HTMLMotionProps<"div"> {
    children: ReactNode;
    className?: string;
    interactive?: boolean;
}

export const GlassCard = ({ children, className = '', interactive = false, ...props }: GlassCardProps) => {
    return (
        <motion.div
            whileHover={interactive ? { y: -4, scale: 1.01 } : {}}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            className={cn(
                "bg-white backdrop-blur-xl border border-pink-100 rounded-2xl shadow-sm relative overflow-hidden",
                interactive && "hover:border-brand/30 hover:shadow-md transition-all cursor-pointer group",
                className
            )}
            {...props}
        >
            <div className="relative z-10">{children}</div>
        </motion.div>
    );
};
