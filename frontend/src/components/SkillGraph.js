"use client";

import React, { useEffect } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';

const SkillGraph = ({ initialNodes = [], initialEdges = [] }) => {
    // We still use hooks to manage internal state (dragging etc)
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // Update internal state when props change
    useEffect(() => {
        setNodes(initialNodes);
        setEdges(initialEdges);
    }, [initialNodes, initialEdges, setNodes, setEdges]);

    const [selectedSkill, setSelectedSkill] = React.useState(null);

    return (
        <div style={{ padding: '20px', background: '#fff', borderRadius: '12px', border: '1px solid #e5e5e5' }}>
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold">Skill Digital Twin Graph</h3>
                <button
                    onClick={() => setSelectedSkill({ name: "React Graph", confidence: 60 })} // Mock selection for demo
                    className="bg-purple-600 text-white px-4 py-2 rounded-full font-bold shadow hover:bg-purple-700 transition flex items-center gap-2"
                >
                    <span>🎓</span> Generate Smart Learning Pack
                </button>
            </div>

            <div style={{ width: '100%', height: '500px', border: '1px solid #ddd', borderRadius: '8px' }}>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    fitView
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                </ReactFlow>
            </div>

            {/* Smart Learning Pack Modal */}
            {selectedSkill && (
                <LearningPackModal
                    isOpen={!!selectedSkill}
                    onClose={() => setSelectedSkill(null)}
                    skillName={selectedSkill.name}
                    context={{ confidence: selectedSkill.confidence }}
                />
            )}
        </div>
    );
};

// Lazy load modal to avoid ssr issues if any
import dynamic from 'next/dynamic';
const LearningPackModal = dynamic(() => import('./LearningPackModal'), { ssr: false });

export default SkillGraph;
