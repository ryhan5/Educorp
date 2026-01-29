import React, { useState } from 'react';
import { LayoutGrid, Mail, Code2, Users, Settings, Bell, ChevronRight, PieChart, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const WorkspaceLayout = ({ children, activeApp, onSwitchApp, gameState }) => {

    const menuItems = [
        { id: 'email', icon: <Mail size={20} />, label: 'Messages', count: gameState?.emails?.length || 0 },
        { id: 'kanban', icon: <LayoutGrid size={20} />, label: 'Tasks', count: gameState?.tasks?.length || 0 },
        { id: 'ide', icon: <Code2 size={20} />, label: 'Development', count: 0 },
    ];

    return (
        <div className="flex h-screen w-full bg-white text-neutral-900 overflow-hidden font-sans">

            {/* Sidebar Rail */}
            <div className="w-64 border-r border-neutral-200 flex flex-col bg-neutral-50">

                {/* Brand */}
                <div className="h-16 flex items-center px-6 border-b border-neutral-200">
                    <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center text-white font-bold mr-3 shadow-sm">
                        E
                    </div>
                    <div>
                        <div className="font-bold text-black tracking-tight">EduCorp UI</div>
                        <div className="text-[10px] text-neutral-500 uppercase tracking-wider font-semibold">Workspace</div>
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex-1 py-6 px-3 space-y-1">
                    <div className="text-xs font-semibold text-neutral-500 px-3 mb-2 uppercase tracking-wider">Apps</div>
                    {menuItems.map(item => (
                        <button
                            key={item.id}
                            onClick={() => onSwitchApp(item.id)}
                            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-all duration-200 group ${activeApp === item.id ? 'bg-white text-black shadow-sm ring-1 ring-neutral-200' : 'hover:bg-neutral-200/50 text-neutral-500 hover:text-black'}`}
                        >
                            <div className="flex items-center gap-3">
                                <span className={activeApp === item.id ? 'text-black' : 'opacity-70 group-hover:opacity-100'}>{item.icon}</span>
                                <span className="text-sm font-medium">{item.label}</span>
                            </div>
                            {item.count > 0 && (
                                <span className={`text-[10px] font-bold px-1.5 min-w-[1.2rem] py-0.5 rounded-md ${activeApp === item.id ? 'bg-black text-white' : 'bg-neutral-200 text-neutral-600'}`}>
                                    {item.count}
                                </span>
                            )}
                        </button>
                    ))}

                    <div className="mt-8 text-xs font-semibold text-neutral-500 px-3 mb-2 uppercase tracking-wider">System</div>
                    <button
                        onClick={() => onSwitchApp('analytics')}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${activeApp === 'analytics' ? 'bg-white text-black shadow-sm ring-1 ring-neutral-200' : 'hover:bg-neutral-200/50 text-neutral-500 hover:text-black'}`}
                    >
                        <PieChart size={20} className={activeApp === 'analytics' ? 'text-black' : 'opacity-70'} />
                        <span className="text-sm font-medium">Analytics</span>
                    </button>
                    <button
                        onClick={() => onSwitchApp('team')}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${activeApp === 'team' ? 'bg-white text-black shadow-sm ring-1 ring-neutral-200' : 'hover:bg-neutral-200/50 text-neutral-500 hover:text-black'}`}
                    >
                        <Users size={20} className={activeApp === 'team' ? 'text-black' : 'opacity-70'} />
                        <span className="text-sm font-medium">Team</span>
                    </button>

                    <div className="flex-1" />

                    <a href="/" className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-50 text-neutral-500 hover:text-red-600 transition-colors mt-4">
                        <LogOut size={20} className="opacity-70" />
                        <span className="text-sm font-medium">Exit Simulation</span>
                    </a>
                </div>

                {/* User Profile */}
                <div className="p-4 border-t border-neutral-200 bg-neutral-100/50">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-500 p-[1px]">
                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" className="w-full h-full rounded-full bg-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-black truncate">Intern User</div>
                            <div className="text-xs text-neutral-500 truncate">Junior Developer • Day {gameState?.day || 1}</div>
                        </div>
                    </div>

                    {/* Trust Score Bar */}
                    <div>
                        <div className="flex justify-between text-[10px] uppercase font-bold text-neutral-500 mb-1">
                            <span>Trust Score</span>
                            <span className={gameState?.trust_score < 40 ? "text-red-500" : "text-green-600"}>{gameState?.trust_score || 0}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full transition-all duration-500 ${gameState?.trust_score < 40 ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${gameState?.trust_score}%` }}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-white relative">

                {/* Background ambient glow - Made subtle for light theme */}
                <div className="absolute top-0 left-0 w-full h-64 bg-blue-500/5 blur-[100px] pointer-events-none" />

                {/* Content Container */}
                <main className="flex-1 p-6 overflow-hidden relative z-10 text-black">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={activeApp}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                            className="h-full"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>

        </div>
    );
};

export default WorkspaceLayout;
