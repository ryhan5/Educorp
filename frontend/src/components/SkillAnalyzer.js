"use client";

import React, { useState } from 'react';
import axios from 'axios';
import SkillGraph from './SkillGraph';
import { Loader2 } from 'lucide-react';

const SkillAnalyzer = () => {
    const [text, setText] = useState('');
    const [githubUrl, setGithubUrl] = useState('');
    const [courseHistory, setCourseHistory] = useState('');
    const [assessments, setAssessments] = useState('');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [error, setError] = useState('');

    const handleAnalyze = async () => {
        setLoading(true);
        setError('');
        try {
            const formData = new FormData();
            if (text) formData.append('text', text);
            if (githubUrl) formData.append('github_url', githubUrl);
            if (courseHistory) formData.append('course_history', courseHistory);
            if (assessments) formData.append('assessments', assessments);
            if (file) formData.append('file', file);

            const response = await axios.post('http://localhost:8000/api/analyze-profile', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data && response.data.data) {
                setGraphData(response.data.data);
            }
        } catch (err) {
            console.error(err);
            setError('Failed to analyze profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            {/* Input Section */}
            <div className="border border-neutral-200 rounded-xl p-6 mb-8 bg-white shadow-sm">
                <h2 className="text-xl font-semibold text-black mb-6">Analyze Profile</h2>

                <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">Resume / Bio</label>
                            <textarea
                                className="w-full p-4 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black transition-colors resize-none h-32 bg-neutral-50"
                                placeholder="Describe your experience and skills..."
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">Upload Resume (PDF/DOCX)</label>
                            <input
                                type="file"
                                accept=".pdf,.docx,.txt"
                                className="w-full p-3 border border-neutral-200 rounded-lg text-sm bg-neutral-50 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-black file:text-white hover:file:opacity-90 cursor-pointer"
                                onChange={(e) => setFile(e.target.files[0])}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">GitHub URL</label>
                            <input
                                type="text"
                                className="w-full p-4 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black transition-colors bg-neutral-50"
                                placeholder="https://github.com/username"
                                value={githubUrl}
                                onChange={(e) => setGithubUrl(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">Course History</label>
                            <textarea
                                className="w-full p-4 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black transition-colors resize-none h-32 bg-neutral-50"
                                placeholder="List completed courses, certifications..."
                                value={courseHistory}
                                onChange={(e) => setCourseHistory(e.target.value)}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-2">Platform Assessments</label>
                            <textarea
                                className="w-full p-4 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:border-black transition-colors resize-none h-14 bg-neutral-50"
                                placeholder="Paste assessment results or quiz scores..."
                                value={assessments}
                                onChange={(e) => setAssessments(e.target.value)}
                            />
                        </div>
                    </div>
                </div>

                <div className="mt-8">
                    <button
                        onClick={handleAnalyze}
                        disabled={loading || (!text && !githubUrl && !courseHistory && !file)}
                        className="w-full bg-black text-white py-4 rounded-lg font-medium text-sm hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {loading && <Loader2 className="animate-spin w-4 h-4" />}
                        {loading ? 'Analyzing Profile Data...' : 'Generate Skill Twin'}
                    </button>

                    {error && (
                        <p className="text-red-600 text-sm mt-3 text-center">{error}</p>
                    )}
                </div>
            </div>

            {/* Graph Section */}
            <div className="grid lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                    <h3 className="text-lg font-medium text-black mb-4 flex items-center gap-2">
                        Skill Graph
                        <span className="text-xs font-normal text-neutral-500 bg-neutral-100 px-2 py-1 rounded-full">
                            {graphData.nodes.length > 0 ? `${graphData.nodes.length} nodes` : 'Empty'}
                        </span>
                    </h3>
                    {graphData.nodes.length > 0 ? (
                        <SkillGraph initialNodes={graphData.nodes} initialEdges={graphData.edges} />
                    ) : (
                        <div className="h-[500px] border border-dashed border-neutral-300 rounded-xl flex items-center justify-center text-neutral-400 text-sm bg-neutral-50">
                            Enter your details above to generate your Skill Digital Twin
                        </div>
                    )}
                </div>

                {/* Metrics Dashboard */}
                <div>
                    <h3 className="text-lg font-medium text-black mb-4">Skill Metrics</h3>
                    {graphData.nodes.filter(n => n.data.type === 'skill').length > 0 ? (
                        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                            <div className="p-4 bg-black text-white rounded-lg mb-4">
                                <div className="text-xs uppercase tracking-wider opacity-70 mb-1">Total Skills</div>
                                <div className="text-3xl font-bold">{graphData.nodes.filter(n => n.data.type === 'skill').length}</div>
                            </div>

                            {graphData.nodes
                                .filter(n => n.data.type === 'skill')
                                .sort((a, b) => b.data.confidence - a.data.confidence)
                                .map(node => (
                                    <div key={node.id} className="border border-neutral-200 rounded-lg p-4 bg-white hover:border-black transition-colors">
                                        <div className="font-semibold text-black mb-3">{node.data.label}</div>

                                        <div className="space-y-3">
                                            <div>
                                                <div className="flex justify-between text-xs mb-1">
                                                    <span className="text-neutral-500">Confidence</span>
                                                    <span className="font-medium">{node.data.confidence}%</span>
                                                </div>
                                                <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-black rounded-full" style={{ width: `${node.data.confidence}%` }}></div>
                                                </div>
                                            </div>

                                            <div>
                                                <div className="flex justify-between text-xs mb-1">
                                                    <span className="text-neutral-500">Depth</span>
                                                    <span className="font-medium">{node.data.depth}%</span>
                                                </div>
                                                <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-neutral-600 rounded-full" style={{ width: `${node.data.depth}%` }}></div>
                                                </div>
                                            </div>

                                            <div>
                                                <div className="flex justify-between text-xs mb-1">
                                                    <span className="text-neutral-500">Industry Relevance</span>
                                                    <span className="font-medium">{node.data.relevance || 50}%</span>
                                                </div>
                                                <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-neutral-400 rounded-full" style={{ width: `${node.data.relevance || 50}%` }}></div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                        </div>
                    ) : (
                        <div className="h-[200px] border border-neutral-200 rounded-xl flex items-center justify-center text-neutral-400 text-sm bg-neutral-50 p-6 text-center">
                            Metrics will appear here after analysis
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SkillAnalyzer;
