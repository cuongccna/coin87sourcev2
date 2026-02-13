'use client'

import { useEffect, useState } from 'react'
import { Bell, BellOff } from 'lucide-react'
import toast from 'react-hot-toast'

interface PushNotificationProps {
  className?: string
}

export function PushNotification({ className = '' }: PushNotificationProps) {
  const [permission, setPermission] = useState<NotificationPermission>('default')
  const [subscription, setSubscription] = useState<PushSubscription | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission)
    }
    checkSubscription()
  }, [])

  const checkSubscription = async () => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready
        const existingSub = await registration.pushManager.getSubscription()
        setSubscription(existingSub)
      } catch (error) {
        console.error('Failed to check subscription:', error)
      }
    }
  }

  const requestPermission = async () => {
    if (!('Notification' in window)) {
      toast.error('This browser does not support notifications')
      return
    }

    setLoading(true)
    try {
      const perm = await Notification.requestPermission()
      setPermission(perm)

      if (perm === 'granted') {
        await subscribeToPush()
      } else if (perm === 'denied') {
        toast.error('Notifications blocked. Enable in browser settings.')
      }
    } catch (error) {
      console.error('Failed to request permission:', error)
      toast.error('Failed to request notification permission')
    } finally {
      setLoading(false)
    }
  }

  const subscribeToPush = async () => {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      return
    }

    try {
      const registration = await navigator.serviceWorker.ready
      
      // Generate VAPID key pair: https://web.dev/push-notifications-subscribing-a-user/
      // For production, store this in .env
      const vapidPublicKey = process.env.NEXT_PUBLIC_VAPID_KEY || 'REPLACE_WITH_VAPID_KEY'

      // Defensive checks: avoid calling subscribe with an invalid placeholder key
      if (!vapidPublicKey || vapidPublicKey.includes('REPLACE') || vapidPublicKey.length < 10) {
        toast.error('Push subscription not configured. Set NEXT_PUBLIC_VAPID_KEY in .env.local')
        return
      }

      // Convert VAPID public key to Uint8Array, then use its underlying ArrayBuffer
      let applicationServerKeyUint8: Uint8Array
      try {
        applicationServerKeyUint8 = urlBase64ToUint8Array(vapidPublicKey)
      } catch (err) {
        console.error('Invalid VAPID public key', err)
        toast.error('Invalid VAPID public key. Please regenerate keys.')
        return
      }

      // Cast the Uint8Array to BufferSource to satisfy TypeScript typings for subscribe
      const applicationServerKey = applicationServerKeyUint8 as unknown as BufferSource

      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey,
      })

      // Send subscription to backend
      await fetch('/api/v1/notifications/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscription.toJSON ? subscription.toJSON() : subscription),
        credentials: 'include',
      })

      setSubscription(subscription)
      toast.success('Notifications enabled!')
    } catch (error) {
      console.error('Failed to subscribe:', error)
      toast.error('Failed to enable notifications')
    }
  }

  const unsubscribe = async () => {
    if (!subscription) return

    setLoading(true)
    try {
      await subscription.unsubscribe()
      
      // Notify backend
      await fetch('/api/v1/notifications/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
        credentials: 'include',
      })

      setSubscription(null)
      toast.success('Notifications disabled')
    } catch (error) {
      console.error('Failed to unsubscribe:', error)
      toast.error('Failed to disable notifications')
    } finally {
      setLoading(false)
    }
  }

  if (!('Notification' in window)) {
    return null
  }

  return (
    <button
      onClick={subscription ? unsubscribe : requestPermission}
      disabled={loading || permission === 'denied'}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        subscription
          ? 'bg-primary text-slate-900 hover:bg-amber-500'
          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
      } disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      title={
        permission === 'denied'
          ? 'Notifications blocked. Enable in browser settings.'
          : subscription
          ? 'Disable notifications'
          : 'Enable notifications'
      }
    >
      {loading ? (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : subscription ? (
        <Bell size={16} />
      ) : (
        <BellOff size={16} />
      )}
      <span className="text-sm font-medium hidden sm:inline">
        {subscription ? 'Notifications On' : 'Enable Notifications'}
      </span>
    </button>
  )
}

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}
