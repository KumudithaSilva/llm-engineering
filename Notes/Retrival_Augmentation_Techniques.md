#  ⚙️ Retrival Augmentation Techniques

1. Chunking
    - It's means dividing a large document into `smaller, manageable pieces` before storing them in a vector database or retrieval system.

    Common Chunking Strategies

    - Fixed-size chunking – split text by a `fixed number of tokens or characters`.
    - Semantic chunking – split based on `semantic meaning`.
    - Sliding window chunking – `overlapping chunks` to preserve context.
    - Recursive chunking – `progressively split text` using logical separators.
    - Adaptive Chunking - `adjusts the chunk size dynamically` based on the document structure and content complexity.
    - Embedding-Based Chunking - splits text using `semantic embeddings` to detect topic changes, so related content stays in the same chunk.
    - Hierarchical Chunking - documents are split into `multiple levels of chunks`.

2. Document Pre-processing
    - `Cleaning and preparing documents` before storing them in the retrieval system.

3. Query rewriting
    - `Modifying the user’s query` to make it clearer or more specific so the system can retrieve better results.

4. Query Expansion
    - `Adding related words or synonyms` to the user’s query to improve search results.

5. Re-ranking
    - `Reordering the retrieved results` so that the most relevant documents appear first.

6. Graph RAG
    - A retrieval-augmented system that uses a `graph database to store and retrieve information`.

7. Agentic-RAG
   - An autonomous agent that decide retrieval `sources, steps, query refinement, and perform actions`.
