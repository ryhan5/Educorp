import SkillAnalyzer from "@/components/SkillAnalyzer";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function SkillsPage() {
    return (
        <main className="min-h-screen bg-white">
            {/* Header */}
            <header className="border-b border-neutral-200">
                <div className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
                    <Link href="/" className="text-xl font-semibold text-black">EduCorp</Link>
                    <nav className="flex gap-6 text-sm">
                        <Link href="/skills" className="text-black font-medium">Skills</Link>
                        <Link href="/roadmap" className="text-neutral-500 hover:text-black">Roadmap</Link>
                        <Link href="/interview" className="text-neutral-500 hover:text-black">Interview</Link>
                        <Link href="/educorp" className="text-neutral-500 hover:text-black">Simulation</Link>
                    </nav>
                </div>
            </header>

            {/* Content */}
            <div className="max-w-4xl mx-auto px-6 py-8">
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/" className="text-neutral-400 hover:text-black">
                        <ArrowLeft size={20} />
                    </Link>
                    <h1 className="text-2xl font-semibold text-black">Skill Digital Twin</h1>
                </div>
                <SkillAnalyzer />
            </div>
        </main>
    );
}
