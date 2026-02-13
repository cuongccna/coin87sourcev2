"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const success = await login(email);
    if (success) {
      router.push("/");
    } else {
      alert("Login Failed. Please try again.");
    }
    setSubmitting(false);
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-4">
      <div className="w-full max-w-sm rounded-xl border border-zinc-800 bg-zinc-900 p-6 shadow-xl">
        <h1 className="mb-6 text-center text-2xl font-bold text-white">
          COIN87 Login
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-zinc-400">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-800 p-2.5 text-white placeholder-zinc-500 focus:border-yellow-500 focus:outline-none"
              placeholder="you@example.com"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-yellow-500 px-5 py-2.5 text-center text-sm font-medium text-black hover:bg-yellow-400 focus:outline-none focus:ring-4 focus:ring-yellow-800 disabled:opacity-50"
          >
            {submitting ? "Processing..." : "Continue with Email"}
          </button>
        </form>
        <p className="mt-4 text-center text-xs text-zinc-500">
          No password required. We'll create an account if none exists.
        </p>
      </div>
    </div>
  );
}
