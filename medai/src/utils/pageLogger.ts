import { headers } from 'next/headers';
import { logUsageToFile } from './logger';

export async function logPageAccess(pagePath: string, additionalInfo: any = {}) {
  try {
    const headersList = await headers();
    const userAgent = headersList.get('user-agent') || 'unknown';
    const referer = headersList.get('referer') || 'direct';
    const acceptLanguage = headersList.get('accept-language') || 'unknown';
    
    // Get client IP from various possible headers
    const clientIP = headersList.get('x-forwarded-for') ||
                     headersList.get('x-real-ip') ||
                     headersList.get('cf-connecting-ip') ||
                     'unknown';

    const logData = {
      timestamp: new Date().toISOString(),
      type: 'page_access',
      page: pagePath,
      clientIP: clientIP.split(',')[0].trim(),
      userAgent,
      referer,
      acceptLanguage,
      ...additionalInfo
    };

    logUsageToFile(logData);
    
    // Also log to console for immediate visibility
    console.log('📄 [PAGE-ACCESS]', {
      page: pagePath,
      clientIP: logData.clientIP,
      userAgent: userAgent.substring(0, 50) + '...',
      referer,
      ...additionalInfo
    });
  } catch (error) {
    console.error('Failed to log page access:', error);
  }
}