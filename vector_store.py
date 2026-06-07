import os
import chromadb
from chromadb.utils import embedding_functions
from ingest import chunk_text

def build_vector_store():
    docs_dir = "./documents"
    db_dir = "./chroma_db"
    
    if not os.path.exists(docs_dir):
        print(f"Error: Couldn't locate directory '{docs_dir}'.")
        return

    print("=== Launching Milestone 4: Vector Database Indexing ===")

    # 1. Initialize Persistent Local Chroma Client
    chroma_client = chromadb.PersistentClient(path=db_dir)

    # 2. Set up the specific Embedding Function matching your plan
    # This automatically downloads and leverages the all-MiniLM-L6-v2 model weights
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 3. Create or fetch your vector collection
    collection = chroma_client.get_or_create_collection(
        name="uw_allen_school_guide",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity for text matchmaking
    )

    # Containers for batch database insertion
    documents = []
    embeddings = [] # Chroma handles this under the hood via embedding_func
    metadatas = []
    ids = []
    
    global_chunk_counter = 0

    # 4. Ingest and Chunk Docs
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_dir, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
                
            file_chunks = chunk_text(raw_content, source_name=filename)
            
            for chunk in file_chunks:
                documents.append(chunk["text"])
                metadatas.append({"source": chunk["source"]})
                ids.append(f"id_chunk_{global_chunk_counter}")
                global_chunk_counter += 1
    
    # 5. Populate Vector Store (Keep this code exactly as it is)
    print(f"Vectorizing and loading {len(documents)} chunks into local ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("✅ Success: Vector Database built and saved to disk.")

    # ====================================================================
    # 📍 RUNNING REGISTRATION VERIFICATION TEST WITH DISTANCE METRICS
    # ====================================================================
    print("\n" + "="*60)
    print("📍 MILESTONE 4 CHECKPOINT: RETRIEVAL DISTANCE SCORES")
    print("="*60)
    
    # 3 Queries chosen directly from your planning.md Evaluation Plan
    test_queries = [
        "What is the grading rigor like in CSE 311, and what tools do students recommend for taking notes and writing homework?",
        "How does the project workload of CSE 333 compare to CSE 351, and what is the typical format of its assignments?",
        "What specific strategy is recommended for an internal UW student looking to secure an undergraduate research position with a computer science professor?"
    ]
    
    for i, query_string in enumerate(test_queries, 1):
        print(f"\n🚀 TEST QUERY #{i}: \"{query_string}\"")
        
        results = collection.query(
            query_texts=[query_string],
            n_results=4  # Returning top-4 as suggested by the rubric
        )
        
        # Unpack Chroma's arrays safely
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results['distances'][0]  # <-- This pulls the raw math scores!
        
        for rank in range(len(docs)):
            # Distances below 0.5 indicate very strong semantic context
            status = "✅ STRONG MATCH" if distances[rank] < 0.5 else "⚠️ WEAK MATCH"
            
            print(f"   [Match {rank+1}] Distance: {distances[rank]:.4f} ({status})")
            print(f"   Source Document: {metas[rank]['source']}")
            print(f"   Content: \"{docs[rank][:160]}...\"\n")
        print("-" * 60)

if __name__ == "__main__":
    build_vector_store()