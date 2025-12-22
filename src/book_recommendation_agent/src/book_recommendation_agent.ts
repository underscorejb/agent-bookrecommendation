// src/book_recommendation_agent/src/book_recommendation_agent.ts
import 'dotenv/config';
import * as readline from "readline";
import { spawn } from "child_process";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai"; 

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function questionAsync(query: string): Promise<string> {
  return new Promise(resolve => rl.question(query, resolve));
}

export function loadBooks(genre: string): Promise<any> {
  // Update this path to your Python venv
  const pythonExecutable = "./venv/bin/python";
  const scriptPath = "src/data_ingestion_service/client/open_library_client.py";
  return new Promise((resolve, reject) => {
    const py = spawn(pythonExecutable, [scriptPath, genre], {
      env: { 
        ...process.env, 
        PYTHONPATH: process.cwd() 
      }
    });

    let data = "";
    let error = "";

    py.stdout.on("data", (chunk) => {
      data += chunk.toString();
    });

    py.stderr.on("data", (chunk) => {
      error += chunk.toString();
    });

    py.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python script exited with code ${code}: ${error}`));
      } else {
        try {
          const books = JSON.parse(data);
          resolve(books);
        } catch (err) {
          reject(err);
        }
      }
    });
  });
}


async function main() {
  console.log("\n📚 Book Recommendation Agent");

  while (true) {
    const userGenre = await questionAsync("\nYou: ");
    if (userGenre.toLowerCase() === "exit") {
      console.log("\nAgent: Goodbye!\n");
      break;
    }

    // Extract genre (simple example: "recommend books in fantasy")
    const words = userGenre.split(" ");
    const genre = words[words.length - 1].toLowerCase(); // grab last word

    try {
      console.log(`\n(Searching for ${genre} books...)\n`);
      
      // 1. Get the raw data from your Python script
      const data = await loadBooks(genre);
      const books = data.books;

      if (!books || books.length === 0) {
        console.log("Agent: I couldn't find any books for that genre.");
        continue;
      }

      // 2. Use Vercel AI SDK to generate a conversational recommendation
      const { text } = await generateText({
        model: openai("gpt-4o"), // Ensure you have OPENAI_API_KEY in your .env
        system: `You are a helpful librarian. You will be provided with a list of books in JSON format. 
                 Your job is to pick the most interesting book from the list and recommend it to the user.
                 Write a friendly, one-sentence summary explaining why it's a good choice.`,
        prompt: `The user is looking for ${genre} books. Here is the data: ${JSON.stringify(books)}. 
                 Please give a recommendation similar to: "Based on our collection, I recommend [Title] by [Author] ([Year]). It's [Description]."`
      });

      // 3. Print the AI response
      console.log(`Agent: ${text}`);

    } catch (err) {
      console.error("Agent Error:", err);
    }

  }
  // ONLY close once the loop is broken by the user typing 'exit'
  rl.close();

}

// Checker to see if live or testing
if (require.main === module) {
  main();
}