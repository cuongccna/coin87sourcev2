import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  // All supported locales
  locales: ['en', 'vi'],
  
  // Default locale
  defaultLocale: 'vi',
  
  // Always show locale prefix
  localePrefix: 'always'
});
