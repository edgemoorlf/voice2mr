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
    const body = await request.json();
    
    console.log('🔍 [DEBUG] Environment and URL info:', {
      JCDSS_API_URL,
      fullUrl: `${JCDSS_API_URL}/query`,
      nodeEnv: process.env.NODE_ENV
    });
    
    // Log usage info with query details
    logUsageInfo(request, '/api/query', {
      promptLength: body.prompt?.length || 0,
      promptPreview: body.prompt?.substring(0, 200) || '',
      role: body.role,
      sessionId: body.session_id,
      hasMedicalRecords: !!body.medical_records,
      medicalRecordsLength: body.medical_records?.length || 0,
      historyLength: body.history?.length || 0,
      language: body.language || 'unknown'
    });
    
    console.log('🔄 [SERVER] Received chat request:', {
      prompt: body.prompt?.substring(0, 100) + '...',
      role: body.role,
      session_id: body.session_id,
      has_medical_records: !!body.medical_records,
      history_length: body.history?.length || 0
    });

    const response = await fetch(`${JCDSS_API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('📡 [SERVER] Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ [SERVER] Backend error:', errorText);
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    
    console.log('✅ [SERVER] Backend success response:', {
      content_preview: data.content?.substring(0, 200) + '...',
      content_length: data.content?.length,
      timestamp: data.timestamp,
      session_id: data.session_id
    });
    
    // Log successful completion
    logUsageInfo(request, '/api/query-success', {
      responseLength: data.content?.length || 0,
      sessionId: data.session_id,
      processingTime: Date.now() - Date.parse(data.timestamp || new Date().toISOString())
    });

    console.log('🔍 [SERVER] Content format analysis:', {
      includes_medical_record: data.content?.includes('病历记录'),
      includes_double_star: /\*\*[^*]+\*\*/.test(data.content || ''),
      includes_single_star: /\*\s*\*[^*]+\*\*/.test(data.content || ''),
      line_count: data.content?.split('\n').length || 0
    });

    return NextResponse.json(data);
  } catch (error) {
    console.error('💥 [SERVER] Error in /api/query:', error);
    
    // Log error for usage tracking
    logErrorToFile({
      endpoint: '/api/query',
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
