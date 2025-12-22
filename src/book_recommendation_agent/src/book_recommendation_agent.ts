// src/book_recommendation_agent/src/book_recommendation_agent.ts
import 'dotenv/config';
import * as readline from "readline";
import { getLibrarianRecommendation } from "./librarian_service";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = (q: string): Promise<string> => new Promise(res => rl.question(q, res));

async function main() {
  console.log("📚 Web-Ready Librarian Agent Active");
  while (true) {
    const input = await question("\nYou: ");
    if (input.toLowerCase() === "exit") break;

    const genre = input.split(" ").pop() || "mystery";
    
    try {
      // Just call the service!
      const response = await getLibrarianRecommendation(genre);
      console.log(`Agent: ${response}`);
    } catch (err) {
      console.error("Agent Error:", err);
    }
  }
  rl.close();
}

if (require.main === module) main();