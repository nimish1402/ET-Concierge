"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Zap, ArrowLeft, CheckCircle2 } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "👋 Hi there! I'm ET AI Concierge — your personal financial guide powered by Economic Times.\n\nI'd love to understand your financial goals so I can recommend the best tools and services from our ecosystem.\n\nTo start, could you tell me your name and rough age group?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [profileComplete, setProfileComplete] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Load userId from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("et_user_id");
    if (stored) {
      setUserId(stored);
      setProfileComplete(true);
    }
  }, []);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const newHistory = [...messages, { role: "user" as const, content: text }];
    setMessages(newHistory);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        user_id: userId,
        message: text,
        history: messages, // send full history
      });

      const { reply, user_id, profile_complete } = res.data;

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply },
      ]);

      if (user_id && !userId) {
        setUserId(user_id);
        localStorage.setItem("et_user_id", user_id);
      }

      if (profile_complete) {
        setProfileComplete(true);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ I encountered an issue. Please make sure the backend is running on port 8000.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [input, isLoading, messages, userId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#0f172a]">
      {/* ── Header ── */}
      <div className="glass border-b border-white/5 px-6 py-4 flex items-center gap-3">
        <Link href="/" className="text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="w-9 h-9 rounded-xl bg-orange-500/20 flex items-center justify-center">
          <Zap className="w-5 h-5 text-orange-500" fill="currentColor" />
        </div>
        <div>
          <div className="font-semibold text-sm">ET AI Concierge</div>
          <div className="text-xs text-slate-400">Powered by Groq llama3 + Gemini</div>
        </div>

        {profileComplete && (
          <div className="ml-auto flex items-center gap-2 text-green-400 text-xs font-medium">
            <CheckCircle2 className="w-4 h-4" />
            Profile Complete
            <Link
              href="/dashboard"
              className="ml-2 bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-full text-xs transition-colors"
            >
              View Dashboard →
            </Link>
          </div>
        )}
      </div>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"} max-w-3xl mx-auto`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white
                  ${msg.role === "assistant" ? "bg-orange-500/80" : "bg-slate-600"}`}
              >
                {msg.role === "assistant" ? (
                  <Bot className="w-4 h-4" />
                ) : (
                  <User className="w-4 h-4" />
                )}
              </div>

              {/* Bubble */}
              <div
                className={`max-w-[75%] px-5 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                  ${msg.role === "assistant"
                    ? "glass text-slate-200 rounded-tl-sm"
                    : "bg-orange-500/90 text-white rounded-tr-sm"
                  }`}
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 max-w-3xl mx-auto"
          >
            <div className="w-8 h-8 rounded-full bg-orange-500/80 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="glass px-5 py-4 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1.5 items-center">
                <div className="w-2 h-2 rounded-full bg-orange-400 dot" />
                <div className="w-2 h-2 rounded-full bg-orange-400 dot" />
                <div className="w-2 h-2 rounded-full bg-orange-400 dot" />
              </div>
            </div>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Input ── */}
      <div className="glass border-t border-white/5 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message… (Enter to send, Shift+Enter for new line)"
            rows={1}
            className="flex-1 bg-slate-800/60 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-500 resize-none outline-none focus:border-orange-500/50 transition-colors"
            style={{ maxHeight: "120px", overflowY: "auto" }}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="w-11 h-11 bg-orange-500 hover:bg-orange-600 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-xl flex items-center justify-center transition-colors flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-center text-xs text-slate-600 mt-2">
          ET AI Concierge may make mistakes. Always verify financial advice with a professional.
        </p>
      </div>
    </div>
  );
}
