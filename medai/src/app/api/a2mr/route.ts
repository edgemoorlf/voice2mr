import { NextRequest, NextResponse } from 'next/server';
import { logUsageToFile, logErrorToFile } from '../../../utils/logger';

const JCDSS_API_URL = process.env.JCDSS_API_URL || 'http://localhost:8000';

// Usage tracking helper
function logUsageInfo(request: NextRequest, endpoint: string, additionalInfo: any = {}) {
  const timestamp = new Date().toISOString();
  const clientIP = request.headers.get('x-forwarded-for') || 
                   request.headers.get('x-real-ip') || 
                   'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';
  const referer = request.headers.get('referer') || 'direct';
  
  const logData = {
    timestamp,
    endpoint,
    clientIP: clientIP.split(',')[0].trim(), // First IP in case of multiple
    userAgent,
    referer,
    ...additionalInfo
  };
  
  logUsageToFile(logData);
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    
    // Log usage info
    logUsageInfo(request, '/api/a2mr', {
      fileCount: files.length,
      totalSizeBytes: files.reduce((sum, f) => sum + f.size, 0),
      fileTypes: [...new Set(files.map(f => f.type))], // Unique file types
      fileNames: files.map(f => f.name)
    });

    console.log('🔄 [A2MR-SERVER] Received file upload request:', {
      fileCount: files.length,
      fileNames: files.map(f => f.name),
      fileSizes: files.map(f => f.size),
      fileTypes: files.map(f => f.type),
      backendUrl: JCDSS_API_URL
    });

    // Forward the form data to the backend
    const backendFormData = new FormData();
    files.forEach(file => {
      backendFormData.append('files', file);
    });

    console.log('📡 [A2MR-SERVER] Forwarding to backend:', `${JCDSS_API_URL}/a2mr`);

    const response = await fetch(`${JCDSS_API_URL}/a2mr`, {
      method: 'POST',
      body: backendFormData,
    });

    console.log('📡 [A2MR-SERVER] Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ [A2MR-SERVER] Backend error:', {
        status: response.status,
        statusText: response.statusText,
        errorText: errorText.substring(0, 500)
      });
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('✅ [A2MR-SERVER] Backend success response:', {
      contentPreview: data.content?.substring(0, 200) + '...',
      contentLength: data.content?.length,
      timestamp: data.timestamp,
      session_id: data.session_id
    });

    console.log('🔍 [A2MR-SERVER] Content format analysis:', {
      includesMedicalRecord: data.content?.includes('病历记录'),
      includesDoubleStar: /\*\*[^*]+\*\*/.test(data.content || ''),
      includesSingleStar: /\*\s*\*[^*]+\*\*/.test(data.content || ''),
      lineCount: data.content?.split('\n').length || 0,
      starPatterns: (data.content?.match(/\*+/g) || []).slice(0, 10)
    });

    console.log('📋 [A2MR-SERVER] Full content being returned:', data.content);
    
    // Log successful completion
    logUsageInfo(request, '/api/a2mr-success', {
      responseLength: data.content?.length || 0,
      processingTime: Date.now() - Date.parse(data.timestamp || new Date().toISOString()),
      sessionId: data.session_id
    });

    return NextResponse.json(data);
  } catch (error) {
    console.error('💥 [A2MR-SERVER] Error in /api/a2mr:', error);
    
    // Log error for usage tracking
    logErrorToFile({
      endpoint: '/api/a2mr',
      clientIP: (request.headers.get('x-forwarded-for') || 'unknown').split(',')[0].trim(),
      errorType: error instanceof Error ? error.constructor.name : 'Unknown',
      errorMessage: error instanceof Error ? error.message : 'Unknown error',
      userAgent: request.headers.get('user-agent') || 'unknown'
    });
    
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
