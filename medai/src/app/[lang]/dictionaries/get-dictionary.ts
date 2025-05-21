import type { Locale } from '../../i18n-config'

// We enumerate all dictionaries here for better linting and typescript support
// We also get the default import for cleaner types
const dictionaries = {
  en: () => import('./en.json').then((module) => module.default),
  zh: () => import('./zh.json').then((module) => module.default),
  es: () => import('./es.json').then((module) => module.default),
  fr: () => import('./fr.json').then((module) => module.default),
  th: () => import('./th.json').then((module) => module.default),
}

export const getDictionary = async (locale: Locale) => {
  if (!(locale in dictionaries)) {
    throw new Error(`Invalid locale: ${locale}`);
  }
  return dictionaries[locale]();
} 