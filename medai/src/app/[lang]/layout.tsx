import '../globals.css'
import { i18n } from '../i18n-config'
import { ReactNode } from 'react'
import type { Locale } from '../i18n-config'

export async function generateStaticParams() {
  return i18n.locales.map((locale) => ({ lang: locale }))
}

type Props = {
  children: ReactNode
  params: { lang: Locale }
}

export default function LocalizedLayout({
  children,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  params: _params, // _params is kept for structural reasons and potential future use with generateStaticParams
}: Props) {
  // Here you could fetch the dictionary for `_params.lang` if needed by the layout itself
  // or to provide it via context to nested server components.
  return <>{children}</>;
} 