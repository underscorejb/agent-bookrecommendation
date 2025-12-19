# Book Recommendation Agent
*v1.0*

A simple AI book recommendation agent that ingests data from an external API and uses it to answer user questions. This agent consists of two parts a data-ingestion-service and a book-recommendation-agent.

* **Data-Ingestion-Service:** Fetch book data from the Open Library API and save to a JSON file

* **Book-Recommendation-Agent:** Read the JSON file and answer book recommendation questions using an LLM with tool/function calling

Note: Python for data ingestion, TypeScript for the AI agent.

## Installation & Prerequisites

``` bash
npm install
```

API Endpoint: GET https://openlibrary.org/subjects/{subject}.json?limit=25


## Agent Workflow Example 
### Example API Response
``` json
{
  "key": "/subjects/mystery",
  "name": "mystery",
  "works": [
    {
      "key": "/works/OL81592W",
      "title": "Murder on the Orient Express",
      "authors": [
        { "name": "Agatha Christie" }
      ],
      "first_publish_year": 1934
    }
  ]
}
```

### Output Format
Save a "books.json" file:
``` json
{
  "books": [
    {
      "title": "Murder on the Orient Express",
      "author": "Agatha Christie",
      "first_publish_year": 1934,
      "subject": "mystery"
    }
  ]
}
```

### Example Interaction
```console 
$ npm run start

📚 Book Recommendation Agent

You: Recommend a fantasy book

Agent: Looking for fantasy books...

Based on our collection, I recommend "The Name of the Wind" by Patrick Rothfuss (2007). It's a beautifully written fantasy epic about a legendary figure recounting his origin story.

You: exit
```

