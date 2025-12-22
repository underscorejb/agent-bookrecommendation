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
  // Update this path to your Python venv
  const pythonExecutable = "./venv/bin/python";
  return new Promise((resolve, reject) => {
    const py = spawn("python3", [
      "src/data_ingestion_service/client/open_library_client.py",
      genre,
    ]);

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
  console.log("📚 Book Recommendation Agent");

  while (true) {
    const userGenre = await questionAsync("You: ");
    if (userGenre.toLowerCase() === "exit") {
      console.log("Agent: Goodbye!");
      break;
    }

    // Extract genre (simple example: "recommend books in fantasy")
    const words = userGenre.split(" ");
    const genre = words[words.length - 1].toLowerCase(); // grab last word

    try {
      // Call Python script and get books
      const books = await loadBooks(genre);

      // Print a sample
      console.log("Agent: Here are some books I found:");
      books.books.slice(0, 5).forEach((b: any, i: number) => {
        console.log(`${i + 1}. ${b.title} by ${b.author} (${b.first_publish_year})`);
      });

      // Here you can feed `books` into your Vercel AI agent as a tool
      // Example: AI agent can take `books` as input for recommendations
    } catch (err) {
      console.error("Error fetching books:", err);
    }
  }

  rl.close();
}


main();