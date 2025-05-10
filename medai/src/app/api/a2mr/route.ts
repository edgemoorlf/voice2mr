import { NextResponse } from 'next/server';

const JCDSS_API_URL = process.env.JCDSS_API_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    
    const response = await fetch(`${JCDSS_API_URL}/a2mr`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to process voice input.' }));
      throw new Error(errorData.detail || 'Failed to process voice input');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in a2mr API route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}
