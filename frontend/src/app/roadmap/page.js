import PlannerDashboard from "@/components/PlannerDashboard";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function PlannerPage() {
    return (
        <main className="min-h-screen bg-white">
            {/* Header */}
            <header className="border-b border-neutral-200">
                <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
                    <Link href="/" className="text-xl font-semibold text-black">EduCorp</Link>
                    <nav className="flex gap-6 text-sm">
                        <Link href="/skills" className="text-neutral-500 hover:text-black">Skills</Link>
                        <Link href="/roadmap" className="text-black font-medium">Roadmap</Link>
                        <Link href="/interview" className="text-neutral-500 hover:text-black">Interview</Link>
                        <Link href="/educorp" className="text-neutral-500 hover:text-black">Simulation</Link>
                    </nav>
                </div>
            </header>

            {/* Content */}
            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/" className="text-neutral-400 hover:text-black">
                        <ArrowLeft size={20} />
                    </Link>
                    <h1 className="text-2xl font-semibold text-black">Roadmap</h1>
                </div>
                <PlannerDashboard />
            </div>
        </main>
    );
}
