import Link from "next/link";
import { Brain, Map, MessageSquare, Monitor } from "lucide-react";

const features = [
  {
    title: "Skill Digital Twin",
    description: "Analyze your profile and visualize your skills",
    href: "/skills",
    icon: Brain
  },
  {
    title: "Roadmap",
    description: "Generate learning mindmaps for any topic",
    href: "/roadmap",
    icon: Map
  },
  {
    title: "Interview",
    description: "Practice with AI interview simulations",
    href: "/interview",
    icon: MessageSquare
  },
  {
    title: "Simulation",
    description: "Experience a realistic work environment",
    href: "/educorp",
    icon: Monitor
  }
];

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-neutral-200">
        <div className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-black">EduCorp</h1>
          <nav className="flex gap-6 text-sm">
            <Link href="/skills" className="text-neutral-500 hover:text-black">Skills</Link>
            <Link href="/roadmap" className="text-neutral-500 hover:text-black">Roadmap</Link>
            <Link href="/interview" className="text-neutral-500 hover:text-black">Interview</Link>
            <Link href="/educorp" className="text-neutral-500 hover:text-black">Simulation</Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 py-20 text-center">
        <h2 className="text-4xl font-semibold text-black mb-4">
          AI-Powered Learning Platform
        </h2>
        <p className="text-neutral-500 text-lg max-w-xl mx-auto">
          Build your skill profile, plan your learning, and practice with AI
        </p>
      </section>

      {/* Features Grid */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <div className="grid md:grid-cols-2 gap-4">
          {features.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className="border border-neutral-200 rounded-xl p-6 hover:border-neutral-300 hover:bg-neutral-50 transition-all group"
            >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center group-hover:bg-neutral-200 transition-colors">
                  <feature.icon size={20} className="text-neutral-600" />
                </div>
                <div>
                  <h3 className="font-medium text-black mb-1">{feature.title}</h3>
                  <p className="text-sm text-neutral-500">{feature.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
