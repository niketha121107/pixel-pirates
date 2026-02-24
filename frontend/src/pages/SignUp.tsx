<<<<<<< HEAD
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { InputField } from '../components/ui/InputField';
import { ArrowRight, Mail, Lock, User } from 'lucide-react';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';

export const SignUp = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignUp = (e: React.FormEvent) => {
        e.preventDefault();
        navigate('/dashboard'); // No auth logic required
    };

    return (
        <PageWrapper className="justify-center items-center py-12" withPadding={false}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, type: 'spring' }}
                className="w-full max-w-md p-4"
            >
                <div className="text-center mb-10">
                    <Link to="/" className="text-4xl font-bold tracking-tighter inline-block mb-4">
                        <span className="text-gradient">EduTwin</span>
                    </Link>
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">Create an Account</h1>
                    <p className="text-gray-500 text-sm">Join the next generation of coding education.</p>
                </div>

                <GlassCard className="p-8">
                    <form onSubmit={handleSignUp} className="space-y-5">
                        <InputField
                            type="text"
                            required
                            placeholder="John Doe"
                            label="Full Name"
                            icon={<User className="w-5 h-5" />}
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />

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

                        <div className="pt-4">
                            <GradientButton type="submit" fullWidth className="group">
                                Create Account
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </GradientButton>
                        </div>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-500">
                            Already have an account?{' '}
                            <Link to="/signin" className="text-brand font-medium hover:text-brand-dark transition-colors">
                                Log in
                            </Link>
                        </p>
                    </div>
                </GlassCard>
            </motion.div>
        </PageWrapper>
    );
};
=======
import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

export default function SignUp() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const validate = (): boolean => {
        const e: Record<string, string> = {};
        if (!name.trim()) e.name = 'Full name is required';
        if (!email.trim()) e.email = 'Email is required';
        else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Enter a valid email';
        if (!password) e.password = 'Password is required';
        else if (password.length < 6) e.password = 'Password must be at least 6 characters';
        if (password !== confirmPassword) e.confirmPassword = 'Passwords do not match';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!validate()) return;
        setLoading(true);
        await new Promise(r => setTimeout(r, 800));
        signup(name, email, password);
        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen bg-surface flex items-center justify-center p-4">
            <div className="w-full max-w-5xl h-[80vh] min-h-[600px] bg-white rounded-3xl overflow-hidden shadow-[0_20px_50px_rgba(8,112,184,0.07)] flex flex-col md:flex-row border border-slate-100 relative z-10">

                {/* Left Panel - Brand / Graphic */}
                <div className="hidden md:flex flex-col justify-between w-1/2 bg-gradient-to-br from-primary-dark via-primary to-accent p-12 text-white relative overflow-hidden">
                    <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
                    <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-accent-light rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob" />
                    <div className="absolute -top-24 -right-24 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000" />

                    <div className="relative z-10">
                        <Link to="/dashboard" className="inline-flex items-center gap-2 group mb-12">
                            <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center shadow-lg border border-white/20">
                                <span className="text-white font-bold text-sm tracking-wider font-display">ET</span>
                            </div>
                            <span className="text-2xl font-bold text-white font-display tracking-tight">
                                EduTwin
                            </span>
                        </Link>

                        <h1 className="text-4xl lg:text-5xl font-bold font-display leading-tight mb-4">
                            Start your <br />learning journey.
                        </h1>
                        <p className="text-white/80 text-lg">
                            Master complex concepts with personalized, adaptive explanations.
                        </p>
                    </div>

                    <div className="relative z-10">
                        <div className="flex -space-x-3 mb-4">
                            <div className="w-10 h-10 rounded-full border-2 border-primary-dark bg-indigo-200 flex items-center justify-center text-xs font-bold text-indigo-700">SC</div>
                            <div className="w-10 h-10 rounded-full border-2 border-primary-dark bg-cyan-200 flex items-center justify-center text-xs font-bold text-cyan-700">RP</div>
                            <div className="w-10 h-10 rounded-full border-2 border-primary-dark bg-fuchsia-200 flex items-center justify-center text-xs font-bold text-fuchsia-700">MG</div>
                        </div>
                        <p className="text-white/70 text-sm font-medium">Join 10,000+ developers learning smarter.</p>
                    </div>
                </div>

                {/* Right Panel - Form */}
                <div className="w-full md:w-1/2 p-8 md:p-12 lg:p-16 flex flex-col justify-center bg-white">
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                        className="w-full max-w-md mx-auto"
                    >
                        <div className="md:hidden text-center mb-8">
                            <span className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent font-display tracking-tight">
                                EduTwin
                            </span>
                        </div>

                        <h2 className="text-3xl font-bold text-slate-800 font-display mb-2">Create Account</h2>
                        <p className="text-slate-500 mb-8 font-medium">Please enter your details to sign up.</p>

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <Field label="Full Name" value={name} onChange={setName} error={errors.name} placeholder="Alex Johnson" />
                            <Field label="Email" type="email" value={email} onChange={setEmail} error={errors.email} placeholder="alex@example.com" />
                            <div className="grid grid-cols-2 gap-4">
                                <Field label="Password" type="password" value={password} onChange={setPassword} error={errors.password} placeholder="••••••••" />
                                <Field label="Confirm" type="password" value={confirmPassword} onChange={setConfirmPassword} error={errors.confirmPassword} placeholder="••••••••" />
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.01, translateY: -2 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading}
                                className="w-full py-3.5 mt-4 rounded-xl bg-slate-900 text-white font-semibold text-sm shadow-[0_10px_20px_rgba(15,23,42,0.15)] hover:shadow-[0_15px_30px_rgba(15,23,42,0.25)] hover:bg-slate-800 transition-all duration-300 disabled:opacity-70 disabled:hover:translate-y-0 cursor-pointer"
                            >
                                {loading ? (
                                    <span className="inline-flex items-center gap-2">
                                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z" /></svg>
                                        Creating account...
                                    </span>
                                ) : 'Create Account'}
                            </motion.button>
                        </form>

                        <p className="text-center text-sm font-medium text-slate-500 mt-8">
                            Already have an account?{' '}
                            <Link to="/signin" className="text-primary font-semibold hover:text-primary-dark transition-colors">
                                Sign in
                            </Link>
                        </p>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}

function Field({ label, type = 'text', value, onChange, error, placeholder }: {
    label: string; type?: string; value: string; onChange: (v: string) => void; error?: string; placeholder?: string;
}) {
    return (
        <div>
            <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider mb-2">{label}</label>
            <input
                type={type}
                value={value}
                onChange={e => onChange(e.target.value)}
                placeholder={placeholder}
                className={`w-full px-4 py-3 rounded-xl border text-sm transition-all duration-300 outline-none
          ${error
                        ? 'border-danger/60 bg-danger/5 focus:border-danger focus:ring-4 focus:ring-danger/10'
                        : 'border-slate-200 bg-slate-50/50 focus:border-primary focus:bg-white focus:ring-4 focus:ring-primary/10 hover:border-slate-300'}`}
            />
            {error && <p className="text-danger text-xs mt-1.5 font-medium">{error}</p>}
        </div>
    );
}
>>>>>>> fff541230f2ea326096f9f7bf3bb0b31c06d86a8
