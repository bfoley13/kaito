# Integrating KAITO RagEngine into the AI PR Reviewer for GitHub Repositories

## Overview

This document outlines the possibilities of leveraging the KAITO RAGEngine within the AI PR Reviewer.

## Requirements

The PR Reviewer has different requirements/needs for working with the KAITO RAGEngine.

1. A Useful RAG will have information stored based off the Abstract Syntax Tree (AST) of the project. The handling of repository analysis is outside the scope of the RAGEngine, so the PR Reviewer will only send information to KAITO it wants to embed.
2. The PR Reviewer will likely use a single index per repository, with relevant documents containing relevant chunks of code from the repository.
3. The PR Reviewer will need to be able to update docs as the repository is updated. This could be through something like GitHub actions on Pull Request merges into `main`. This mean document updates within kaito.


## Design 

To accomplish this, we want to use an azure service integrated into the KAITO RAGEngine as our Vector DB. We have 3 potential candidates, Azure AI Search, Cosmos DB, Postgres.

For all options, we will be able to leverage [LlamaIndex Vector Store Integration](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/vector_stores) to simplify the logic.

### Azure AI Search

### Cosmos DB