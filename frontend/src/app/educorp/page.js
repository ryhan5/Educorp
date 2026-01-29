"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import WorkspaceLayout from '@/components/educorp/WorkspaceLayout';
import EmailClient from '@/components/educorp/apps/EmailClient';
import CodeEditor from '@/components/educorp/apps/CodeEditor';
import TaskBoard from '@/components/educorp/apps/TaskBoard';
import TeamView from '@/components/educorp/apps/TeamView';
import AnalyticsDashboard from '@/components/educorp/apps/AnalyticsDashboard';

const EduCorpPage = () => {
    const [gameState, setGameState] = useState({
        emails: [],
        tasks: [],
        day: 1,
        trust_score: 50,
        team_members: []
    });
    const [activeApp, setActiveApp] = useState('email');
    const [code, setCode] = useState("# Fix the bug in auth.py\n\ndef login(username, password):\n    # TODO: Implement secure login\n    pass");

    // Polling for state
    useEffect(() => {
        fetchState();
        const interval = setInterval(fetchState, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchState = async () => {
        try {
            const res = await axios.get('http://localhost:8000/api/simulator/state');
            setGameState(res.data);
        } catch (e) {
            console.error("Failed to fetch state", e);
        }
    };

    const handleReplyEmail = async (emailId, content) => {
        try {
            await axios.post('http://localhost:8000/api/simulator/action', {
                session_id: "demo_sim",
                action_type: "reply_email",
                payload: { email_id: emailId, content }
            });
            fetchState();
        } catch (e) { console.error(e); }
    };

    const handleSubmitCode = async () => {
        // Just pick the first task for this demo
        const taskId = gameState.tasks.find(t => t.status !== 'done')?.id;
        if (!taskId) {
            alert("No active task to submit for!");
            return;
        }

        try {
            await axios.post('http://localhost:8000/api/simulator/action', {
                session_id: "demo_sim",
                action_type: "submit_task",
                payload: { task_id: taskId, code }
            });
            alert("Code Submitted!");
            fetchState();
        } catch (e) { console.error(e); }
    };

    const handleTeamChat = async (memberName, message) => {
        try {
            await axios.post('http://localhost:8000/api/simulator/action', {
                session_id: "demo_sim",
                action_type: "chat_colleague",
                payload: { member_name: memberName, message }
            });
            fetchState();
        } catch (e) { console.error(e); }
    };


    const [loading, setLoading] = useState(false);
    const hasStarted = gameState.emails.length > 0 || gameState.tasks.length > 0;

    const handleStart = async () => {
        setLoading(true);
        try {
            await axios.post('http://localhost:8000/api/simulator/start', {}, {
                params: { session_id: "demo_sim" }
            });
            await fetchState();
        } catch (e) {
            console.error("Failed to start", e);
            alert("Failed to start simulation. Check backend console.");
        } finally {
            setLoading(false);
        }
    };

    // Auto-start simulation logic
    useEffect(() => {
        if (!hasStarted && !loading) {
            handleStart();
        }
    }, [hasStarted, loading]);

    if (!hasStarted) {
        return (
            <div className="h-screen w-full bg-slate-50 flex items-center justify-center p-6">
                <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center border border-slate-200">
                    <div className="w-16 h-16 bg-black rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg animate-pulse">
                        <span className="text-white text-2xl font-bold">E</span>
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-2">Setting up Environment...</h1>
                    <p className="text-slate-500 mb-8">
                        The AI Manager is generating your onboarding tasks. Please wait.
                    </p>

                    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-4 overflow-hidden">
                        <div className="bg-black h-2.5 rounded-full animate-progress" style={{ width: '45%' }}></div>
                    </div>

                    <p className="text-xs text-slate-400">
                        *This typically takes 5-10 seconds.
                    </p>
                </div>
                <style jsx>{`
                    @keyframes progress {
                        0% { width: 0%; }
                        50% { width: 70%; }
                        100% { width: 100%; }
                    }
                    .animate-progress {
                        animation: progress 2s infinite ease-in-out;
                    }
                `}</style>
            </div>
        );
    }

    return (
        <WorkspaceLayout
            activeApp={activeApp}
            onSwitchApp={setActiveApp}
            gameState={gameState}
        >
            {activeApp === 'email' && (
                <EmailClient
                    emails={gameState.emails}
                    onReply={handleReplyEmail}
                />
            )}

            {activeApp === 'ide' && (
                <CodeEditor
                    code={code}
                    setCode={setCode}
                    onSubmit={handleSubmitCode}
                />
            )}

            {activeApp === 'kanban' && (
                <TaskBoard
                    tasks={gameState.tasks}
                />
            )}

            {activeApp === 'team' && (
                <TeamView
                    members={gameState.team_members || []}
                    onChat={handleTeamChat}
                />
            )}

            {activeApp === 'analytics' && (
                <AnalyticsDashboard
                    gameState={gameState}
                />
            )}
        </WorkspaceLayout>
    );
};

export default EduCorpPage;
