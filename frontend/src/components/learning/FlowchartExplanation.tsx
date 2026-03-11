import { motion } from 'framer-motion';
import { ArrowDown, Circle, Diamond, Square, PlayCircle, StopCircle, RotateCcw, Zap, CheckCircle2 } from 'lucide-react';

export interface FlowchartNode {
    id: string;
    type: 'start' | 'process' | 'decision' | 'end' | 'io';
    label: string;
    detail?: string;
    yes?: string;   // for decision nodes — target id or inline text
    no?: string;     // for decision nodes — target id or inline text
}

interface FlowchartExplanationProps {
    nodes: FlowchartNode[];
    title?: string;
}

const nodeIcon = (type: FlowchartNode['type']) => {
    switch (type) {
        case 'start':
            return <PlayCircle className="w-4 h-4" />;
        case 'end':
            return <StopCircle className="w-4 h-4" />;
        case 'decision':
            return <Diamond className="w-4 h-4" />;
        case 'io':
            return <Zap className="w-4 h-4" />;
        default:
            return <Square className="w-4 h-4" />;
    }
};

const nodeColors = (type: FlowchartNode['type']) => {
    switch (type) {
        case 'start':
            return {
                bg: 'bg-emerald-50',
                border: 'border-emerald-300',
                text: 'text-emerald-700',
                icon: 'text-emerald-500',
                glow: 'shadow-emerald-100',
            };
        case 'end':
            return {
                bg: 'bg-rose-50',
                border: 'border-rose-300',
                text: 'text-rose-700',
                icon: 'text-rose-500',
                glow: 'shadow-rose-100',
            };
        case 'decision':
            return {
                bg: 'bg-amber-50',
                border: 'border-amber-300',
                text: 'text-amber-700',
                icon: 'text-amber-500',
                glow: 'shadow-amber-100',
            };
        case 'io':
            return {
                bg: 'bg-blue-50',
                border: 'border-blue-300',
                text: 'text-blue-700',
                icon: 'text-blue-500',
                glow: 'shadow-blue-100',
            };
        default:
            return {
                bg: 'bg-purple-50',
                border: 'border-purple-300',
                text: 'text-purple-700',
                icon: 'text-purple-500',
                glow: 'shadow-purple-100',
            };
    }
};

const nodeShape = (type: FlowchartNode['type']) => {
    switch (type) {
        case 'start':
        case 'end':
            return 'rounded-full';
        case 'decision':
            return 'rounded-xl rotate-0'; // we'll style the diamond via inner content
        default:
            return 'rounded-xl';
    }
};

export const FlowchartExplanation = ({ nodes, title }: FlowchartExplanationProps) => {
    if (!nodes || nodes.length === 0) return null;

    return (
        <div className="space-y-2">
            {title && (
                <p className="text-sm text-gray-500 mb-4 flex items-center gap-2">
                    <RotateCcw className="w-4 h-4 text-purple-400" />
                    {title}
                </p>
            )}

            <div className="flex flex-col items-center gap-0">
                {nodes.map((node, i) => {
                    const colors = nodeColors(node.type);
                    const shape = nodeShape(node.type);
                    const isDecision = node.type === 'decision';

                    return (
                        <div key={node.id} className="flex flex-col items-center w-full">
                            {/* Connector arrow (skip for first node) */}
                            {i > 0 && (
                                <motion.div
                                    initial={{ scaleY: 0 }}
                                    animate={{ scaleY: 1 }}
                                    transition={{ delay: i * 0.08, duration: 0.2 }}
                                    className="flex flex-col items-center"
                                >
                                    <div className="w-0.5 h-6 bg-gradient-to-b from-gray-300 to-gray-400" />
                                    <ArrowDown className="w-4 h-4 text-gray-400 -mt-1" />
                                </motion.div>
                            )}

                            {/* Node */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.85, y: 10 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                transition={{ delay: i * 0.1, duration: 0.35, type: 'spring', bounce: 0.3 }}
                                className={`
                                    relative flex items-center gap-3 px-5 py-3
                                    border-2 ${colors.border} ${colors.bg} ${shape}
                                    shadow-md ${colors.glow} 
                                    ${isDecision ? 'min-w-[240px] max-w-[380px]' : 'min-w-[200px] max-w-[420px]'}
                                    transition-shadow hover:shadow-lg
                                `}
                            >
                                {/* Diamond indicator for decision */}
                                {isDecision && (
                                    <div className="absolute -top-2.5 left-1/2 -translate-x-1/2">
                                        <div className={`w-5 h-5 ${colors.bg} border-2 ${colors.border} rotate-45 rounded-sm`} />
                                    </div>
                                )}

                                <div className={`flex-shrink-0 p-1.5 rounded-lg ${colors.bg} ${colors.icon}`}>
                                    {nodeIcon(node.type)}
                                </div>

                                <div className="flex-1 min-w-0">
                                    <p className={`text-sm font-semibold ${colors.text} leading-tight`}>
                                        {node.label}
                                    </p>
                                    {node.detail && (
                                        <p className="text-xs text-gray-500 mt-0.5 leading-snug">
                                            {node.detail}
                                        </p>
                                    )}
                                </div>

                                {/* Step number badge */}
                                <div className={`absolute -right-2 -top-2 w-5 h-5 rounded-full ${colors.bg} border ${colors.border} flex items-center justify-center`}>
                                    <span className={`text-[10px] font-bold ${colors.icon}`}>{i + 1}</span>
                                </div>
                            </motion.div>

                            {/* Decision branches */}
                            {isDecision && (node.yes || node.no) && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: i * 0.1 + 0.15 }}
                                    className="flex items-start gap-4 mt-2"
                                >
                                    {node.yes && (
                                        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200">
                                            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                                            <span className="text-xs font-medium text-emerald-700">Yes: {node.yes}</span>
                                        </div>
                                    )}
                                    {node.no && (
                                        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-50 border border-rose-200">
                                            <Circle className="w-3 h-3 text-rose-500" />
                                            <span className="text-xs font-medium text-rose-700">No: {node.no}</span>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
