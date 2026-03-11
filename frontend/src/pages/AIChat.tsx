import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageWrapper } from '../components/layout/PageWrapper';
import { Navbar } from '../components/layout/Navbar';
import { Sidebar } from '../components/layout/Sidebar';
import { MobileDrawer } from '../components/layout/MobileDrawer';
import { GlassCard } from '../components/ui/GlassCard';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Send, Bot, User, Loader2, Sparkles, Globe, Trash2,
    ThumbsUp, ThumbsDown, BookOpen, Code, Lightbulb,
    MessageSquare, ChevronDown, Languages, Mic, MicOff
} from 'lucide-react';
import { useVoiceSearch } from '../hooks/useVoiceSearch';
import api from '../services/api';
import { useUserPreferences } from '../context/UserPreferencesContext';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    translatedContent?: string;
    translatedLang?: string;
    timestamp: number;
    liked?: boolean;
    disliked?: boolean;
    image?: string; // base64 image data from Gemini
}

const QUICK_PROMPTS = [
    { icon: Code, label: 'Explain a concept', prompt: 'Hey! Can you explain ' },
    { icon: Lightbulb, label: 'Give me tips', prompt: 'What are some good tips for learning ' },
    { icon: BookOpen, label: 'Study plan', prompt: 'Help me create a study plan for ' },
    { icon: MessageSquare, label: 'Practice questions', prompt: 'Can you give me some practice questions about ' },
];

