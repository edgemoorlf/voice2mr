import { getDictionary } from './dictionaries/get-dictionary'
import type { Locale } from '../i18n-config'
import type { Dictionary } from '@/types/dictionary'
import HomeClient from '../components/HomeClient'
import { notFound } from 'next/navigation';

const validLocales = ['en', 'zh', 'es', 'fr', 'th'];

export default async function LocalizedHomePage({ params: { lang } }: { params: { lang: Locale } }) {
  if (!validLocales.includes(lang)) {
    notFound();
  }
  const dict = (await getDictionary(lang)) as Dictionary

  return <HomeClient dict={dict} lang={lang} />
}