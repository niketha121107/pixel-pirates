import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import { Eye, BookOpen, Lightbulb, Workflow } from 'lucide-react';

interface ExplanationSelectorProps {
    selected: string;
    onSelect: (value: string) => void;
}

export const ExplanationSelector = ({ selected, onSelect }: ExplanationSelectorProps) => {
    const options = [
        { id: 'visual', label: 'Visual', icon: Eye, color: 'text-purple-500', bg: 'bg-candy-lavender/50' },
        { id: 'simplified', label: 'Simplified', icon: BookOpen, color: 'text-emerald-500', bg: 'bg-candy-mint/50' },
        { id: 'logical', label: 'Logical', icon: Workflow, color: 'text-pink-500', bg: 'bg-candy-pink/50' },
        { id: 'analogy', label: 'Analogy', icon: Lightbulb, color: 'text-orange-500', bg: 'bg-candy-peach/50' },
    ];

    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {options.map((option) => {
                const isSelected = selected === option.id;
                return (
                    <button
                        key={option.id}
                        onClick={() => onSelect(option.id)}
                        className={cn(
                            "relative p-4 rounded-xl border transition-all text-left overflow-hidden group flex flex-col gap-3",
                            isSelected
                                ? "border-brand bg-brand/5 shadow-md"
                                : "border-pink-100 bg-white hover:border-pink-200 hover:bg-pink-50/30"
                        )}
                    >
                        {isSelected && (
                            <motion.div
                                layoutId="active-explanation"
                                className="absolute inset-0 bg-brand/10"
                            />
                        )}

                        <div className={cn("p-2 rounded-lg w-fit", option.bg)}>
                            <option.icon className={cn("w-5 h-5", option.color)} />
                        </div>

                        <span className={cn(
                            "relative z-10 font-semibold text-sm",
                            isSelected ? "text-gray-800" : "text-gray-500 group-hover:text-gray-700"
                        )}>
                            {option.label}
                        </span>
                    </button>
                );
            })}
        </div>
    );
};
