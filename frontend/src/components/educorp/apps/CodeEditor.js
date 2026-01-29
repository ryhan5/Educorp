import React, { useState, useRef } from 'react';
import { Play, Save, GitBranch, Settings, FileCode, CheckCircle, AlertCircle, Search as SearchIconType } from 'lucide-react';

const CodeEditor = ({ code, setCode, onSubmit }) => {
    const lineNumbers = code.split('\n').map((_, i) => i + 1);
    const textareaRef = useRef(null);
    const lineNumbersRef = useRef(null);

    // Sync scroll between textarea and line numbers
    const handleScroll = () => {
        if (textareaRef.current && lineNumbersRef.current) {
            lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
        }
    };

    // Handle Tab key for indentation
    const handleKeyDown = (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const spaces = "    "; // 4 spaces
            const newCode = code.substring(0, start) + spaces + code.substring(end);
            setCode(newCode);

            // Move cursor
            setTimeout(() => {
                if (textareaRef.current) {
                    textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
                }
            }, 0);
        }
    };

    return (
        <div className="h-full flex flex-col bg-white rounded-2xl overflow-hidden border border-neutral-200 shadow-sm relative group">
            {/* Toolbar */}
            <div className="h-10 bg-neutral-50 border-b border-neutral-200 flex items-center px-4 justify-between shrink-0">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 text-neutral-600 bg-white px-3 py-1 rounded text-xs border border-neutral-200 shadow-sm">
                        <FileCode size={12} className="text-blue-600" />
                        <span className="font-medium">main.py</span>
                    </div>
                </div>
                {/* Top button (can keep or remove, keeping for desktop visibility) */}
                <div className="hidden md:flex items-center gap-2">
                    <span className="text-[10px] text-neutral-400">Autosave on</span>
                </div>
            </div>

            {/* Main Editor Area */}
            <div className="flex-1 flex bg-white min-h-0 relative">

                {/* Sidebar (Fake Activity Bar) */}
                <div className="w-12 border-r border-neutral-200 flex flex-col items-center py-4 gap-6 text-neutral-400 bg-neutral-50 shrink-0">
                    <FileCode size={20} className="text-black" />
                    <SearchIcon size={20} />
                    <GitBranch size={20} />
                    <div className="flex-1" />
                    <Settings size={20} />
                </div>

                {/* Editor Surface */}
                <div className="flex-1 flex overflow-hidden relative">
                    {/* Line Numbers */}
                    <div
                        ref={lineNumbersRef}
                        className="w-12 bg-white text-neutral-300 text-right pr-4 text-xs font-mono pt-4 select-none leading-relaxed border-r border-neutral-100 overflow-hidden"
                    >
                        {lineNumbers.map(n => (
                            <div key={n}>{n}</div>
                        ))}
                    </div>

                    {/* Text Area */}
                    <textarea
                        ref={textareaRef}
                        onScroll={handleScroll}
                        onKeyDown={handleKeyDown}
                        className="flex-1 bg-transparent text-neutral-800 font-mono text-xs p-4 leading-relaxed outline-none resize-none whitespace-pre selection:bg-blue-100 placeholder:text-neutral-300 caret-black cursor-text z-0"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        spellCheck="false"
                        placeholder="# Write your python code here..."
                    />

                    {/* Floating Run Button */}
                    <button
                        onClick={onSubmit}
                        className="absolute bottom-6 right-6 bg-green-600 hover:bg-green-500 text-white px-5 py-3 rounded-full font-bold shadow-xl hover:shadow-2xl hover:scale-105 transition-all flex items-center gap-2 z-10"
                    >
                        <Play size={16} fill="currentColor" /> Run Code
                    </button>
                </div>
            </div>

            {/* Status Bar */}
            <div className="h-6 bg-blue-600 text-white text-[10px] flex items-center px-3 justify-between font-mono shrink-0">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1"><GitBranch size={10} /> main</span>
                    <span className="flex items-center gap-1"><AlertCircle size={10} /> 0 errors</span>
                </div>
                <div className="flex items-center gap-4">
                    <span>Ln {lineNumbers.length}, Col 1</span>
                    <span>UTF-8</span>
                    <span>Python</span>
                </div>
            </div>
        </div>
    );
};

// Helper for fake icon to avoid import error
const SearchIcon = ({ size, className }) => <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>;

export default CodeEditor;
