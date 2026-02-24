import { forwardRef } from 'react';
import type { InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

interface InputFieldProps extends InputHTMLAttributes<HTMLInputElement> {
    icon?: React.ReactNode;
    label?: string;
    error?: string;
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
    ({ className, icon, label, error, ...props }, ref) => {
        return (
            <div className="w-full space-y-2">
                {label && (
                    <label className="text-sm font-medium text-gray-600 ml-1">
                        {label}
                    </label>
                )}
                <div className="relative group">
                    {icon && (
                        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-brand transition-colors z-10">
                            {icon}
                        </div>
                    )}

                    <input
                        ref={ref}
                        className={cn(
                            "w-full bg-pink-50/30 border border-pink-100 rounded-xl py-3 px-4 text-gray-800",
                            "placeholder:text-gray-400 transition-all z-20 relative",
                            "focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand focus:bg-white",
                            icon && "pl-11",
                            error && "border-status-error focus:border-status-error focus:ring-status-error",
                            className
                        )}
                        {...props}
                    />
                </div>

                {error && (
                    <motion.p
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-xs text-status-error ml-1"
                    >
                        {error}
                    </motion.p>
                )}
            </div>
        );
    }
);
InputField.displayName = "InputField";
