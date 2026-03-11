import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { InputField } from '../components/ui/InputField';
import { ArrowRight, Mail, Lock, Brain, Globe, Target, Rocket } from 'lucide-react';
import { motion } from 'framer-motion';

const FEATURES = [
    { icon: Brain, title: 'Smart Learning', desc: 'Adapts to your style — visual, logical, simplified, or analogy-based.', color: 'text-purple-500', bg: 'bg-purple-50' },
    { icon: Globe, title: '8 Languages', desc: 'Tamil, Hindi, German, French, Malayalam, Kannada, Telugu & English.', color: 'text-blue-500', bg: 'bg-blue-50' },
    { icon: Target, title: 'Adaptive Quizzes', desc: 'Difficulty adjusts to your performance — always in your growth zone.', color: 'text-rose-500', bg: 'bg-rose-50' },
    { icon: Rocket, title: 'All-in-One', desc: 'Curated videos, notes, PDFs & mock tests — everything you need.', color: 'text-amber-500', bg: 'bg-amber-50' },
];

export const SignIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { login, backendError } = useAuth();

    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        const success = await login(email, password);
        setIsLoading(false);
        if (success) {
            navigate('/profile');
        } else {
            setError(backendError
                ? 'Cannot connect to server. Please make sure the backend is running (cd backend && python main.py)'
                : 'Invalid email or password');
        }
    };

    return (
        <div className="min-h-screen w-full flex flex-col lg:flex-row overflow-auto">
            {/* Left panel — branding + features */}
            <div className="lg:w-1/2 w-full relative flex flex-col justify-center px-8 sm:px-14 lg:px-16 py-12 lg:py-0" style={{ background: 'linear-gradient(135deg, #fce4ec 0%, #fdf2f8 50%, #fce7f3 100%)' }}>
                {/* Decorative circles */}
                <div className="absolute top-10 left-10 w-48 h-48 bg-pink-200/30 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute bottom-16 right-10 w-64 h-64 bg-rose-200/20 rounded-full blur-3xl pointer-events-none" />

                <motion.div
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6 }}
                    className="relative z-10 max-w-lg mx-auto lg:mx-0 select-none"
                >
                    <Link to="/" className="inline-block mb-6">
                        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-pink-600 via-rose-500 to-orange-500 bg-clip-text text-transparent">
                            EduTwin
                        </h1>
                    </Link>
                    <p className="text-gray-700 text-lg sm:text-xl font-medium leading-relaxed mb-10">
                        Your AI-powered adaptive learning companion.<br />
                        <span className="text-gray-500 text-base">Master any topic, your way.</span>
                    </p>
 
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {FEATURES.map((f, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
                                className="flex items-start gap-3 bg-white/60 backdrop-blur-sm rounded-xl p-4 hover:bg-white/80 transition-colors shadow-sm cursor-default"
                            >
                                <div className="w-9 h-9 rounded-lg bg-pink-100 flex items-center justify-center flex-shrink-0">
                                    <f.icon className="w-5 h-5 text-rose-500" />
                                </div>
                                <div>
                                    <h3 className="text-gray-800 font-bold text-sm">{f.title}</h3>
                                    <p className="text-gray-500 text-xs leading-relaxed mt-0.5">{f.desc}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    <p className="mt-10 text-gray-400 text-xs">
                        Built with 💗 by <span className="text-gray-600 font-semibold">Pixel Pirates</span>
                    </p>
                </motion.div>
            </div>

            {/* Right panel — login form */}
            <div className="lg:w-1/2 w-full flex items-center justify-center px-6 sm:px-12 py-12 lg:py-0" style={{ background: 'linear-gradient(135deg, #fce4ec 0%, #fdf2f8 50%, #fce7f3 100%)' }}>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2, type: 'spring' }}
                    className="w-full max-w-md"
                >
                    <div className="mb-10">
                        <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
                            Welcome Back
                        </h2>
                        <p className="text-gray-500 mt-2">Sign in to continue your learning journey.</p>
                    </div>

                    <GlassCard className="p-8 shadow-xl shadow-pink-200/30">
                        <form onSubmit={handleSignIn} className="space-y-6">
                            <InputField
                                type="email"
                                required
                                placeholder="name@email.com"
                                label="Email Address"   
                                icon={<Mail className="w-5 h-5" />}
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />

                            <InputField
                                type="password"
                                required
                                placeholder="••••••••"
                                label="Password"
                                icon={<Lock className="w-5 h-5" />}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />

                            {error && (
                                <p className="text-sm text-red-500 text-center">{error}</p>
                            )}

                            <div className="pt-2">
                                <GradientButton type="submit" fullWidth className="group" disabled={isLoading}>
                                    {isLoading ? 'Signing in...' : 'Log In'}
                                    {!isLoading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
                                </GradientButton>
                            </div>
                        </form>

                        <div className="mt-8 text-center">
                            <p className="text-sm text-gray-500">
                                Don't have an account?{' '}
                                <Link to="/signup" className="text-brand font-semibold hover:text-brand-dark transition-colors">
                                    Sign up
                                </Link>
                            </p>
                        </div>
                    </GlassCard>
                </motion.div>
            </div>
        </div>
    );
};
