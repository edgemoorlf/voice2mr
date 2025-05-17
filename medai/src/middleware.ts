import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { i18n } from './app/i18n-config'

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if this is a direct locale route (e.g., /es, /fr)
  const isDirectLocaleRoute = i18n.locales.some(locale => pathname === `/${locale}`)
  if (isDirectLocaleRoute) {
    return // Allow direct locale routes to pass through
  }

  // Check if the pathname is missing a locale
  const pathnameIsMissingLocale = i18n.locales.every(
    (locale) => !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`
  )

  if (pathnameIsMissingLocale) {
    // Get the preferred locale from the request header
    const locale = request.headers.get('accept-language')?.split(',')[0].split('-')[0] || i18n.defaultLocale

    // Redirect to the locale-prefixed path
    return NextResponse.redirect(
      new URL(`/${locale}${pathname === '/' ? '' : pathname}`, request.url)
    )
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
} 