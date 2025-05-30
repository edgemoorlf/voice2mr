import { NextRequest, NextResponse } from 'next/server';

const JCDSS_API_URL = process.env.JCDSS_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
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

    console.log('🔍 [SERVER] Content format analysis:', {
      includes_medical_record: data.content?.includes('病历记录'),
      includes_double_star: /\*\*[^*]+\*\*/.test(data.content || ''),
      includes_single_star: /\*\s*\*[^*]+\*\*/.test(data.content || ''),
      line_count: data.content?.split('\n').length || 0
    });

    return NextResponse.json(data);
  } catch (error) {
    console.error('💥 [SERVER] Error in /api/query:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
