import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

export default function SignIn() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const validate = (): boolean => {
        const e: Record<string, string> = {};
        if (!email.trim()) e.email = 'Email is required';
        else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Enter a valid email';
        if (!password) e.password = 'Password is required';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!validate()) return;
        setLoading(true);
        await new Promise(r => setTimeout(r, 800));
        const ok = login(email, password);
        if (ok) navigate('/dashboard');
        else {
            setLoading(false);
            setErrors({ email: 'Invalid credentials' });
        }
    };

    return (
        <div className="min-h-screen bg-surface flex items-center justify-center p-4">
            <div className="w-full max-w-5xl h-[80vh] min-h-[600px] bg-white rounded-3xl overflow-hidden shadow-[0_20px_50px_rgba(8,112,184,0.07)] flex flex-col md:flex-row-reverse border border-slate-100 relative z-10">

                {/* Right Panel - Brand / Graphic */}
                <div className="hidden md:flex flex-col justify-between w-1/2 bg-slate-900 p-12 text-white relative overflow-hidden">
                    <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
                    <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-primary rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-blob" />
                    <div className="absolute -top-24 -left-24 w-96 h-96 bg-accent rounded-full mix-blend-screen filter blur-3xl opacity-30 animate-blob animation-delay-2000" />

                    <div className="relative z-10 flex justify-end">
                        <Link to="/dashboard" className="inline-flex items-center gap-2 group mb-12">
                            <span className="text-2xl font-bold text-white font-display tracking-tight">
                                EduTwin
                            </span>
                            <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center shadow-lg border border-white/20">
                                <span className="text-white font-bold text-sm tracking-wider font-display">ET</span>
                            </div>
                        </Link>
                    </div>

                    <div className="relative z-10">
                        <h1 className="text-4xl lg:text-5xl font-bold font-display leading-tight mb-4">
                            Welcome back.
                        </h1>
                        <p className="text-slate-400 text-lg">
                            Pick up right where you left off. The leaderboard awaits.
                        </p>
                    </div>
                </div>

                {/* Left Panel - Form */}
                <div className="w-full md:w-1/2 p-6 sm:p-10 md:p-12 lg:p-16 flex flex-col justify-center bg-white order-2 md:order-none shrink-0 border-r border-slate-100">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                        className="w-full max-w-md mx-auto"
                    >
                        <div className="md:hidden text-center mb-8">
                            <span className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-display tracking-tight">
                                EduTwin
                            </span>
                        </div>

                        <h2 className="text-3xl font-bold text-slate-800 font-display mb-2">Sign In</h2>
                        <p className="text-slate-500 mb-8 font-medium">Please enter your details to sign in.</p>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">Email</label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                    placeholder="alex@example.com"
                                    className={`w-full px-4 py-3 rounded-xl border text-sm transition-all duration-300 outline-none
                    ${errors.email
                                            ? 'border-danger/60 bg-danger/5 focus:border-danger focus:ring-4 focus:ring-danger/10'
                                            : 'border-slate-200 bg-slate-50/50 focus:border-primary focus:bg-white focus:ring-4 focus:ring-primary/10 hover:border-slate-300'}`}
                                />
                                {errors.email && <p className="text-danger text-xs mt-1.5 font-medium">{errors.email}</p>}
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">Password</label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className={`w-full px-4 py-3 rounded-xl border text-sm transition-all duration-300 outline-none
                    ${errors.password
                                            ? 'border-danger/60 bg-danger/5 focus:border-danger focus:ring-4 focus:ring-danger/10'
                                            : 'border-slate-200 bg-slate-50/50 focus:border-primary focus:bg-white focus:ring-4 focus:ring-primary/10 hover:border-slate-300'}`}
                                />
                                {errors.password && <p className="text-danger text-xs mt-1.5 font-medium">{errors.password}</p>}
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.01, translateY: -2 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading}
                                className="w-full py-3.5 mt-4 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold text-sm shadow-[0_10px_20px_rgba(79,70,229,0.25)] hover:shadow-[0_15px_30px_rgba(79,70,229,0.35)] transition-all duration-300 disabled:opacity-70 disabled:hover:translate-y-0 cursor-pointer"
                            >
                                {loading ? (
                                    <span className="inline-flex items-center gap-2">
                                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" /></svg>
                                        Signing in...
                                    </span>
                                ) : 'Log In'}
                            </motion.button>
                        </form>

                        <p className="text-center text-sm font-medium text-slate-500 mt-8">
                            Don't have an account?{' '}
                            <Link to="/signup" className="text-primary font-semibold hover:text-primary-dark transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
