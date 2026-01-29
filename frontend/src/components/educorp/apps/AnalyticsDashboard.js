import React from 'react';
import { Target, Mail, Award, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

const AnalyticsDashboard = ({ gameState }) => {
    // Derived Metrics
    const completedTasks = gameState.tasks.filter(t => t.status === 'done').length;
    const totalTasks = gameState.tasks.length;
    const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

    const emailReplies = gameState.logs.filter(l => l.includes("Replied to")).length;
    const totalEmails = gameState.emails.length;
    const responseRate = totalEmails > 0 ? (emailReplies / totalEmails) * 100 : 0;

    const getGrade = (score) => {
        if (score >= 90) return { grade: 'A+', color: 'text-green-600', text: 'Exceptional' };
        if (score >= 80) return { grade: 'A', color: 'text-green-500', text: 'Excellent' };
        if (score >= 70) return { grade: 'B', color: 'text-blue-500', text: 'Good' };
        if (score >= 50) return { grade: 'C', color: 'text-yellow-500', text: 'Average' };
        return { grade: 'D', color: 'text-red-500', text: 'At Risk' };
    };

    const gradeInfo = getGrade(gameState.trust_score);

    return (
        <div className="h-full max-w-5xl mx-auto p-2">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-neutral-900 mb-2">Performance Analytics</h1>
                <p className="text-neutral-500">Real-time breakdown of your internship performance.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Main Score Card */}
                <div className="md:col-span-2 bg-white rounded-xl border border-neutral-200 shadow-sm p-8 flex items-center justify-between overflow-hidden relative">
                    <div className="relative z-10">
                        <div className="uppercase tracking-widest text-xs font-bold text-neutral-500 mb-2">Overall Performance Rating</div>
                        <div className={`text-6xl font-black ${gradeInfo.color} mb-2`}>{gradeInfo.grade}</div>
                        <div className="text-lg font-medium text-neutral-800">{gradeInfo.text}</div>
                        <p className="text-neutral-500 text-sm mt-2 max-w-sm">
                            Your current standing based on code quality, communication, and timeliness.
                        </p>
                    </div>

                    {/* Visual Circle Gauge */}
                    <div className="relative w-40 h-40 flex-shrink-0">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                className="fill-none stroke-neutral-100"
                                strokeWidth="12"
                            />
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                className={`fill-none ${gradeInfo.color.replace('text', 'stroke')} transition-all duration-1000 ease-out`}
                                strokeWidth="12"
                                strokeDasharray="283" // 2 * pi * 45
                                strokeDashoffset={283 - (283 * gameState.trust_score) / 100}
                                strokeLinecap="round"
                            />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center flex-col">
                            <span className="text-3xl font-bold text-neutral-900">{gameState.trust_score}</span>
                            <span className="text-[10px] text-neutral-500 bg-white px-1">TRUST SCORE</span>
                        </div>
                    </div>

                    {/* Decor */}
                    <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-full -mr-16 -mt-16 z-0" />
                </div>

                {/* Status Card */}
                <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6 flex flex-col justify-center">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                            <TrendingUp size={20} />
                        </div>
                        <div className="font-bold text-neutral-900">Career Trajectory</div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-neutral-500">Goal Progress</span>
                            <span className="font-bold text-neutral-900">{Math.round(progress)}%</span>
                        </div>
                        <div className="w-full bg-neutral-100 rounded-full h-2">
                            <div className="bg-indigo-600 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                        </div>

                        <div className="flex justify-between items-center text-sm">
                            <span className="text-neutral-500">Comm. Efficiency</span>
                            <span className="font-bold text-neutral-900">{Math.round(responseRate)}%</span>
                        </div>
                        <div className="w-full bg-neutral-100 rounded-full h-2">
                            <div className="bg-cyan-500 h-2 rounded-full transition-all duration-500" style={{ width: `${responseRate}%` }}></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-neutral-700">Tasks Completed</h3>
                        <CheckCircle size={20} className="text-green-500" />
                    </div>
                    <div className="text-4xl font-bold text-neutral-900 mb-1">{completedTasks}</div>
                    <div className="text-xs text-neutral-500">out of {totalTasks} assigned</div>
                </div>

                <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-neutral-700">Emails Handled</h3>
                        <Mail size={20} className="text-blue-500" />
                    </div>
                    <div className="text-4xl font-bold text-neutral-900 mb-1">{emailReplies}</div>
                    <div className="text-xs text-neutral-500">out of {totalEmails} received</div>
                </div>

                <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-neutral-700">Manager Trust</h3>
                        <Award size={20} className="text-amber-500" />
                    </div>
                    <div className="text-4xl font-bold text-neutral-900 mb-1">{gameState.trust_score}</div>
                    <div className="text-xs text-neutral-500">Current trust level</div>
                </div>
            </div>

            {gameState.trust_score < 50 && (
                <div className="mt-8 bg-red-50 border border-red-100 rounded-xl p-4 flex items-start gap-3">
                    <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
                    <div>
                        <h4 className="font-bold text-red-800 text-sm">Performance Alert</h4>
                        <p className="text-red-600 text-sm mt-1">Your trust score is critically low. Focus on completing tasks accurately and replying to emails promptly to avoid termination.</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyticsDashboard;
