import { cn } from '../../lib/utils';
import { GlassCard } from './GlassCard';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: {
        value: string;
        isPositive: boolean;
    };
    className?: string;
}

export const StatCard = ({ title, value, icon, trend, className }: StatCardProps) => {
    return (
        <GlassCard className={cn("flex flex-col gap-4 p-5", className)}>
            <div className="flex items-start justify-between">
                <div className="p-3 bg-brand/10 rounded-xl text-brand">
                    {icon}
                </div>
                {trend && (
                    <div className={cn(
                        "text-xs font-medium px-2.5 py-1 rounded-full",
                        trend.isPositive ? "bg-status-success/10 text-status-success" : "bg-status-error/10 text-status-error"
                    )}>
                        {trend.isPositive ? '+' : '-'}{trend.value}
                    </div>
                )}
            </div>

            <div>
                <h3 className="text-sm text-gray-500 font-medium">{title}</h3>
                <p className="text-3xl font-bold mt-1 text-gray-800">{value}</p>
            </div>
        </GlassCard>
    );
};
