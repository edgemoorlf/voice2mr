import { NextRequest, NextResponse } from 'next/server';

const JCDSS_API_URL = process.env.JCDSS_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];

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

    return NextResponse.json(data);
  } catch (error) {
    console.error('💥 [A2MR-SERVER] Error in /api/a2mr:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
