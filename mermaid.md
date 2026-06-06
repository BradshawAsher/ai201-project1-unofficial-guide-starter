```mermaid
graph TD
    subgraph Data Ingestion
        A[Raw .txt Files in docs/] -->|Python File I/O| B[Document Parser Script]
    end
    
    subgraph Chunking & Vectorization
        B -->|Fixed Character Splitting: 500 / Overlap: 100| C[Text Chunks]
        C -->|all-MiniLM-L6-v2 Model| D[Dense Vector Embeddings]
        D -->|Write Vector + Metadata| E[(Local ChromaDB Vector Store)]
    end
    
    subgraph Execution & Retrieval
        F[User Search Query] -->|all-MiniLM-L6-v2 Model| G[Query Embedding Vector]
        G -->|Vector Distance Query top-k: 3| E
        E -->|Return Relevant Chunks| H[Retrieved Text Chunks]
    end
    
    subgraph Text Generation
        H -->|Inject Chunks as System Context| I[System Prompt Assembly Template]
        F --> I
        I -->|Structured Context Payload| J[Local Gemini API Inference Engine]
        J -->|Grounded Student Guide Answer| K[Terminal Interface / User UI]
    end

    style E fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px