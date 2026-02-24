import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { InputField } from '../components/ui/InputField';
import { ArrowRight, Mail, Lock } from 'lucide-react';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';

export const SignIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSignIn = (e: React.FormEvent) => {
        e.preventDefault();
        navigate('/dashboard'); // No auth logic required
    };

    return (
        <PageWrapper className="justify-center items-center" withPadding={false}>
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
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">Welcome Back</h1>
                    <p className="text-gray-500 text-sm">Sign in to continue your adaptive coding journey.</p>
                </div>

                <GlassCard className="p-8">
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

                        <div className="pt-2">
                            <GradientButton type="submit" fullWidth className="group">
                                Log In
                                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </GradientButton>
                        </div>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-500">
                            Don't have an account?{' '}
                            <Link to="/signup" className="text-brand font-medium hover:text-brand-dark transition-colors">
                                Sign up
                            </Link>
                        </p>
                    </div>
                </GlassCard>
            </motion.div>
        </PageWrapper>
    );
};
