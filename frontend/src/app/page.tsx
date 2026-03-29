"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Brain,
  TrendingUp,
  ShieldCheck,
  Zap,
  ArrowRight,
  Star,
  MessageCircle,
  BarChart3,
  Wallet,
} from "lucide-react";

const features = [
  {
    icon: <MessageCircle className="w-6 h-6" />,
    title: "ET Welcome Concierge",
    desc: "A 3-minute AI conversation that builds your complete financial persona.",
  },
  {
    icon: <Brain className="w-6 h-6" />,
    title: "Financial Life Navigator",
    desc: "Ask any financial question — get RAG-powered answers personalized to your profile.",
  },
  {
    icon: <TrendingUp className="w-6 h-6" />,
    title: "Smart Recommendations",
    desc: "AI scores and ranks ET products based on your goals, interests, and behavior.",
  },
  {
    icon: <ShieldCheck className="w-6 h-6" />,
    title: "Services Marketplace",
    desc: "Find the right credit card, loan, or insurance matched by AI to your profile.",
  },
];

const stats = [
  { label: "ET Products", value: "50+" },
  { label: "Financial Articles", value: "1000+" },
  { label: "Satisfied Users", value: "10M+" },
  { label: "AI Accuracy", value: "94%" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#0f172a] text-white overflow-hidden">
      {/* ── Nav ── */}
      <nav className="fixed top-0 w-full z-50 glass border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-orange-500" fill="currentColor" />
            <span className="font-bold text-lg">
              <span className="gradient-text">ET</span> AI Concierge
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/chat"
              className="bg-orange-500 hover:bg-orange-600 text-white px-5 py-2 rounded-full text-sm font-semibold transition-all duration-200 shadow-lg shadow-orange-500/20"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-36 pb-24 px-6 relative">
        {/* BG glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-orange-500/10 rounded-full blur-3xl" />
        </div>

        <div className="max-w-4xl mx-auto text-center relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-block bg-orange-500/10 text-orange-400 text-sm font-medium px-4 py-1.5 rounded-full border border-orange-500/20 mb-6">
              ✨ Powered by Groq & Gemini AI
            </span>
            <h1 className="text-5xl md:text-7xl font-extrabold leading-tight mb-6">
              Your Personal{" "}
              <span className="gradient-text">Financial</span> AI
              <br />
              Concierge
            </h1>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-10">
              ET AI Concierge understands your financial goals in a 3-minute
              conversation and recommends exactly the right products, articles,
              and services from the ET ecosystem.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 rounded-2xl text-base font-semibold transition-all duration-200 shadow-xl shadow-orange-500/30 group"
              >
                Start Your AI Session
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 glass text-slate-300 hover:text-white px-8 py-4 rounded-2xl text-base font-semibold transition-all duration-200"
              >
                <BarChart3 className="w-5 h-5" />
                View Dashboard
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 + 0.3 }}
              className="glass rounded-2xl p-6 text-center"
            >
              <div className="text-3xl font-extrabold gradient-text">{s.value}</div>
              <div className="text-sm text-slate-400 mt-1">{s.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Everything you need, <span className="gradient-text">powered by AI</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 + 0.5 }}
                className="glass rounded-2xl p-8 hover:border-orange-500/30 transition-colors group cursor-pointer"
              >
                <div className="w-12 h-12 bg-orange-500/10 rounded-xl flex items-center justify-center text-orange-500 mb-4 group-hover:bg-orange-500/20 transition-colors">
                  {f.icon}
                </div>
                <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="py-20 px-6">
        <div className="max-w-2xl mx-auto text-center glass rounded-3xl p-12">
          <Wallet className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">
            Ready to take control of your finances?
          </h2>
          <p className="text-slate-400 mb-8">
            Join millions who trust ET for their financial decisions.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 rounded-2xl text-base font-semibold transition-all duration-200 shadow-xl shadow-orange-500/30"
          >
            Talk to ET Concierge
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-slate-500 text-sm">
        © {new Date().getFullYear()} Economic Times AI Concierge. Built with ❤️ using
        Groq, Gemini & Weaviate.
      </footer>
    </main>
  );
}
