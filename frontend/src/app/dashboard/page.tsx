"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  BarChart3,
  User,
  Target,
  Heart,
  TrendingUp,
  ExternalLink,
  RefreshCw,
  Zap,
  ArrowLeft,
  Shield,
  Award,
  MessageCircle,
} from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface UserProfile {
  id: string;
  name: string;
  persona: string;
  risk_level: string;
  goals: string[];
  interests: string[];
  recommended_products: string[];
  created_at: string;
}

interface Recommendation {
  product: string;
  reason: string;
  score: number;
  category?: string;
  url?: string;
}

const riskColors: Record<string, string> = {
  conservative: "text-blue-400 bg-blue-400/10 border-blue-400/30",
  moderate: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
  aggressive: "text-red-400 bg-red-400/10 border-red-400/30",
};

const personaEmoji: Record<string, string> = {
  student: "🎓",
  young_professional: "💼",
  mid_career: "🏆",
  pre_retiree: "🌅",
  retiree: "🏡",
  business_owner: "🚀",
};

export default function DashboardPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("et_user_id");
    if (stored) {
      setUserId(stored);
      fetchData(stored);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchData = async (uid: string) => {
    try {
      const [profileRes, recRes] = await Promise.all([
        axios.get(`${API_URL}/user/${uid}`),
        axios.get(`${API_URL}/recommendations?user_id=${uid}`),
      ]);
      setProfile(profileRes.data);
      setRecommendations(recRes.data.recommendations || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load data.");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!userId) return;
    setRefreshing(true);
    try {
      await axios.post(`${API_URL}/recommendations/refresh?user_id=${userId}`);
      await fetchData(userId);
    } catch {
      /* ignore */
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-2 border-orange-500 border-t-transparent animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  if (!userId || error) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center px-6">
        <div className="text-center glass rounded-3xl p-12 max-w-md">
          <MessageCircle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-3">No Profile Found</h2>
          <p className="text-slate-400 mb-6">
            {error || "Complete your onboarding chat to see your personalized dashboard."}
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-xl font-semibold transition-colors"
          >
            Start AI Chat →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-white">
      {/* ── Nav ── */}
      <nav className="glass border-b border-white/5 px-6 py-4 flex items-center gap-3 sticky top-0 z-10">
        <Link href="/" className="text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <Zap className="w-5 h-5 text-orange-500" fill="currentColor" />
        <span className="font-semibold">My Financial Dashboard</span>
        <div className="ml-auto flex items-center gap-3">
          <Link href="/chat" className="text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1">
            <MessageCircle className="w-4 h-4" /> Chat
          </Link>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 text-sm bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 px-4 py-2 rounded-xl transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
        {/* ── Profile Card ── */}
        {profile && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-8"
          >
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="w-20 h-20 rounded-2xl bg-orange-500/10 flex items-center justify-center text-4xl flex-shrink-0">
                {personaEmoji[profile.persona] || "👤"}
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold">
                  {profile.name || "Financial Profile"}
                </h1>
                <p className="text-slate-400 capitalize mt-1">
                  {profile.persona?.replace("_", " ")}
                </p>
              </div>
              <div
                className={`px-4 py-2 rounded-xl border text-sm font-semibold capitalize ${riskColors[profile.risk_level] || "text-slate-400 bg-slate-400/10 border-slate-400/30"}`}
              >
                <Shield className="w-4 h-4 inline mr-1" />
                {profile.risk_level} Risk
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <div>
                <div className="flex items-center gap-2 text-slate-400 text-sm font-medium mb-3">
                  <Target className="w-4 h-4" /> Financial Goals
                </div>
                <div className="flex flex-wrap gap-2">
                  {profile.goals?.map((g, i) => (
                    <span key={i} className="bg-slate-800 text-slate-300 text-xs px-3 py-1.5 rounded-full border border-white/5">
                      {g}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2 text-slate-400 text-sm font-medium mb-3">
                  <Heart className="w-4 h-4" /> Interests
                </div>
                <div className="flex flex-wrap gap-2">
                  {profile.interests?.map((interest, i) => (
                    <span key={i} className="bg-orange-500/10 text-orange-300 text-xs px-3 py-1.5 rounded-full border border-orange-500/20">
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ── Recommendations ── */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            <h2 className="text-xl font-bold">AI Recommendations</h2>
            <span className="text-xs text-slate-500 ml-auto">Sorted by AI relevance score</span>
          </div>

          {recommendations.length === 0 ? (
            <div className="glass rounded-2xl p-8 text-center text-slate-400">
              <Award className="w-10 h-10 mx-auto mb-3 opacity-40" />
              No recommendations yet. Click Refresh to generate.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((rec, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.07 }}
                  className="glass rounded-2xl p-6 flex flex-col gap-4 hover:border-orange-500/30 transition-colors group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="font-semibold text-sm leading-snug">{rec.product}</h3>
                    <div className="flex-shrink-0 text-xs font-bold text-orange-400 bg-orange-400/10 px-2 py-1 rounded-lg">
                      {rec.score?.toFixed(0)}pt
                    </div>
                  </div>

                  {/* Score bar */}
                  <div className="w-full bg-slate-800 rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-orange-500 to-yellow-400 h-1.5 rounded-full transition-all"
                      style={{ width: `${Math.min((rec.score / 100) * 100, 100)}%` }}
                    />
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed flex-1">
                    {rec.reason || "Matched to your profile and interests."}
                  </p>

                  {rec.url && (
                    <a
                      href={rec.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-xs text-orange-400 hover:text-orange-300 transition-colors mt-auto"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      Explore on ET
                    </a>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* ── User ID info ── */}
        <div className="text-center text-xs text-slate-600 pb-4">
          User session: {userId} &nbsp;·&nbsp;
          <button
            onClick={() => {
              localStorage.removeItem("et_user_id");
              window.location.href = "/chat";
            }}
            className="underline hover:text-slate-400 transition-colors"
          >
            Start new session
          </button>
        </div>
      </div>
    </div>
  );
}
