// src/book_recommendation_agent/src/book_recommendation_agent.ts
import * as readline from "readline";
import { spawn } from "child_process";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function questionAsync(query: string): Promise<string> {
  return new Promise(resolve => rl.question(query, resolve));
}

function loadBooks(genre: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const py = spawn("python3", ["src/data_ingestion_service/client/open_library_client.py", genre]); // adjust path

  });
}


async function main() {

  console.log("📚 Book Recommendation Agent");

  while (true) {
    //Prompt
    const userGenre = await questionAsync("You: ");
    if (userGenre.toLowerCase() === "exit") {
      console.log("Agent: Goodbye!");
      break;
    }

    // Genre Extraction
    const words = userGenre.split(" ");
    const genre = words[2].toLowerCase;

    // Pass genre to py script which return a json list of books
    // Use Vercel AI SDK with one tool
    // Stream the response
    
  }

  rl.close();
}

main();