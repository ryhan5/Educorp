"use client";

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, AlertCircle, CheckCircle, Mic, Video, FileText } from 'lucide-react';

const InterviewTwin = () => {
    const [persona, setPersona] = useState("Technical Interviewer");
    const [jobDesc, setJobDesc] = useState("");
    const [resumeText, setResumeText] = useState("");
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [started, setStarted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const [isListening, setIsListening] = useState(false);
    const [cameraOn, setCameraOn] = useState(true);
    const scrollRef = useRef(null);
    const videoRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" });
        }

        // TTS for latest AI message
        const lastMsg = messages[messages.length - 1];
        if (lastMsg && lastMsg.role === 'ai') {
            speak(lastMsg.content);
        }
    }, [messages]);

    // Camera Logic
    useEffect(() => {
        let stream = null;
        const startCamera = async () => {
            if (cameraOn) {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                    }
                } catch (err) {
                    console.error("Camera failed", err);
                    setCameraOn(false);
                }
            } else {
                if (videoRef.current && videoRef.current.srcObject) {
                    const tracks = videoRef.current.srcObject.getTracks();
                    tracks.forEach(t => t.stop());
                    videoRef.current.srcObject = null;
                }
            }
        };
        startCamera();
        return () => {
            if (stream) stream.getTracks().forEach(t => t.stop());
        };
    }, [cameraOn, started]);

    const speak = (text) => {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel(); // Stop previous
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
    };

    const handleStart = async () => {
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/api/interview/start', {
                persona,
                job_description: jobDesc,
                resume_text: resumeText
            });
            setStarted(true);
            setMessages([{ role: 'ai', content: res.data.message }]);
        } catch (error) {
            console.error("Failed to start", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMsg = input;
        setInput("");
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            const res = await axios.post('http://localhost:8000/api/interview/chat', {
                message: userMsg,
                session_id: "demo_session"
            });
            setMessages(prev => [...prev, { role: 'ai', content: res.data.response }]);
        } catch (error) {
            console.error("Chat failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleEndSession = async () => {
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/api/interview/feedback', {}, {
                params: { session_id: "demo_session" }
            });
            setFeedback(res.data);
        } catch (error) {
            console.error("Feedback failed", error);
        } finally {
            setLoading(false);
        }
    };

    const handleMicClick = () => {
        setIsListening(!isListening);
        if (!isListening) {
            setTimeout(() => {
                setIsListening(false);
                setInput("I have experience with Python and scalable systems."); // Mock voice input
            }, 2000);
        }
    };

    // Feedback View
    if (feedback) {
        return (
            <div className="border border-neutral-200 rounded-xl p-8">
                <h2 className="text-2xl font-semibold text-black mb-6">Detailed Feedback Report</h2>

                <div className="flex items-baseline gap-4 mb-8">
                    <div className="text-center">
                        <div className="text-5xl font-semibold text-black">{feedback.score}</div>
                        <div className="text-xs text-neutral-500 uppercase mt-1">Overall Score</div>
                    </div>
                </div>

                {/* Readiness Heatmap */}
                {feedback.readiness_score && (
                    <div className="mb-8 p-4 bg-neutral-50 rounded-lg">
                        <h3 className="font-medium text-black mb-3">Readiness Heatmap</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {Object.entries(feedback.readiness_score).map(([skill, score]) => (
                                <div key={skill} className="bg-white p-3 rounded border border-neutral-200">
                                    <div className="text-xs text-neutral-500">{skill}</div>
                                    <div className="text-xl font-bold text-black">{score}%</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <div className="border border-neutral-200 rounded-lg p-5 bg-green-50/50">
                        <h3 className="flex items-center gap-2 font-medium text-green-800 mb-3">
                            <CheckCircle size={16} /> Strengths
                        </h3>
                        <ul className="space-y-2 text-sm text-green-900">
                            {feedback.strengths.map((s, i) => <li key={i}>• {s}</li>)}
                        </ul>
                    </div>
                    <div className="border border-neutral-200 rounded-lg p-5 bg-red-50/50">
                        <h3 className="flex items-center gap-2 font-medium text-red-800 mb-3">
                            <AlertCircle size={16} /> Areas to Improve
                        </h3>
                        <ul className="space-y-2 text-sm text-red-900">
                            {feedback.weaknesses.map((w, i) => <li key={i}>• {w}</li>)}
                        </ul>
                    </div>
                </div>

                <div className="border-t border-neutral-200 pt-6 mb-8">
                    <h3 className="font-medium text-black mb-2">Executive Summary</h3>
                    <p className="text-neutral-600 text-sm leading-relaxed">{feedback.summary}</p>
                </div>

                <button
                    onClick={() => window.location.reload()}
                    className="bg-black text-white px-6 py-3 rounded-lg text-sm font-medium hover:opacity-90"
                >
                    Start New Interview
                </button>
            </div>
        );
    }

    // Config View
    if (!started) {
        return (
            <div className="border border-neutral-200 rounded-xl p-8 max-w-xl">
                <h2 className="text-xl font-semibold text-black mb-6">Setup Your Interview Twin</h2>

                <div className="mb-6">
                    <label className="block text-sm text-neutral-600 mb-3">Select Interview Round</label>
                    <div className="flex flex-wrap gap-2">
                        {["Technical Interviewer", "HR Manager", "Hiring Manager"].map(p => (
                            <button
                                key={p}
                                onClick={() => setPersona(p)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${persona === p
                                    ? 'bg-black text-white'
                                    : 'border border-neutral-200 text-neutral-600 hover:border-neutral-300'
                                    }`}
                            >
                                {p}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="mb-6">
                    <label className="block text-sm text-neutral-600 mb-2 flex items-center gap-2">
                        <FileText size={16} /> Upload Resume (PDF/DOCX/TXT)
                    </label>
                    <div className="flex gap-2">
                        <input
                            type="file"
                            accept=".pdf,.docx,.txt"
                            onChange={async (e) => {
                                const file = e.target.files[0];
                                if (!file) return;
                                setLoading(true);
                                const formData = new FormData();
                                formData.append('file', file);
                                try {
                                    const res = await axios.post('http://localhost:8000/api/interview/parse-resume', formData);
                                    setResumeText(res.data.text);
                                } catch (err) {
                                    console.error("Upload failed", err);
                                    alert("Failed to parse resume content");
                                } finally {
                                    setLoading(false);
                                }
                            }}
                            className="block w-full text-sm text-neutral-500
                               file:mr-4 file:py-2 file:px-4
                               file:rounded-full file:border-0
                               file:text-sm file:font-semibold
                               file:bg-black file:text-white
                               hover:file:bg-neutral-800
                             "
                        />
                    </div>
                    {resumeText && (
                        <div className="mt-2 p-3 bg-green-50 rounded-lg border border-green-200 text-xs text-green-800 flex items-center gap-2">
                            <CheckCircle size={14} /> Resume content parsed successfully! ({resumeText.length} chars)
                        </div>
                    )}
                    <textarea
                        className="w-full mt-2 p-3 border border-neutral-200 rounded-lg text-xs focus:outline-none focus:border-black transition-colors resize-none h-20 bg-neutral-50"
                        placeholder="Content will appear here..."
                        value={resumeText}
                        readOnly
                    />
                </div>

                <div className="mb-8">
                    <label className="block text-sm text-neutral-600 mb-2">Job Description (optional)</label>
                    <textarea
                        className="w-full p-4 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black transition-colors resize-none h-24"
                        placeholder="Paste job description..."
                        value={jobDesc}
                        onChange={(e) => setJobDesc(e.target.value)}
                    />
                </div>

                <button
                    onClick={handleStart}
                    disabled={loading}
                    className="w-full bg-black text-white py-3.5 rounded-lg font-medium text-sm hover:opacity-90 disabled:opacity-40"
                >
                    {loading ? "Initializing Twin..." : "Start Interview"}
                </button>
            </div>
        );
    }

    // Chat View
    return (
        <div className="border border-neutral-200 rounded-xl overflow-hidden flex flex-col h-[650px] relative">
            {/* Header */}
            <div className="border-b border-neutral-200 p-4 flex justify-between items-center bg-white z-10">
                <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
                    <div>
                        <h3 className="font-medium text-black">{persona}</h3>
                        <p className="text-xs text-neutral-400">AI Interview Twin Active</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setCameraOn(!cameraOn)}
                        className={`p-2 rounded-lg ${cameraOn ? 'bg-neutral-100 text-black' : 'bg-red-50 text-red-500'}`}>
                        <Video size={18} />
                    </button>
                    <button
                        onClick={handleEndSession}
                        className="text-sm text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100 px-3 py-1.5 rounded-lg"
                    >
                        End Session
                    </button>
                </div>
            </div>

            {/* Real Camera Feed Overlay */}
            {cameraOn && (
                <div className="absolute top-20 right-4 w-48 h-36 bg-black rounded-lg border-2 border-white/20 shadow-lg z-20 overflow-hidden">
                    <video
                        ref={videoRef}
                        autoPlay
                        muted
                        playsInline
                        className="w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                    />
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-neutral-50 relative">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[75%] rounded-xl px-4 py-3 text-sm shadow-sm ${msg.role === 'user'
                            ? 'bg-black text-white'
                            : 'bg-white border border-neutral-200 text-neutral-700'
                            }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-neutral-200 px-4 py-3 rounded-xl shadow-sm">
                            <div className="flex gap-1">
                                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" />
                                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                <span className="w-1.5 h-1.5 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={scrollRef} />
            </div>

            {/* Input */}
            <div className="border-t border-neutral-200 p-4 bg-white">
                <div className="flex gap-3">
                    <button
                        onClick={handleMicClick}
                        className={`p-3 rounded-lg transition-colors ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'}`}
                    >
                        <Mic size={20} />
                    </button>
                    <input
                        type="text"
                        className="flex-1 px-4 py-3 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black"
                        placeholder={isListening ? "Listening..." : "Type your answer..."}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="bg-black text-white px-4 rounded-lg disabled:opacity-40"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default InterviewTwin;
