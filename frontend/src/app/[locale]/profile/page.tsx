'use client'

import { useAuth } from '@/context/AuthContext'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { User, Mail, Award, TrendingUp, LogOut, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [loggingOut, setLoggingOut] = useState(false)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  const handleLogout = async () => {
    setLoggingOut(true)
    try {
      await logout()
      toast.success('Logged out successfully')
      router.push('/')
    } catch (error) {
      toast.error('Failed to logout')
      setLoggingOut(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const memberSince = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors">
      {/* Header */}
      <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-4">
          <Link 
            href="/"
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <ArrowLeft size={20} className="text-slate-600 dark:text-slate-400" />
          </Link>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Profile</h1>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Profile Card */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center">
              <User size={32} className="text-slate-900" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">{user.email}</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">Member since {memberSince}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={16} className="text-yellow-500" />
                <span className="text-xs text-slate-500 dark:text-slate-400">Balance</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{user.balance.toFixed(2)}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">$C87</p>
            </div>

            <div className="bg-slate-50 dark:bg-slate-900/50 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center gap-2 mb-1">
                <Award size={16} className="text-yellow-500" />
                <span className="text-xs text-slate-500 dark:text-slate-400">Tier</span>
              </div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white capitalize">{user.tier}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Membership</p>
            </div>
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 mb-6">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Account Information</h3>
          
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Mail size={18} className="text-slate-400" />
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Email</p>
                <p className="text-sm text-slate-900 dark:text-white">{user.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <User size={18} className="text-slate-400" />
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">User ID</p>
                <p className="text-sm text-slate-900 dark:text-white">#{user.id}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <button
          onClick={handleLogout}
          disabled={loggingOut}
          className="w-full flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 text-white font-medium py-3 rounded-xl transition-colors disabled:opacity-50"
        >
          <LogOut size={18} />
          {loggingOut ? 'Logging out...' : 'Logout'}
        </button>
      </div>
    </div>
  )
}
