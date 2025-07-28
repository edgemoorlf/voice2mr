import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { i18n } from './app/i18n-config'

const PUBLIC_FILE = /\.(.*)$/;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Exclude static files and special Next.js files
  if (
    pathname.startsWith('/api') ||
    pathname.startsWith('/_next') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.startsWith('/manifest.json') ||
    pathname.startsWith('/robots.txt') ||
    pathname.startsWith('/sitemap.xml') ||
    PUBLIC_FILE.test(pathname)
  ) {
    return NextResponse.next();
  }

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
    
    // Log the redirect for tracking
    console.log('🔄 [REDIRECT]', {
      from: pathname,
      to: `/${locale}${pathname === '/' ? '' : pathname}`,
      userAgent: request.headers.get('user-agent')?.substring(0, 50) + '...',
      acceptLanguage: request.headers.get('accept-language'),
      clientIP: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown'
    });

    // Redirect to the locale-prefixed path
    let targetPath = `/${locale}`;
    if (pathname !== '/') {
      targetPath = `/${locale}${pathname}`;
    }
    return NextResponse.redirect(new URL(targetPath, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
      Match all except:
      - /_next (Next.js internals)
      - /static (static files)
      - /favicon.ico, /manifest.json, etc.
    */
    '/((?!_next|static|favicon.ico|manifest.json|icons|images|screenshots).*)',
  ],
} 