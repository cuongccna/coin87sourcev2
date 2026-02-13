'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from '@/i18n/navigation';
import { useTransition } from 'react';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const switchLocale = (newLocale: string) => {
    // Store preference in localStorage for persistence
    if (typeof window !== 'undefined') {
      localStorage.setItem('preferredLocale', newLocale);
    }

    startTransition(() => {
      // The i18n router handles locale switching automatically
      router.replace(pathname, { locale: newLocale as any });
    });
  };

  return (
    <div className="relative inline-flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
      <button
        onClick={() => switchLocale('vi')}
        disabled={isPending}
        className={`
          px-3 py-1.5 rounded-md text-sm font-medium transition-all
          ${locale === 'vi' 
            ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' 
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }
          ${isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        VI
      </button>
      <button
        onClick={() => switchLocale('en')}
        disabled={isPending}
        className={`
          px-3 py-1.5 rounded-md text-sm font-medium transition-all
          ${locale === 'en' 
            ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' 
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          }
          ${isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        EN
      </button>
      <Globe className="w-4 h-4 ml-1 text-slate-400" />
    </div>
  );
}
