import { NextResponse } from 'next/server';
// Import the service we refactored
import { getLibrarianRecommendation } from '@/../../src/book_recommendation_agent/src/librarian_service';

export async function POST(req: Request) {
  try {
    const { genre } = await req.json();
    
    // 1. Destructure the updated return from your service
    // This expects { text: string, coverUrl: string | null }
    const { text, coverUrl } = await getLibrarianRecommendation(genre);
    
    // 2. Return them both as a JSON object
    return NextResponse.json({ 
      text: text,
      coverUrl: coverUrl 
    });

  } catch (error: any) {
    console.error("API Route Error:", error);
    return NextResponse.json(
      { error: 'Failed to fetch recommendation', details: error.message }, 
      { status: 500 }
    );
  }
}
