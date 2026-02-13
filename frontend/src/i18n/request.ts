import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  // requestLocale is a Promise in Next.js 16
  let locale = await requestLocale;
  
  // Validate locale - fallback to default if invalid
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }
  
  console.log('[i18n] Requested locale:', locale);
  
  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default
  };
});
