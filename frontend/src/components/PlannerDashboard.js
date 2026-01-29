"use client";

import React, { useState } from 'react';
import axios from 'axios';
import { Loader2, Search } from 'lucide-react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

const PlannerDashboard = () => {
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    const handleGenerate = async () => {
        if (!topic.trim()) return;
        setLoading(true);
        setError("");
        try {
            const res = await axios.post('http://localhost:8000/api/generate-mindmap', { topic });

            const backendNodes = res.data.nodes || [];
            const backendEdges = res.data.edges || [];

            const flowNodes = backendNodes.map((node, index) => ({
                id: node.id,
                position: { x: (index % 3) * 250, y: Math.floor(index / 3) * 150 },
                data: { label: node.label },
                type: node.type === 'root' ? 'input' : 'default',
                style: {
                    border: '1px solid #e5e5e5',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    background: node.type === 'root' ? '#0a0a0a' : '#ffffff',
                    color: node.type === 'root' ? '#ffffff' : '#0a0a0a',
                    fontSize: '13px',
                    fontWeight: '500',
                    minWidth: '120px',
                    textAlign: 'center'
                }
            }));

            const flowEdges = backendEdges.map(edge => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                markerEnd: { type: MarkerType.ArrowClosed, color: '#0a0a0a' },
                style: { stroke: '#0a0a0a', strokeWidth: 1.5 }
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);

        } catch (err) {
            console.error("Failed to generate mindmap", err);
            setError("Failed to generate mindmap.");
        } finally {
            setLoading(false);
        }
    };

    const [widgetData, setWidgetData] = useState(null);
    const [widgetLoading, setWidgetLoading] = useState(false);

    const onNodeClick = async (event, node) => {
        // Only generate for concept nodes, not root or resources
        if (node.type !== 'default') return;

        setWidgetLoading(true);
        setWidgetData(null);
        try {
            const res = await axios.post('http://localhost:8000/api/generate-widget', { topic: node.data.label });
            setWidgetData(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setWidgetLoading(false);
        }
    };

    const closeWidget = () => {
        setWidgetData(null);
        setWidgetLoading(false);
    };

    return (
        <div className="h-[700px] flex flex-col gap-6 relative">
            {/* Widget Modal */}
            {(widgetData || widgetLoading) && (
                <div className="absolute inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-6">
                    <div className="bg-white w-full max-w-4xl h-[85%] rounded-2xl shadow-2xl flex flex-col overflow-hidden relative animate-in fade-in zoom-in duration-200">

                        <div className="p-4 border-b border-neutral-200 flex justify-between items-center bg-white">
                            <div>
                                <h3 className="font-semibold text-lg">
                                    {widgetLoading ? "Generating Interactive Widget..." : widgetData?.name}
                                </h3>
                                {!widgetLoading && <p className="text-xs text-neutral-500">{widgetData?.description}</p>}
                            </div>
                            <button onClick={closeWidget} className="p-2 hover:bg-neutral-100 rounded-full">
                                <span className="text-xl">&times;</span>
                            </button>
                        </div>

                        <div className="flex-1 bg-neutral-100 relative">
                            {widgetLoading ? (
                                <div className="absolute inset-0 flex items-center justify-center flex-col gap-4 text-neutral-500">
                                    <Loader2 className="animate-spin text-black" size={40} />
                                    <p className="text-sm opacity-70">AI is coding your visualization...</p>
                                </div>
                            ) : (
                                <iframe
                                    srcDoc={widgetData?.html_content}
                                    className="w-full h-full border-none"
                                    title="Interactive Widget"
                                    style={{ background: 'white' }}
                                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                                />
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Search Bar */}
            <div className="flex gap-3">
                <div className="flex-1 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
                    <input
                        type="text"
                        className="w-full pl-12 pr-4 py-3.5 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black"
                        placeholder="Enter a topic (e.g., 'Docker for Beginners')..."
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
                    />
                </div>
                <button
                    onClick={handleGenerate}
                    disabled={loading || !topic.trim()}
                    className="bg-black text-white px-6 rounded-lg text-sm font-medium flex items-center gap-2 hover:opacity-90 disabled:opacity-40"
                >
                    {loading && <Loader2 className="animate-spin" size={16} />}
                    Generate
                </button>
            </div>

            {error && <p className="text-red-600 text-sm">{error}</p>}

            {/* Canvas */}
            <div className="flex-1 border border-neutral-200 rounded-xl overflow-hidden relative bg-white">
                {nodes.length === 0 && !loading && (
                    <div className="absolute inset-0 flex items-center justify-center text-neutral-400 text-sm z-10">
                        Enter a topic to generate mindmap
                    </div>
                )}

                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    fitView
                >
                    <Background color="#e5e5e5" gap={20} size={1} />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => node.type === 'input' ? '#0a0a0a' : '#e5e5e5'}
                    />
                </ReactFlow>
            </div>
        </div>
    );
};

export default PlannerDashboard;
