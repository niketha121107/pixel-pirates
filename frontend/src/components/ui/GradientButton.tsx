import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';

interface GradientButtonProps extends HTMLMotionProps<"button"> {
    children: React.ReactNode;
    className?: string;
    variant?: 'primary' | 'secondary' | 'outline';
    fullWidth?: boolean;
}

export const GradientButton = ({
    children,
    className = '',
    variant = 'primary',
    fullWidth = false,
    ...props
}: GradientButtonProps) => {

    const baseStyles = "relative group overflow-hidden rounded-xl px-6 py-3 font-semibold transition-all inline-flex items-center justify-center gap-2";
    const widthStyle = fullWidth ? "w-full" : "";

    const variants = {
        primary: "bg-gradient-brand text-white shadow-md hover:shadow-lg border border-brand/20",
        secondary: "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200",
        outline: "bg-transparent text-brand border border-brand/50 hover:border-brand hover:bg-brand/5"
    };

    return (
        <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={cn(baseStyles, variants[variant], widthStyle, className)}
            {...props}
        >
            {variant === 'primary' && (
                <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            )}
            <span className="relative z-10 flex items-center gap-2">{children}</span>
        </motion.button>
    );
};
