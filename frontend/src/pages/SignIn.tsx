import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useUserPreferences } from '../context/UserPreferencesContext';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { InputField } from '../components/ui/InputField';
import { LanguageSelector } from '../components/LanguageSelector';
import { ArrowRight, Mail, Lock, Brain, Globe, Target, Rocket } from 'lucide-react';
import { motion } from 'framer-motion';
import { getTranslation } from '../lib/translations';

const FEATURES = [
    { icon: Brain, title: 'smart_learning', desc: 'smart_learning_desc', color: 'text-purple-500', bg: 'bg-purple-50' },
    { icon: Globe, title: 'languages_feature', desc: 'languages_desc', color: 'text-blue-500', bg: 'bg-blue-50', isClickable: true },
    { icon: Target, title: 'adaptive_quizzes', desc: 'adaptive_quizzes_desc', color: 'text-rose-500', bg: 'bg-rose-50' },
    { icon: Rocket, title: 'all_in_one', desc: 'all_in_one_desc', color: 'text-amber-500', bg: 'bg-amber-50' },
];

export const SignIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isLanguageSelectorOpen, setIsLanguageSelectorOpen] = useState(false);
    const navigate = useNavigate();
    const { login, backendError } = useAuth();
    const { preferences, setLanguage } = useUserPreferences();
    const language = preferences.language;

    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        const result = await login(email, password);
        setIsLoading(false);
        if (result === true) {
            navigate('/dashboard');
        } else {
            setError(result || (backendError
                ? getTranslation(language, 'server_error')
                : getTranslation(language, 'invalid_credentials')));
        }
    };

    const handleLanguageSelect = (langCode: string) => {
        setLanguage(langCode);
    };

    return (
        <div className="w-full flex flex-col lg:flex-row lg:min-h-screen overflow-auto relative">
            {/* Center Seal Mark */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 0.5, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    className="w-96 h-96 lg:w-full lg:h-full lg:max-w-2xl lg:max-h-2xl flex items-center justify-center"
                >
                    <svg viewBox="0 0 200 200" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="brainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style={{ stopColor: '#ec4899', stopOpacity: 1 }} />
                                <stop offset="100%" style={{ stopColor: '#f97316', stopOpacity: 1 }} />
                            </linearGradient>
                            <linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style={{ stopColor: '#f472b6', stopOpacity: 1 }} />
                                <stop offset="100%" style={{ stopColor: '#c084fc', stopOpacity: 1 }} />
                            </linearGradient>
                        </defs>
                        
                        {/* Outer circle */}
                        <circle cx="100" cy="100" r="90" fill="none" stroke="url(#brainGradient)" strokeWidth="8" opacity="0.4" />
                        
                        {/* Left brain silhouette */}
                        <g opacity="0.6">
                            <circle cx="70" cy="85" r="25" fill="none" stroke="url(#brainGradient)" strokeWidth="3" />
                            <path d="M 55 85 Q 50 80 50 75 Q 50 70 55 65" fill="none" stroke="url(#brainGradient)" strokeWidth="2.5" strokeLinecap="round" />
                            <path d="M 70 65 Q 75 60 80 60" fill="none" stroke="url(#brainGradient)" strokeWidth="2" strokeLinecap="round" />
                        </g>
                        
                        {/* Right AI circuit silhouette */}
                        <g opacity="0.6">
                            <circle cx="130" cy="85" r="25" fill="none" stroke="url(#aiGradient)" strokeWidth="3" />
                            <circle cx="130" cy="70" r="4" fill="url(#aiGradient)" />
                            <circle cx="120" cy="85" r="3" fill="url(#aiGradient)" />
                            <circle cx="140" cy="85" r="3" fill="url(#aiGradient)" />
                            <path d="M 130 70 L 130 78" stroke="url(#aiGradient)" strokeWidth="1.5" />
                            <path d="M 120 85 L 128 85" stroke="url(#aiGradient)" strokeWidth="1.5" />
                            <path d="M 140 85 L 132 85" stroke="url(#aiGradient)" strokeWidth="1.5" />
                        </g>
                        
                        {/* Bottom curved connector */}
                        <path d="M 60 105 Q 100 130 140 105" fill="none" stroke="url(#brainGradient)" strokeWidth="3" opacity="0.5" strokeLinecap="round" />
                        
                        {/* Arrow element */}
                        <path d="M 85 120 L 95 135 L 85 135" fill="none" stroke="url(#brainGradient)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
                    </svg>
                </motion.div>
            </div>

            {/* Left panel — branding + features */}
            <div className="lg:w-1/2 w-full relative flex flex-col justify-center px-8 sm:px-14 lg:px-16 py-12 lg:py-0 z-10" style={{ background: 'linear-gradient(135deg, #fce4ec 0%, #fdf2f8 50%, #fce7f3 100%)' }}>
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
                        {getTranslation(language, 'your_ai_companion')}<br />
                        <span className="text-gray-500 text-base">{getTranslation(language, 'master_topic')}</span>
                    </p>
 
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {FEATURES.map((f, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
                                onClick={() => f.isClickable && setIsLanguageSelectorOpen(true)}
                                className={`flex items-start gap-3 bg-white/60 backdrop-blur-sm rounded-xl p-4 hover:bg-white/80 transition-colors shadow-sm ${f.isClickable ? 'cursor-pointer hover:ring-2 hover:ring-blue-400' : 'cursor-default'}`}
                            >
                                <div className="w-9 h-9 rounded-lg bg-pink-100 flex items-center justify-center flex-shrink-0">
                                    <f.icon className="w-5 h-5 text-rose-500" />
                                </div>
                                <div>
                                    <h3 className="text-gray-800 font-bold text-sm">{getTranslation(language, f.title)}</h3>
                                    <p className="text-gray-500 text-xs leading-relaxed mt-0.5">{getTranslation(language, f.desc)}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    <p className="mt-10 text-gray-400 text-xs">
                        {getTranslation(language, 'built_by')} <span className="text-gray-600 font-semibold">{getTranslation(language, 'pixel_pirates')}</span>
                    </p>
                </motion.div>
            </div>

            {/* Right panel — login form */}
            <div className="lg:w-1/2 w-full relative flex items-center justify-center px-6 sm:px-12 py-12 lg:py-0 z-10" style={{ background: 'linear-gradient(135deg, #fce4ec 0%, #fdf2f8 50%, #fce7f3 100%)' }}>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2, type: 'spring' }}
                    className="w-full max-w-md"
                >
                    <div className="mb-10">
                        <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
                            {getTranslation(language, 'welcome_back')}
                        </h2>
                        <p className="text-gray-500 mt-2">{getTranslation(language, 'sign_in_subtitle')}</p>
                    </div>

                    <GlassCard className="p-8 shadow-xl shadow-pink-200/30">
                        <form onSubmit={handleSignIn} className="space-y-6">
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

                            <div className="pt-2">
                                <GradientButton type="submit" fullWidth className="group" disabled={isLoading}>
                                    {isLoading ? getTranslation(language, 'signin_loading') : getTranslation(language, 'signin_button')}
                                    {!isLoading && <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />}
                                </GradientButton>
                            </div>
                        </form>

                        <div className="mt-8 text-center">
                            <p className="text-sm text-gray-500">
                                {getTranslation(language, 'no_account')}{' '}
                                <Link to="/signup" className="text-brand font-semibold hover:text-brand-dark transition-colors">
                                    {getTranslation(language, 'signup_link')}
                                </Link>
                            </p>
                        </div>
                    </GlassCard>
                </motion.div>
            </div>

            <LanguageSelector
                isOpen={isLanguageSelectorOpen}
                onClose={() => setIsLanguageSelectorOpen(false)}
                currentLanguage={language}
                onSelectLanguage={handleLanguageSelect}
            />
        </div>
    );
};
