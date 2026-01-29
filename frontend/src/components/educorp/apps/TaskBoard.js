import React from 'react';
import { MoreHorizontal, Plus, Clock, CheckCircle2, Circle } from 'lucide-react';

const TaskBoard = ({ tasks }) => {

    // Group tasks (simplified logic, usually would be stateful for drag/drop)
    const columns = {
        todo: { title: 'To Do', icon: <Circle size={14} />, color: 'bg-slate-500' },
        in_progress: { title: 'In Progress', icon: <Clock size={14} className="text-blue-400" />, color: 'bg-blue-500' },
        done: { title: 'Done', icon: <CheckCircle2 size={14} className="text-green-400" />, color: 'bg-green-500' }
    };

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center justify-between mb-6 px-2">
                <h2 className="text-xl font-bold text-neutral-900 tracking-tight">Project Board</h2>
                <div className="flex gap-2">
                    <button className="text-xs bg-black text-white px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 hover:opacity-80 transition-opacity">
                        <Plus size={14} /> New Issue
                    </button>
                </div>
            </div>

            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden min-h-0">
                {Object.entries(columns).map(([status, config]) => (
                    <div key={status} className="flex flex-col h-full bg-neutral-50 rounded-xl border border-neutral-200">
                        {/* Column Header */}
                        <div className="p-3 flex items-center justify-between border-b border-neutral-200">
                            <div className="flex items-center gap-2">
                                <span className="opacity-80">{config.icon}</span>
                                <span className="text-sm font-semibold text-neutral-700">{config.title}</span>
                                <span className="text-xs bg-white text-neutral-500 px-1.5 py-0.5 rounded-full border border-neutral-200">
                                    {tasks.filter(t => t.status === status).length}
                                </span>
                            </div>
                            <button className="text-neutral-400 hover:text-neutral-600">
                                <MoreHorizontal size={14} />
                            </button>
                        </div>

                        {/* Drop Zone */}
                        <div className="flex-1 p-3 overflow-y-auto space-y-3 custom-scrollbar">
                            {tasks.filter(t => t.status === status).map(task => (
                                <div
                                    key={task.id}
                                    className="bg-white rounded-lg p-3 hover:-translate-y-0.5 transition-all cursor-grab group shadow-sm border border-neutral-200 hover:shadow-md"
                                >
                                    <div className="flex justify-between items-start mb-2 opacity-80 group-hover:opacity-100">
                                        <span className="text-[10px] font-mono text-neutral-500">TASK-{task.id.slice(0, 4)}</span>
                                        <div className={`w-2 h-2 rounded-full ${config.color}`}></div>
                                    </div>
                                    <div className="text-sm font-medium text-neutral-900 mb-2 leading-snug">
                                        {task.title}
                                    </div>
                                    <div className="flex items-center gap-2 text-xs text-neutral-500">
                                        <div className="flex -space-x-1.5">
                                            <div className="w-5 h-5 rounded-full bg-neutral-100 border border-white flex items-center justify-center text-[8px] text-neutral-600 font-bold">JD</div>
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {/* Empty State */}
                            {tasks.filter(t => t.status === status).length === 0 && (
                                <div className="h-24 border border-dashed border-neutral-300 rounded-lg flex items-center justify-center text-xs text-neutral-400">
                                    No cards
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TaskBoard;
