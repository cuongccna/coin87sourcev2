"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Wallet, User } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { DarkModeToggle } from "./DarkModeToggle";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { PushNotification } from "./PushNotification";
import { TokenModal } from "./TokenModal";

export const Header = () => {
  const { user, loading } = useAuth();
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [modalContext, setModalContext] = useState<{newsId?: string, action?: string}>({});
  
  // Listen to openTokenModal events from NewsCard unlock buttons
  React.useEffect(() => {
    const handleOpenModal = (e: CustomEvent) => {
      console.log('Open token modal event:', e.detail)
      setModalContext(e.detail || {})
      setShowTokenModal(true)
    }
    window.addEventListener('openTokenModal' as any, handleOpenModal)
    return () => window.removeEventListener('openTokenModal' as any, handleOpenModal)
  }, [])
  
  return (
    <>
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-3 flex items-center justify-between transition-colors shadow-sm dark:shadow-none">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-yellow-400 rounded-lg flex items-center justify-center shadow-lg shadow-yellow-400/20">
            <span className="font-black text-slate-900 text-xs">C87</span>
          </div>
          <h1 className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">
            Coin<span className="text-yellow-400">87</span>
          </h1>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <LanguageSwitcher />
          <DarkModeToggle />
          
          {!loading && user ? (
            <>
              <Link
                href="/profile"
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                aria-label="Profile"
              >
                <User size={18} className="text-slate-600 dark:text-slate-400" />
              </Link>

              <button
                onClick={() => setShowTokenModal(true)}
                className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-full border border-slate-300 dark:border-slate-700 hover:border-yellow-400 dark:hover:border-primary transition-colors"
              >
                <Wallet className="w-4 h-4 text-yellow-400" />
                <span className="text-sm font-medium text-slate-900 dark:text-slate-200">
                  {user.balance.toFixed(2)}
                </span>
                <span className="text-xs text-slate-500 hidden sm:inline">$C87</span>
              </button>
              
              <PushNotification className="hidden sm:flex" />
            </>
          ) : (
            !loading && (
              <Link 
                href="/login"
                className="px-3 sm:px-4 py-1.5 text-sm font-medium bg-yellow-500 text-slate-900 rounded-full hover:bg-yellow-400 transition-colors"
              >
                Login
              </Link>
            )
          )}
        </div>
      </header>
      
      {user && (
        <TokenModal
          isOpen={showTokenModal}
          onClose={() => setShowTokenModal(false)}
          currentBalance={user.balance}
          newsId={modalContext.newsId}
          action={modalContext.action}
        />
      )}
    </>
  );
};
