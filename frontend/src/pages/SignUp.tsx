import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useUserPreferences } from '../context/UserPreferencesContext';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { InputField } from '../components/ui/InputField';
import { LanguageSelector } from '../components/LanguageSelector';
import { ArrowRight, Mail, Lock, User, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { getTranslation } from '../lib/translations';

export const SignUp = () => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isLanguageSelectorOpen, setIsLanguageSelectorOpen] = useState(false);
    const navigate = useNavigate();
    const { signup, backendError } = useAuth();
    const { preferences, setLanguage } = useUserPreferences();
    const language = preferences.language;

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        const result = await signup(name, email, password);
        setIsLoading(false);
        if (result === true) {
            navigate('/dashboard');
        } else if (result === 'email_exists') {
            setError(getTranslation(language, 'email_exists') || 'This email is already registered. Please log in instead.');
        } else {
            setError(backendError
                ? getTranslation(language, 'server_error')
                : getTranslation(language, 'signup_failed'));
        }
    };

    const handleLanguageSelect = (langCode: string) => {
        setLanguage(langCode);
    };

    return (
        <PageWrapper className="justify-center items-center py-12 relative" withPadding={false}>
            {/* Center Seal Mark */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 0.5, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    className="w-96 h-96 max-w-2xl max-h-2xl flex items-center justify-center"
                >
                    <svg viewBox="0 0 200 200" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="brainGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style={{ stopColor: '#ec4899', stopOpacity: 1 }} />
                                <stop offset="100%" style={{ stopColor: '#f97316', stopOpacity: 1 }} />
                            </linearGradient>
                            <linearGradient id="aiGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style={{ stopColor: '#f472b6', stopOpacity: 1 }} />
                                <stop offset="100%" style={{ stopColor: '#c084fc', stopOpacity: 1 }} />
                            </linearGradient>
                        </defs>
                        
                        {/* Outer circle */}
                        <circle cx="100" cy="100" r="90" fill="none" stroke="url(#brainGradient2)" strokeWidth="8" opacity="0.4" />
                        
                        {/* Left brain silhouette */}
                        <g opacity="0.6">
                            <circle cx="70" cy="85" r="25" fill="none" stroke="url(#brainGradient2)" strokeWidth="3" />
                            <path d="M 55 85 Q 50 80 50 75 Q 50 70 55 65" fill="none" stroke="url(#brainGradient2)" strokeWidth="2.5" strokeLinecap="round" />
                            <path d="M 70 65 Q 75 60 80 60" fill="none" stroke="url(#brainGradient2)" strokeWidth="2" strokeLinecap="round" />
                        </g>
                        
                        {/* Right AI circuit silhouette */}
                        <g opacity="0.6">
                            <circle cx="130" cy="85" r="25" fill="none" stroke="url(#aiGradient2)" strokeWidth="3" />
                            <circle cx="130" cy="70" r="4" fill="url(#aiGradient2)" />
                            <circle cx="120" cy="85" r="3" fill="url(#aiGradient2)" />
                            <circle cx="140" cy="85" r="3" fill="url(#aiGradient2)" />
                            <path d="M 130 70 L 130 78" stroke="url(#aiGradient2)" strokeWidth="1.5" />
                            <path d="M 120 85 L 128 85" stroke="url(#aiGradient2)" strokeWidth="1.5" />
                            <path d="M 140 85 L 132 85" stroke="url(#aiGradient2)" strokeWidth="1.5" />
                        </g>
                        
                        {/* Bottom curved connector */}
                        <path d="M 60 105 Q 100 130 140 105" fill="none" stroke="url(#brainGradient2)" strokeWidth="3" opacity="0.5" strokeLinecap="round" />
                        
                        {/* Arrow element */}
                        <path d="M 85 120 L 95 135 L 85 135" fill="none" stroke="url(#brainGradient2)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
                    </svg>
                </motion.div>
            </div>
            {/* Language Selector Button */}
            <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsLanguageSelectorOpen(true)}
                className="fixed top-4 right-4 z-50 p-3 bg-white/80 backdrop-blur-sm rounded-lg shadow-md hover:bg-white/90 transition-colors flex items-center gap-2 text-sm font-medium text-gray-700"
            >
                <Globe className="w-4 h-4" />
                <span className="hidden sm:inline">{getTranslation(language, 'select_language')}</span>
            </motion.button>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, type: 'spring' }}
                className="w-full max-w-md p-4 relative z-10"
            >
                <div className="text-center mb-10">
                    <Link to="/" className="text-4xl font-bold tracking-tighter inline-block mb-4">
                        <span className="text-gradient">EduTwin</span>
                    </Link>
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">{getTranslation(language, 'create_account')}</h1>
                    <p className="text-gray-500 text-sm">{getTranslation(language, 'join_message')}</p>
                </div>

                <GlassCard className="p-8">
                    <form onSubmit={handleSignUp} className="space-y-5">
                        <InputField
                            type="text"
                            required
                            placeholder={getTranslation(language, 'full_name_placeholder')}
                            label={getTranslation(language, 'full_name_label')}
                            icon={<User className="w-5 h-5" />}
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />

                        <InputField
                            type="email"
                            required
                            placeholder={getTranslation(language, 'email_placeholder')}
                            label={getTranslation(language, 'email_label')}
                            icon={<Mail className="w-5 h-5" />}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />

                        <InputField
                            type="password"
                            required
                            placeholder={getTranslation(language, 'password_placeholder')}
                            label={getTranslation(language, 'password_label')}
                            icon={<Lock className="w-5 h-5" />}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />

                        {error && (
                            <p className="text-sm text-red-500 text-center">{error}</p>
                        )}

                        <div className="pt-4">
                            <GradientButton type="submit" fullWidth className="group" disabled={isLoading}>
                                {isLoading ? getTranslation(language, 'creating_account') : getTranslation(language, 'create_account_button')}
                                {!isLoading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
                            </GradientButton>
                        </div>
                    </form>

                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-500">
                            {getTranslation(language, 'already_have_account')}{' '}
                            <Link to="/signin" className="text-brand font-medium hover:text-brand-dark transition-colors">
                                {getTranslation(language, 'login_link')}
                            </Link>
                        </p>
                    </div>
                </GlassCard>
            </motion.div>

            <LanguageSelector
                isOpen={isLanguageSelectorOpen}
                onClose={() => setIsLanguageSelectorOpen(false)}
                currentLanguage={language}
                onSelectLanguage={handleLanguageSelect}
            />
        </PageWrapper>
    );
};
