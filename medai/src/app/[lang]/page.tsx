import { getDictionary } from './dictionaries/get-dictionary'
import type { Locale } from '../i18n-config'
import type { Dictionary } from '@/types/dictionary'
import HomeClient from '../components/HomeClient'
import { notFound } from 'next/navigation';
import { logPageAccess } from '@/utils/pageLogger';

const validLocales = ['en', 'zh', 'es', 'fr', 'th'];

// Force dynamic rendering for logging
export const dynamic = 'force-dynamic';

export default async function LocalizedHomePage({ params: { lang } }: { params: { lang: Locale } }) {
  if (!validLocales.includes(lang)) {
    notFound();
  }
  
  // Log page access
  await logPageAccess(`/${lang}`, {
    language: lang,
    isValidLocale: true
  });
  
  const dict = (await getDictionary(lang)) as Dictionary

  return <HomeClient dict={dict} lang={lang} />
}