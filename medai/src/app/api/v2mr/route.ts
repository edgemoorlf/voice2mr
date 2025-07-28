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
    
    // Extract form data for logging
    const files = formData.getAll('files') as File[];
    const medicalRecords = formData.get('medical_records') as string;
    const language = formData.get('language') as string;
    const isJson = formData.get('is_json') as string;
    
    // Log usage info
    logUsageInfo(request, '/api/v2mr', {
      fileCount: files.length,
      totalSizeBytes: files.reduce((sum, f) => sum + f.size, 0),
      fileTypes: [...new Set(files.map(f => f.type))], // Unique file types
      fileNames: files.map(f => f.name),
      hasMedicalRecords: !!medicalRecords,
      medicalRecordsLength: medicalRecords?.length || 0,
      language: language || 'unknown',
      isJson: isJson === 'true'
    });
    
    const response = await fetch(`${JCDSS_API_URL}/v2mr`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to process voice input.' }));
      throw new Error(errorData.detail || 'Failed to process voice input');
    }

    const data = await response.json();
    
    // Log successful completion
    logUsageInfo(request, '/api/v2mr-success', {
      responseLength: data.content?.length || 0,
      sessionId: data.session_id,
      processingTime: Date.now() - Date.parse(data.timestamp || new Date().toISOString())
    });
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in v2mr API route:', error);
    
    // Log error for usage tracking
    logErrorToFile({
      endpoint: '/api/v2mr',
      clientIP: (request.headers.get('x-forwarded-for') || 'unknown').split(',')[0].trim(),
      errorType: error instanceof Error ? error.constructor.name : 'Unknown',
      errorMessage: error instanceof Error ? error.message : 'Unknown error',
      userAgent: request.headers.get('user-agent') || 'unknown'
    });
    
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
