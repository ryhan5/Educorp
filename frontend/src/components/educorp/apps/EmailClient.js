import React, { useState } from 'react';
import { Search, Star, MoreVertical, Reply, CornerUpRight, Trash2, Mail, Send } from 'lucide-react';

const EmailClient = ({ emails, onReply }) => {
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [replyText, setReplyText] = useState("");

    const handleSendReply = () => {
        if (!selectedEmail) return;
        onReply(selectedEmail.id, replyText);
        setReplyText("");
    };

    return (
        <div className="flex h-full rounded-2xl overflow-hidden bg-white border border-neutral-200 shadow-sm">
            {/* Sidebar / List */}
            <div className={`w-full md:w-80 border-r border-neutral-200 flex flex-col ${selectedEmail ? 'hidden md:flex' : 'flex'} bg-neutral-50`}>
                {/* Header */}
                <div className="p-4 border-b border-neutral-200 flex justify-between items-center bg-white">
                    <h2 className="font-semibold text-neutral-900 flex items-center gap-2">
                        <Mail size={18} className="text-black" /> Inbox
                    </h2>
                    <span className="text-xs font-mono text-neutral-500">{emails.length} messages</span>
                </div>

                {/* Search */}
                <div className="p-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-2.5 text-neutral-400" size={14} />
                        <input
                            type="text"
                            placeholder="Search emails..."
                            className="w-full bg-white text-neutral-900 text-sm rounded-lg pl-9 pr-4 py-2 outline-none focus:ring-1 focus:ring-black border border-neutral-200 placeholder:text-neutral-400 shadow-sm"
                        />
                    </div>
                </div>

                {/* Email List */}
                <div className="flex-1 overflow-y-auto">
                    {emails.map(email => (
                        <div
                            key={email.id}
                            onClick={() => setSelectedEmail(email)}
                            className={`p-4 border-b border-neutral-200 cursor-pointer transition-colors ${selectedEmail?.id === email.id ? 'bg-white border-l-2 border-l-black shadow-sm' : 'hover:bg-white border-l-2 border-l-transparent hover:shadow-sm'}`}
                        >
                            <div className="flex justify-between items-start mb-1">
                                <span className={`font-medium ${!email.read ? 'text-black' : 'text-neutral-500'}`}>{email.sender}</span>
                                <span className="text-[10px] text-neutral-400">10:42 AM</span>
                            </div>
                            <div className="text-sm text-neutral-700 font-medium truncate mb-1">{email.subject}</div>
                            <div className="text-xs text-neutral-500 truncate">{email.body}</div>
                            {email.replied && (
                                <div className="mt-2 flex items-center gap-1 text-[10px] text-green-700 bg-green-50 px-2 py-0.5 rounded w-fit border border-green-100">
                                    <Reply size={10} /> Replied
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Content / Detail View */}
            <div className={`flex-1 flex flex-col bg-white ${!selectedEmail ? 'hidden md:flex' : 'flex'}`}>
                {selectedEmail ? (
                    <>
                        {/* Toolbar */}
                        <div className="h-16 border-b border-neutral-200 flex items-center justify-between px-6 bg-white">
                            <div className="flex items-center gap-4">
                                <button className="md:hidden text-neutral-500" onClick={() => setSelectedEmail(null)}>← Back</button>
                                <div className="flex gap-2 text-neutral-500">
                                    <button className="p-2 hover:bg-neutral-100 rounded-full transition-colors"><Reply size={16} /></button>
                                    <button className="p-2 hover:bg-neutral-100 rounded-full transition-colors"><Trash2 size={16} /></button>
                                    <button className="p-2 hover:bg-neutral-100 rounded-full transition-colors"><MoreVertical size={16} /></button>
                                </div>
                            </div>
                        </div>

                        {/* Email Body */}
                        <div className="flex-1 p-8 overflow-y-auto bg-white">
                            <h1 className="text-2xl font-bold text-neutral-900 mb-6">{selectedEmail.subject}</h1>

                            <div className="flex items-center gap-4 mb-8">
                                <div className="w-10 h-10 rounded-full bg-black flex items-center justify-center text-white font-bold">
                                    {selectedEmail.sender[0]}
                                </div>
                                <div>
                                    <div className="font-medium text-neutral-900">{selectedEmail.sender}</div>
                                    <div className="text-xs text-neutral-500">to me</div>
                                </div>
                            </div>

                            <div className="prose prose-neutral prose-sm max-w-none text-neutral-800">
                                <p className="whitespace-pre-wrap leading-relaxed">
                                    {selectedEmail.body}
                                </p>
                            </div>

                            {/* Reply Box */}
                            <div className="mt-12 border border-neutral-200 rounded-xl overflow-hidden shadow-sm">
                                <div className="bg-neutral-50 px-4 py-2 border-b border-neutral-200 flex gap-2">
                                    <span className="text-xs font-bold text-neutral-500">Reply</span>
                                </div>
                                <textarea
                                    className="w-full bg-white p-4 text-neutral-900 outline-none min-h-[100px] text-sm resize-none"
                                    placeholder="Write your reply..."
                                    value={replyText}
                                    onChange={(e) => setReplyText(e.target.value)}
                                />
                                <div className="p-3 bg-neutral-50 flex justify-end border-t border-neutral-200">
                                    <button
                                        onClick={handleSendReply}
                                        disabled={!replyText.trim()}
                                        className="bg-black hover:bg-neutral-800 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Send size={14} /> Send
                                    </button>
                                </div>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-neutral-400">
                        <Mail size={48} className="mb-4 opacity-20" />
                        <p>Select an email to read</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmailClient;
