import '../globals.css'
import { i18n } from '../i18n-config'
import { ReactNode } from 'react'

export async function generateStaticParams() {
  return i18n.locales.map((locale) => ({ lang: locale }))
}

type Props = {
  children: ReactNode
  // params: Promise<{ lang: Locale }>
}

export default async function LangLayout({ children }: Props) {
  return children;
} 