export const AIChat = () => {
    const [searchParams] = useSearchParams();
    const { user } = useAuth();
    const { preferences, setLanguage } = useUserPreferences();
    const { currentLang, setCurrentLang, translate, isTranslating, languages } = useTranslation();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>(() => {
        const stored = localStorage.getItem('ai_chat_messages');
        return stored ? JSON.parse(stored) : [];
    });
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showLangPicker, setShowLangPicker] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const langPickerRef = useRef<HTMLDivElement>(null);

    // Voice search integration
    const handleVoiceResult = useCallback((text: string) => {
        setInput(prev => prev + text);
    }, []);
    const { isListening, startListening, stopListening, isSupported: voiceSupported } = useVoiceSearch(handleVoiceResult);

    // Persist messages
    useEffect(() => {
        localStorage.setItem('ai_chat_messages', JSON.stringify(messages.slice(-50)));
    }, [messages]);

    useEffect(() => {
        const topic = searchParams.get('topic');
        if (topic) {
            setInput(`Can you explain ${topic} in simple terms with an example?`);
        }
    }, [searchParams]);

    // Sync saved language preference
    useEffect(() => {
        if (preferences.language && preferences.language !== currentLang) {
            setCurrentLang(preferences.language);
        }
    }, [preferences.language]);

    // Re-translate messages when language changes
    useEffect(() => {
        if (currentLang === 'en' || messages.length === 0) return;
        
        // Only re-translate assistant messages that need it
        const needsTranslation = messages.some(m => 
            m.role === 'assistant' && 
            (!m.translatedContent || m.translatedLang !== currentLang)
        );
        
        if (needsTranslation) {
            const translateAll = async () => {
                const updated = await Promise.all(
                    messages.map(async (msg) => {
                        if (msg.role === 'assistant' && (!msg.translatedContent || msg.translatedLang !== currentLang)) {
                            const translated = await translate(msg.content);
                            return { ...msg, translatedContent: translated, translatedLang: currentLang };
                        }
                        return msg;
                    })
                );
                setMessages(updated);
            };
            translateAll();
        }
    }, [currentLang]);

    // Auto-scroll
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    // Close lang picker on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (langPickerRef.current && !langPickerRef.current.contains(e.target as Node)) {
                setShowLangPicker(false);
            }
        };
        if (showLangPicker) document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, [showLangPicker]);

    const sendMessage = async () => {
        const text = input.trim();
        if (!text || isLoading) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: text,
            timestamp: Date.now(),
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Try to get AI response from the backend
            const res = await api.post('/chat/message', {
                message: text,
                history: messages.slice(-10).map(m => ({ role: m.role, content: m.content })),
                language: currentLang,
            });

            const aiContent = res.data?.data?.response || res.data?.response || res.data?.message || 'Hey! I got your message and I\'m here to help! What would you like to know more about? 😊';
            const aiImage = res.data?.data?.image || null;

            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: aiContent,
                timestamp: Date.now(),
                image: aiImage || undefined,
            };

            // Backend already responds in the target language via Gemini,
            // so store the response as the translated content directly.
            if (currentLang !== 'en') {
                aiMsg.translatedContent = aiContent;
                aiMsg.translatedLang = currentLang;
            }

            setMessages(prev => [...prev, aiMsg]);
        } catch {
            // Generate a friendly, conversational AI response as fallback
            const greetings = [
                `Hey${user?.name ? ` ${user.name}` : ' there'}! 😊`,
                `Hi${user?.name ? ` ${user.name}` : ''}! 👋`,
                `Yo${user?.name ? ` ${user.name}` : ''}! 🌟`,
                `Hello${user?.name ? ` ${user.name}` : ' friend'}! ✨`,
            ];
            const greeting = greetings[Math.floor(Math.random() * greetings.length)];

            const lowerText = text.toLowerCase();
            let response: string;
            
            if (lowerText.includes('python')) {
                const pythonResponses = [
                    `${greeting} Ooh, Python! Love that language! 🐍\n\nSo, Python is super beginner-friendly but also crazy powerful. Think of it as the Swiss Army knife of programming!\n\nHere's what makes it cool:\n• You don't need to declare variable types - Python just figures it out (that's called "dynamic typing")\n• The syntax reads almost like English - seriously, it's that clean!\n• Lists and dictionaries are your best friends for storing data\n• Indentation actually matters (uses spaces/tabs instead of curly braces)\n\nWant me to explain something specific? Like how loops work, or maybe you're curious about functions? Just say the word! 🚀`,
                    `${greeting} Python time! This is gonna be fun! 🎉\n\nPython is like that friend who's super easy to talk to but also really smart, you know? Here's the deal:\n\n**Why everyone loves Python:**\n🐍 Clean, readable code (no semicolons needed!)\n⚡ Great for beginners AND pros\n📦 Tons of libraries for everything - web, AI, data science, you name it\n🔥 Write less code, do more stuff\n\nWhat aspect of Python are you curious about? Variables? Loops? Functions? Or maybe you want to build something cool? Let's chat! 💬`,
                ];
                response = pythonResponses[Math.floor(Math.random() * pythonResponses.length)];
            } else if (lowerText.includes('javascript') || lowerText.includes('js')) {
                const jsResponses = [
                    `${greeting} JavaScript! Now we're talking! 🚀\n\nJS literally runs the internet, my friend. Every interactive website you've ever used? That's JavaScript doing its magic!\n\nHere's what's awesome about it:\n🌐 Runs in every browser (no installation needed)\n⚡ Can build full websites - both frontend AND backend (thanks Node.js!)\n🎨 Make buttons click, animations happen, forms submit\n📱 Even build mobile apps with React Native\n\nThe best part? Once you learn JS, you can build pretty much anything on the web. What do you want to create? Or curious about how something works? I'm all ears! 👂`,
                    `${greeting} Ah, JavaScript - the language that powers the web! 💻\n\nLet me tell you, JS is everywhere. And I mean EVERYWHERE. Here's why it's so popular:\n\n• Start seeing results immediately in your browser\n• Make websites interactive and fun\n• Tons of frameworks (React, Vue, Angular) to make life easier\n• Can handle both client-side and server-side stuff\n\nWhat interests you most? Wanna learn about DOM manipulation? Async/await? Or maybe build something cool together? Just let me know! 🎯`,
                ];
                response = jsResponses[Math.floor(Math.random() * jsResponses.length)];
            } else if (lowerText.includes('java') && !lowerText.includes('javascript')) {
                response = `${greeting} Java! The classic! ☕\n\nJava's been around forever and it's still going strong. It's like the reliable friend who always has your back.\n\n**Why Java rocks:**\n🏢 Powers millions of enterprise applications\n📱 All Android apps are built with it\n💪 "Write once, run anywhere" - works on any device\n🔒 Super secure and stable\n\nIt's a bit more verbose than Python, but that makes it really explicit about what you're doing. Perfect for learning solid programming fundamentals!\n\nWhat do you want to explore? Classes? Inheritance? Or maybe you're building something specific? 🎯`;
            } else if (lowerText.includes('html') || lowerText.includes('css')) {
                response = `${greeting} Ah yes, the building blocks of the web! 🏗️\n\nHTML and CSS are like... HTML is the skeleton (structure) and CSS is the outfit (styling). Together they make websites look amazing!\n\n**Quick breakdown:**\n📄 HTML = structure and content (headings, paragraphs, images)\n🎨 CSS = make it pretty (colors, layouts, animations)\n✨ Add JavaScript = make it interactive\n\nThe cool thing? You can literally open Notepad, write some HTML, save it as .html, and boom - you've built a webpage! Want to try building something? Or need help with a specific concept? 🚀`;
            } else if (lowerText.includes('help') || lowerText.includes('hi') || lowerText.includes('hello') || lowerText.includes('hey')) {
                response = `${greeting} Great to meet you! I'm your AI learning buddy, and I'm super excited to help you learn! 🎓\n\nThink of me as that friend who's always down to explain things, no judgment, no silly questions allowed (because there aren't any!).\n\n**What I can do for you:**\n💡 Break down complex concepts into simple terms\n📝 Help you understand code and programming\n🎯 Create personalized study plans\n🧩 Give you practice problems to work through\n🐛 Help debug code issues\n❓ Answer your "why" and "how" questions\n\nSeriously, ask me anything! Want to learn a new language? Need help with a concept? Just curious about how something works? I'm here for it all! What's on your mind? 😊`;
            } else if (lowerText.includes('how') || lowerText.includes('what') || lowerText.includes('why') || lowerText.includes('explain')) {
                response = `${greeting} Love the curiosity! That's exactly the right attitude for learning! 🌟\n\nYou asked about: "${text.slice(0, 80)}${text.length > 80 ? '...' : ''}"\n\nLet me help you out! To give you the best explanation:\n\n💭 If it's a concept - I'll break it down with real-world examples\n💻 If it's code - I'll show you how it works step by step\n🎯 If it's a strategy - I'll share practical tips you can use right away\n\nCould you tell me a bit more about what specifically you'd like to know? Or if you want, I can give you a full explanation right now! Your choice! 😄`;
            } else if (lowerText.includes('learn') || lowerText.includes('study') || lowerText.includes('practice')) {
                response = `${greeting} Awesome that you're ready to learn! That's the spirit! 💪\n\nLearning to code is like learning a musical instrument - it takes practice, but every little bit adds up! And the best part? You get to BUILD stuff!\n\n**Here's how we can work together:**\n📚 I can create a learning path tailored just for you\n🎯 Break down topics into bite-sized chunks\n💻 Give you coding exercises to practice\n🔄 Review concepts you're struggling with\n✅ Quiz you to test your knowledge\n\nWhat would you like to learn or practice today? Pick a language, a concept, or just tell me what you want to build, and let's make it happen! 🚀`;
            } else {
                const generalResponses = [
                    `${greeting} Interesting question! Let's figure this out together! 🤔\n\nYou said: "${text.slice(0, 80)}${text.length > 80 ? '...' : ''}"\n\nI'm here to help however I can! Whether you need:\n• A detailed explanation with examples\n• Code snippets to see how it works\n• Tips and best practices\n• Related resources to explore\n\nJust give me a bit more context about what you're working on or what you're curious about, and I'll give you my best answer! Or if you want, I can just start explaining now? 😊`,
                    `${greeting} Cool question! I like where your head's at! 🧠\n\nYou're asking about: "${text.slice(0, 80)}${text.length > 80 ? '...' : ''}"\n\nLet me help you out! I can:\n🎯 Explain the core concept in simple terms\n💡 Show you real examples\n🔍 Dive deeper into specific parts\n📚 Suggest resources or next steps\n\nWhat would be most helpful for you right now? A quick overview or a deep dive? Either way, I got you! 💪`,
                ];
                response = generalResponses[Math.floor(Math.random() * generalResponses.length)];
            }

            const aiMsg: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response,
                timestamp: Date.now(),
            };

            if (currentLang !== 'en') {
                aiMsg.translatedContent = await translate(response);
                aiMsg.translatedLang = currentLang;
            }

            setMessages(prev => [...prev, aiMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const translateMessage = async (msg: ChatMessage) => {
        if (currentLang === 'en') return;
        // Re-translate if language changed or no translation exists
        if (!msg.translatedContent || msg.translatedLang !== currentLang) {
            const translated = await translate(msg.content);
            setMessages(prev => prev.map(m =>
                m.id === msg.id ? { ...m, translatedContent: translated, translatedLang: currentLang } : m
            ));
        }
    };

    const clearChat = () => {
        setMessages([]);
        localStorage.removeItem('ai_chat_messages');
    };

    const toggleLike = (id: string, type: 'like' | 'dislike') => {
        setMessages(prev => prev.map(m => {
            if (m.id !== id) return m;
            if (type === 'like') return { ...m, liked: !m.liked, disliked: false };
            return { ...m, disliked: !m.disliked, liked: false };
        }));
    };

    const currentLangObj = languages.find(l => l.code === currentLang);

    return (
        <>
            <Navbar onMenuClick={() => setDrawerOpen(true)} />
            <Sidebar />
            <MobileDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
            <PageWrapper>
                <div className="lg:ml-64 flex flex-col h-[calc(100vh-8rem)]">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4 flex-shrink-0">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                                <Bot className="w-7 h-7 text-brand" />
                                Chat with Your AI Buddy
                            </h1>
                            <p className="text-sm text-gray-500">Your 24/7 learning companion - friendly, helpful, and judgment-free! 😊</p>
                        </div>
                        <div className="flex items-center gap-2">
                            {/* Language Picker */}
                            <div className="relative" ref={langPickerRef}>
                                <button
                                    onClick={() => setShowLangPicker(prev => !prev)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/80 border border-gray-200 text-sm hover:bg-gray-50 transition-colors"
                                >
                                    <Globe className="w-4 h-4 text-gray-500" />
                                    <span>{currentLangObj?.flag} {currentLangObj?.name || 'English'}</span>
                                    <ChevronDown className="w-3 h-3 text-gray-400" />
                                </button>
                                <AnimatePresence>
                                    {showLangPicker && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -8 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -8 }}
                                            className="absolute right-0 top-full mt-1 w-56 bg-white border border-gray-200 rounded-xl shadow-xl z-50 max-h-72 overflow-y-auto"
                                        >
                                            {languages.map(lang => (
                                                <button
                                                    key={lang.code}
                                                    onClick={() => { 
                                                        setCurrentLang(lang.code); 
                                                        setLanguage(lang.code);
                                                        setShowLangPicker(false); 
                                                    }}
                                                    className={`w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 flex items-center gap-2 ${
                                                        currentLang === lang.code ? 'bg-brand/5 text-brand font-medium' : 'text-gray-700'
                                                    }`}
                                                >
                                                    <span>{lang.flag}</span>
                                                    {lang.name}
                                                </button>
                                            ))}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>

                            <button
                                onClick={clearChat}
                                className="p-2 rounded-xl text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                                title="Clear chat"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Chat Messages */}
                    <div className="flex-1 overflow-y-auto rounded-2xl bg-white/40 backdrop-blur-sm border border-gray-100 p-4 mb-4">
                        {messages.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-full text-center">
                                <div className="w-20 h-20 rounded-2xl bg-brand/10 flex items-center justify-center mb-4">
                                    <Sparkles className="w-10 h-10 text-brand" />
                                </div>
                                <h3 className="text-lg font-bold text-gray-800 mb-2">Hey! Let's learn together! 👋</h3>
                                <p className="text-sm text-gray-500 mb-6 max-w-sm">
                                    I'm your friendly AI tutor - think of me as your study buddy who's always here to help! Ask me anything, no question is too basic or too complex. Let's make learning fun! 😊
                                </p>
                                {/* Quick Prompts */}
                                <div className="grid grid-cols-2 gap-3 max-w-md">
                                    {QUICK_PROMPTS.map(({ icon: Icon, label, prompt }) => (
                                        <button
                                            key={label}
                                            onClick={() => setInput(prompt)}
                                            className="flex items-center gap-2 px-4 py-3 rounded-xl bg-white border border-gray-200 hover:border-brand/30 hover:bg-brand/5 text-sm text-gray-600 transition-all text-left"
                                        >
                                            <Icon className="w-4 h-4 text-brand flex-shrink-0" />
                                            {label}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {messages.map((msg) => (
                                    <motion.div
                                        key={msg.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                                    >
                                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                                            msg.role === 'user'
                                                ? 'bg-brand text-white'
                                                : 'bg-purple-100 text-purple-600'
                                        }`}>
                                            {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                        </div>
                                        <div className={`max-w-[75%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                            <div className={`px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                                                msg.role === 'user'
                                                    ? 'bg-brand text-white rounded-tr-md'
                                                    : 'bg-white border border-gray-100 text-gray-800 rounded-tl-md shadow-sm'
                                            }`}>
                                                {msg.translatedContent && currentLang !== 'en'
                                                    ? msg.translatedContent
                                                    : msg.content
                                                }
                                                {msg.image && (
                                                    <img
                                                        src={`data:image/png;base64,${msg.image}`}
                                                        alt="AI generated diagram"
                                                        className="mt-3 rounded-lg max-w-full border border-gray-200"
                                                    />
                                                )}
                                            </div>
                                            {/* Message actions for AI messages */}
                                            {msg.role === 'assistant' && (
                                                <div className="flex items-center gap-1 mt-1">
                                                    <button
                                                        onClick={() => translateMessage(msg)}
                                                        className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                                                        title="Translate"
                                                    >
                                                        <Languages className="w-3.5 h-3.5" />
                                                    </button>
                                                    <button
                                                        onClick={() => toggleLike(msg.id, 'like')}
                                                        className={`p-1 transition-colors ${msg.liked ? 'text-green-500' : 'text-gray-400 hover:text-green-500'}`}
                                                    >
                                                        <ThumbsUp className="w-3.5 h-3.5" />
                                                    </button>
                                                    <button
                                                        onClick={() => toggleLike(msg.id, 'dislike')}
                                                        className={`p-1 transition-colors ${msg.disliked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'}`}
                                                    >
                                                        <ThumbsDown className="w-3.5 h-3.5" />
                                                    </button>
                                                    <span className="text-[10px] text-gray-400 ml-2">
                                                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    </span>
                                                </div>
                                            )}
                                            {msg.role === 'user' && (
                                                <div className="flex justify-end mt-1">
                                                    <span className="text-[10px] text-gray-400">
                                                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    </span>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                ))}

                                {/* Typing indicator */}
                                {isLoading && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="flex gap-3"
                                    >
                                        <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                                            <Bot className="w-4 h-4 text-purple-600" />
                                        </div>
                                        <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-tl-md shadow-sm">
                                            <div className="flex gap-1">
                                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                <div ref={chatEndRef} />
                            </div>
                        )}
                    </div>

                    {/* Translation indicator */}
                    {isTranslating && (
                        <div className="text-xs text-blue-500 flex items-center gap-1 mb-1 px-2">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Translating...
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="flex-shrink-0">
                        <GlassCard className="p-3">
                            <div className="flex items-end gap-2">
                                <div className="flex-1 relative">
                                    <textarea
                                        ref={inputRef}
                                        value={input}
                                        onChange={e => setInput(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Ask me anything! Press Shift+Enter for new line 💬"
                                        rows={1}
                                        className="w-full resize-none px-4 py-3 pr-20 rounded-xl border border-gray-200 bg-white/80 text-sm focus:outline-none focus:ring-2 focus:ring-brand/30 transition-all max-h-32"
                                        style={{ minHeight: '44px' }}
                                        onInput={e => {
                                            const target = e.target as HTMLTextAreaElement;
                                            target.style.height = 'auto';
                                            target.style.height = Math.min(target.scrollHeight, 128) + 'px';
                                        }}
                                    />
                                    {/* Voice input button */}
                                    {voiceSupported && (
                                        <button
                                            onClick={isListening ? stopListening : startListening}
                                            className={`absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-colors ${
                                                isListening
                                                    ? 'bg-red-100 text-red-500 animate-pulse'
                                                    : 'text-gray-400 hover:text-brand hover:bg-brand/5'
                                            }`}
                                            title={isListening ? 'Stop recording' : 'Voice input'}
                                        >
                                            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                                        </button>
                                    )}
                                </div>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={sendMessage}
                                    disabled={!input.trim() || isLoading}
                                    className="p-3 rounded-xl bg-brand text-white hover:bg-brand/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                >
                                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                                </motion.button>
                            </div>
                        </GlassCard>
                    </div>
                </div>
            </PageWrapper>
        </>
    );
};
