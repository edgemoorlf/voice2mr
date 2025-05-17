export const i18n = {
  defaultLocale: 'en',
  locales: ['en', 'zh', 'es', 'fr', 'th'],
  languageNames: {
    en: 'English',
    zh: '中文',
    es: 'Español',
    fr: 'Français',
    th: 'ไทย',
  },
} as const

export type Locale = typeof i18n.locales[number] 