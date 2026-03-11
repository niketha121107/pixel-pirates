import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
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
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { signup, backendError } = useAuth();

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        const result = await signup(name, email, password);
        setIsLoading(false);
        if (result === true) {
            navigate('/profile');
        } else if (result === 'email_exists') {
            setError('This email is already registered. Please log in instead.');
        } else {
            setError(backendError
                ? 'Cannot connect to server. Please make sure the backend is running (cd backend && python main.py)'
                : 'Signup failed. Please try again later.');
        }
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

                        {error && (
                            <p className="text-sm text-red-500 text-center">{error}</p>
                        )}

                        <div className="pt-4">
                            <GradientButton type="submit" fullWidth className="group" disabled={isLoading}>
                                {isLoading ? 'Creating account...' : 'Create Account'}
                                {!isLoading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
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
