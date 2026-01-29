"use client";

import React, { useState } from 'react';

const LearningPackModal = ({ isOpen, onClose, skillName, context }) => {
    const [loading, setLoading] = useState(false);
    const [pack, setPack] = useState(null);
    const [activeTab, setActiveTab] = useState('notes');
    const [quizAnswers, setQuizAnswers] = useState({});
    const [feedback, setFeedback] = useState(null);
    const [error, setError] = useState(null);

    const generatePack = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/api/learning-pack/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    skill_name: skillName,
                    context: context || { confidence: 50 }
                })
            });
            const data = await res.json();

            // Validate response has content
            if (!data.notes || data.notes.length === 0) {
                setError("AI could not generate notes. Please try again.");
                return;
            }

            setPack(data);
        } catch (e) {
            console.error("Failed to generate pack", e);
            setError("Failed to connect to AI. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const submitQuiz = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/learning-pack/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    skill_name: skillName,
                    submission: { answers: quizAnswers }
                })
            });
            const data = await res.json();
            setFeedback(data);
        } catch (e) {
            console.error("Failed to submit quiz", e);
        }
    };

    // Auto-generate on open if not present
    React.useEffect(() => {
        if (isOpen && !pack && !loading) {
            generatePack();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white text-black p-6 rounded-lg w-full max-w-4xl h-[80vh] flex flex-col shadow-2xl">

                {/* Header */}
                <div className="flex justify-between items-center mb-4 border-b pb-2">
                    <h2 className="text-2xl font-bold">🎓 Smart Learning Pack: {skillName}</h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-black text-2xl">&times;</button>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <p className="text-gray-600 text-lg animate-pulse">
                            Agentic AI is crafting your personalized content...
                        </p>
                        <div className="text-sm text-gray-500">
                            (Generating Notes → Designing Quiz → Creating Flashcards)
                        </div>
                    </div>
                )}

                {/* Error State */}
                {!loading && error && (
                    <div className="flex-1 flex flex-col items-center justify-center space-y-4">
                        <div className="text-red-500 text-6xl">⚠️</div>
                        <p className="text-gray-700 text-lg">{error}</p>
                        <button
                            onClick={() => { setError(null); generatePack(); }}
                            className="bg-blue-600 text-white px-6 py-2 rounded-full font-bold hover:bg-blue-700 transition"
                        >
                            Retry
                        </button>
                    </div>
                )}

                {/* Content */}
                {!loading && !error && pack && (
                    <div className="flex flex-col flex-1 overflow-hidden">
                        {/* Tabs */}
                        <div className="flex space-x-4 mb-4 border-b">
                            {['notes', 'quiz', 'flashcards'].map(tab => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`py-2 px-4 capitalize font-semibold ${activeTab === tab ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
                                >
                                    {tab}
                                </button>
                            ))}
                        </div>

                        <div className="flex-1 overflow-y-auto pr-2">
                            {/* Notes Tab */}
                            {activeTab === 'notes' && (
                                <div className="space-y-6">
                                    {pack.notes.map((note, idx) => (
                                        <div key={idx} className="bg-gray-50 p-4 rounded border-l-4 border-blue-500">
                                            <h3 className="font-bold text-lg mb-2">{note.title}</h3>
                                            <p className="whitespace-pre-line text-gray-700">{note.content}</p>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Quiz Tab */}
                            {activeTab === 'quiz' && (
                                <div className="space-y-6">
                                    {!feedback ? (
                                        <>
                                            {pack.quiz.map(q => (
                                                <div key={q.id} className="p-4 border rounded">
                                                    <p className="font-semibold mb-3">{q.question}</p>
                                                    <div className="space-y-2">
                                                        {q.options.map(opt => (
                                                            <label key={opt.label} className="flex items-center space-x-2 cursor-pointer p-2 hover:bg-gray-50 rounded">
                                                                <input
                                                                    type="radio"
                                                                    name={q.id}
                                                                    value={opt.label}
                                                                    onChange={(e) => setQuizAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                                                                    checked={quizAnswers[q.id] === opt.label}
                                                                />
                                                                <span>{opt.text}</span>
                                                            </label>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                            <button
                                                onClick={submitQuiz}
                                                className="w-full bg-blue-600 text-white py-3 rounded font-bold hover:bg-blue-700 transition"
                                            >
                                                Submit Quiz
                                            </button>
                                        </>
                                    ) : (
                                        <div className="space-y-8 pb-8">
                                            {/* Score Header */}
                                            <div className="bg-green-50 p-6 rounded text-center border border-green-100">
                                                <h3 className="text-3xl font-bold text-green-700 mb-2">
                                                    Score: {feedback.score} / {feedback.total}
                                                </h3>
                                                <p className="text-xl mb-4 italic text-gray-700">"{feedback.feedback}"</p>
                                                <div className="bg-white p-4 rounded inline-block shadow-sm text-left max-w-lg border border-green-100">
                                                    <strong className="block mb-1 text-green-800">Agent Recommendation:</strong>
                                                    {feedback.recommendation}
                                                </div>
                                            </div>

                                            {/* Question Review */}
                                            <div>
                                                <h3 className="text-xl font-bold border-b pb-2 mb-4">Detailed Review</h3>
                                                <div className="space-y-4">
                                                    {pack.quiz.map(q => {
                                                        const userAnswer = quizAnswers[q.id];
                                                        const isCorrect = userAnswer === q.correctAnswer;
                                                        return (
                                                            <div key={q.id} className={`p-4 border rounded-lg ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                                                                <p className="font-semibold mb-3 text-lg">{q.question}</p>

                                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-3">
                                                                    <div className={`p-2 rounded ${isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                                        <span className="font-bold">Your Answer: </span>
                                                                        {userAnswer ? q.options.find(o => o.label === userAnswer)?.text : "Skipped"}
                                                                        {isCorrect ? " ✅" : " ❌"}
                                                                    </div>
                                                                    {!isCorrect && (
                                                                        <div className="bg-green-100 text-green-800 p-2 rounded">
                                                                            <span className="font-bold">Correct Answer: </span>
                                                                            {q.options.find(o => o.label === q.correctAnswer)?.text}
                                                                        </div>
                                                                    )}
                                                                </div>

                                                                {q.explanation && (
                                                                    <div className="mt-3 text-gray-700 text-sm bg-white p-3 rounded border border-gray-200 shadow-sm">
                                                                        <strong className="text-blue-600">💡 Explanation: </strong>{q.explanation}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>

                                            <button
                                                onClick={() => { setFeedback(null); setQuizAnswers({}); }}
                                                className="block w-full bg-gray-800 text-white py-3 rounded font-bold hover:bg-black transition"
                                            >
                                                Retake Quiz
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Flashcards Tab */}
                            {activeTab === 'flashcards' && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {pack.flashcards.map((card, idx) => (
                                        <div
                                            key={idx}
                                            className="group h-48 cursor-pointer"
                                            style={{ perspective: '1000px' }}
                                            onClick={(e) => {
                                                const target = e.currentTarget.firstChild;
                                                const isFlipped = target.style.transform === 'rotateY(180deg)';
                                                target.style.transform = isFlipped ? 'rotateY(0deg)' : 'rotateY(180deg)';
                                            }}
                                        >
                                            <div className="relative w-full h-full transition-transform duration-500 transform border rounded shadow-md"
                                                style={{ transformStyle: 'preserve-3d' }}>

                                                {/* Front */}
                                                <div className="absolute inset-0 bg-white flex items-center justify-center p-4"
                                                    style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden' }}>
                                                    <p className="font-bold text-center text-lg">{card.front}</p>
                                                    <span className="absolute bottom-2 right-2 text-xs text-gray-400">Click to flip</span>
                                                </div>
                                                {/* Back */}
                                                <div className="absolute inset-0 bg-blue-600 text-white flex items-center justify-center p-4 rounded"
                                                    style={{ backfaceVisibility: 'hidden', WebkitBackfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}>
                                                    <p className="text-center">{card.back}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LearningPackModal;
