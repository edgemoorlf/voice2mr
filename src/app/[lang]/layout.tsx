import '../globals.css'
import { i18n } from '../i18n-config'

export async function generateStaticParams() {
  return i18n.locales.map((locale) => ({ lang: locale }))
}

type Props = {
  children: React.ReactNode
  params: { lang: string }
}

export default async function LangLayout({ children, params }: Props) {
  return children
} 