import { getDictionary } from './dictionaries/get-dictionary'
import type { Locale } from '../i18n-config'
import type { Dictionary } from '@/types/dictionary'
import HomeClient from '../components/HomeClient'

export default async function LocalizedHomePage({ params: { lang } }: { params: { lang: Locale } }) {
  const dict = (await getDictionary(lang)) as Dictionary

  return <HomeClient dict={dict} />
}