// src/book_recommendation_agent/src/librarian_service.ts
import { spawn } from "child_process";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";
import path from 'path';

/**
 * Core Logic: Fetches data from Python and gets AI recommendation
 */
// src/book_recommendation_agent/src/librarian_service.ts
export async function getLibrarianRecommendation(genre: string) {
  const data = await loadBooksFromPython(genre);
  const books = data.books;

  if (!books || books.length === 0) return { text: "No books found.", coverUrl: null };

  // Pick the first book to recommend
  const recommendedBook = books[0]; 
  
  // Generate the Cover URL using Open Library's free service
  // format: https://covers.openlibrary.org/b/id/{ID}-L.jpg
  const coverUrl = recommendedBook.cover_i 
    ? `https://covers.openlibrary.org/b/id/${recommendedBook.cover_i}-L.jpg` 
    : null;

  const { text } = await generateText({
    model: openai("gpt-4o"),
    system: `You are a helpful librarian. Summarize this book: ${recommendedBook.title}.`,
    prompt: `User wants ${genre}. Data: ${JSON.stringify(recommendedBook)}`
  });

  // Return BOTH the text and the image URL
  return { text, coverUrl, title: recommendedBook.title };
}

/**
 * Internal helper to talk to the Python service
 */
function loadBooksFromPython(genre: string): Promise<any> {
  const projectRoot = path.resolve(process.cwd(), '..'); 
  const pythonExecutable = path.join(projectRoot, "venv", "bin", "python");
  const scriptPath = path.join(projectRoot, "src", "data_ingestion_service", "client", "open_library_client.py");

  return new Promise((resolve, reject) => {
    const py = spawn(pythonExecutable, [scriptPath, genre], {
      env: { 
        ...process.env, 
        PYTHONPATH: projectRoot // Ensure Python can find your 'src' module
      }
    });

    let data = "";
    let error = "";
    py.stdout.on("data", (chunk) => data += chunk.toString());
    py.stderr.on("data", (chunk) => error += chunk.toString());
    py.on("close", (code) => {
      if (code !== 0) reject(new Error(error));
      else resolve(JSON.parse(data));
    });
  });
}