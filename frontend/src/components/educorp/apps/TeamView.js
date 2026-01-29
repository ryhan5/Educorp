import React, { useState } from 'react';
import { Mail, MessageSquare, X, Send } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

const TeamView = ({ members = [], onChat }) => {
    const [activeMemberName, setActiveMemberName] = useState(null);
    const [messageInput, setMessageInput] = useState("");

    // Derive active member from props to ensure real-time updates
    const activeChatMember = members.find(m => m.name === activeMemberName) || null;

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!messageInput.trim() || !activeChatMember) return;

        onChat(activeChatMember.name, messageInput);
        setMessageInput("");
    };

    return (
        <div className="h-full relative overflow-hidden">

            {/* Main Directory */}
            <div className="h-full overflow-y-auto p-6">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-neutral-900 mb-2">Team Directory</h1>
                    <p className="text-neutral-500">Meet your colleagues at EduCorp.</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Manager Card (Always one) */}
                    <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-4">
                            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-700 font-bold text-xl">
                                A
                            </div>
                            <span className="px-2 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded-full uppercase tracking-wide">
                                Manager
                            </span>
                        </div>
                        <h3 className="text-lg font-bold text-neutral-900">Alice</h3>
                        <p className="text-sm text-neutral-500 font-medium mb-3">Engineering Manager</p>

                        <p className="text-sm text-neutral-600 mb-6 italic">
                            "Professional, demanding, focused on results."
                        </p>

                        <button className="w-full py-2 flex items-center justify-center gap-2 border border-neutral-200 rounded-lg text-sm font-medium text-neutral-600 hover:bg-neutral-50 transition-colors">
                            <Mail size={16} />
                            Send Update
                        </button>
                    </div>

                    {/* AI Colleagues */}
                    {members.map((member, idx) => (
                        <div key={idx} className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6 hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between mb-4">
                                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${idx % 2 === 0 ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}`}>
                                    {member.name.charAt(0)}
                                </div>
                                <span className="px-2 py-1 bg-neutral-100 text-neutral-600 text-xs font-bold rounded-full uppercase tracking-wide">
                                    Colleague
                                </span>
                            </div>
                            <h3 className="text-lg font-bold text-neutral-900">{member.name}</h3>
                            <p className="text-sm text-neutral-500 font-medium mb-3">{member.role}</p>

                            <p className="text-sm text-neutral-600 mb-6 italic">
                                "{member.personality}"
                            </p>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => setActiveMemberName(member.name)}
                                    className="flex-1 py-2 flex items-center justify-center gap-2 border border-blue-200 bg-blue-50 rounded-lg text-sm font-medium text-blue-700 hover:bg-blue-100 transition-colors">
                                    <MessageSquare size={16} />
                                    Chat
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {members.length === 0 && (
                    <div className="bg-yellow-50 text-yellow-800 p-4 rounded-lg flex items-center gap-4 border border-yellow-200 mt-4">
                        <span>⚠️ No team members found. Start the simulation to meet your team.</span>
                    </div>
                )}
            </div>

            {/* Chat Overlay */}
            <AnimatePresence>
                {activeChatMember && (
                    <motion.div
                        initial={{ x: '100%', opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: '100%', opacity: 0 }}
                        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                        className="absolute inset-y-0 right-0 w-full md:w-[450px] bg-white border-l border-neutral-200 shadow-2xl z-30 flex flex-col font-sans"
                    >
                        {/* Header */}
                        <div className="px-6 py-4 border-b border-neutral-100 flex items-center justify-between bg-white sticky top-0 z-10">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg shadow-sm border border-blue-100">
                                        {activeChatMember.name.charAt(0)}
                                    </div>
                                    <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-white rounded-full"></div>
                                </div>
                                <div>
                                    <h3 className="font-bold text-neutral-900 text-lg leading-tight">{activeChatMember.name}</h3>
                                    <p className="text-xs text-neutral-500 font-medium">{activeChatMember.role}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setActiveMemberName(null)}
                                className="p-2 hover:bg-neutral-100 rounded-full transition-colors text-neutral-400 hover:text-neutral-600"
                            >
                                <X size={24} />
                            </button>
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-neutral-50/50">
                            {(!activeChatMember.chats || activeChatMember.chats.length === 0) && (
                                <div className="flex flex-col items-center justify-center h-full text-neutral-400 space-y-3 opacity-60">
                                    <div className="w-16 h-16 bg-neutral-200 rounded-full flex items-center justify-center">
                                        <MessageSquare size={32} />
                                    </div>
                                    <div className="text-center">
                                        <p className="font-medium text-neutral-600">No messages yet</p>
                                        <p className="text-xs">Start collaboration with {activeChatMember.name}.</p>
                                    </div>
                                </div>
                            )}

                            {activeChatMember.chats?.map((msg, idx) => (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    key={idx}
                                    className={`flex w-full ${msg.sender === 'You' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`flex max-w-[85%] gap-3 ${msg.sender === 'You' ? 'flex-row-reverse' : 'flex-row'}`}>
                                        {/* Avatar for message */}
                                        <div className="flex-shrink-0 mt-auto">
                                            {msg.sender !== 'You' ? (
                                                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold border border-blue-200">
                                                    {activeChatMember.name.charAt(0)}
                                                </div>
                                            ) : (
                                                <div className="w-8 h-8 rounded-full bg-neutral-200 text-neutral-600 flex items-center justify-center text-xs font-bold border border-neutral-300">
                                                    Me
                                                </div>
                                            )}
                                        </div>

                                        {/* Bubble */}
                                        <div className={`group relative p-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.sender === 'You'
                                            ? 'bg-blue-600 text-white rounded-br-none'
                                            : 'bg-white text-neutral-800 border border-neutral-200 rounded-bl-none'
                                            }`}>
                                            {msg.message}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Input Area */}
                        <div className="p-4 bg-white border-t border-neutral-100">
                            <form
                                onSubmit={handleSendMessage}
                                className="flex items-center gap-2 bg-neutral-50 rounded-xl border border-neutral-200 p-1.5 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all shadow-sm"
                            >
                                <input
                                    type="text"
                                    value={messageInput}
                                    onChange={(e) => setMessageInput(e.target.value)}
                                    placeholder={`Message ${activeChatMember.name}...`}
                                    className="flex-1 bg-transparent text-neutral-900 placeholder-neutral-400 text-sm px-3 py-2 focus:outline-none"
                                />
                                <button
                                    type="submit"
                                    disabled={!messageInput.trim()}
                                    className={`p-2 rounded-lg transition-all duration-200 ${messageInput.trim()
                                        ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
                                        : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                                        }`}
                                >
                                    <Send size={18} />
                                </button>
                            </form>
                            <div className="text-[10px] text-neutral-400 text-center mt-2 font-medium">
                                AI responses are generated based on persona.
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default TeamView;
