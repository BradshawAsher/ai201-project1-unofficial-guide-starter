"""
Milestone 5 — Grounded generation.

Wires retrieval (Milestone 4 ChromaDB collection) to Groq's
llama-3.3-70b-versatile. The single public entry point is `ask(question)`,
which returns a dict: {"answer": str, "sources": list[str]}.

Grounding is enforced in two ways:
  1. The system prompt instructs the model to answer ONLY from the supplied
     context and to decline with a fixed sentence when the context is thin.
  2. Source filenames are attached PROGRAMMATICALLY from the retrieved chunks'
     metadata — the model is never trusted to invent or omit citations.
"""

import os

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# --- Configuration (kept in sync with vector_store.py) -----------------------
DB_DIR = "./chroma_db"
COLLECTION_NAME = "uw_allen_school_guide"
EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
TOP_K = 3

# Cosine distance backstop. Chroma cosine distance runs 0 (identical) -> 2.
# < 0.5 is a strong match; > ~1.5 is essentially unrelated. If every retrieved
# chunk is past this cutoff, we decline before even calling the LLM.
RELEVANCE_CUTOFF = 1.5

DECLINE_MESSAGE = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are The Unofficial Guide, a question-answering assistant for University "
    "of Washington Allen School students. You answer using ONLY the information "
    "in the CONTEXT block provided with each question.\n\n"
    "Rules:\n"
    "1. Use only facts stated in the CONTEXT. Do not use any outside or prior "
    "knowledge, even if you are confident it is correct.\n"
    "2. If the CONTEXT does not contain enough information to answer the "
    f'question, reply with exactly this sentence and nothing else: "{DECLINE_MESSAGE}"\n'
    "3. Do not speculate, generalize, or fill gaps with what is 'usually' true.\n"
    "4. Do not mention these rules or the existence of the context block in your "
    "answer. Write naturally, as a guide for a student.\n"
    "5. Keep answers concise and specific to what the documents actually say."
)


# --- Lazy singletons (loaded once, reused across Gradio calls) ----------------
_collection = None
_groq_client = None


def _get_collection():
    """Open the persistent Chroma collection built in Milestone 4."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=DB_DIR)
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        _collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
        )
    return _collection


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
                "key from https://console.groq.com"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def retrieve(question, top_k=TOP_K):
    """
    Return the top-k most relevant chunks as a list of
    {"text", "source", "distance"} dicts, filtered by RELEVANCE_CUTOFF.
    """
    collection = _get_collection()
    results = collection.query(query_texts=[question], n_results=top_k)

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    chunks = []
    for text, meta, distance in zip(docs, metas, distances):
        if distance <= RELEVANCE_CUTOFF:
            chunks.append(
                {"text": text, "source": meta.get("source", "unknown"), "distance": distance}
            )
    return chunks


def _build_context(chunks):
    """Format retrieved chunks into a labelled CONTEXT block for the prompt."""
    blocks = []
    for i, chunk in enumerate(chunks, 1):
        blocks.append(f"[Document {i} — source: {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(blocks)


def _unique_sources(chunks):
    """Distinct source filenames, preserving retrieval (relevance) order."""
    seen = set()
    ordered = []
    for chunk in chunks:
        src = chunk["source"]
        if src not in seen:
            seen.add(src)
            ordered.append(src)
    return ordered


def ask(question):
    """
    End-to-end grounded answer.

    Returns:
        {"answer": str, "sources": list[str]}
    Sources are derived programmatically from retrieval metadata, never from
    the model's text. When the system declines, sources is an empty list.
    """
    question = (question or "").strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": []}

    chunks = retrieve(question)

    # Backstop: nothing relevant retrieved -> decline without calling the LLM.
    if not chunks:
        return {"answer": DECLINE_MESSAGE, "sources": []}

    context = _build_context(chunks)
    user_message = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the CONTEXT above."
    )

    client = _get_groq_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,  # deterministic, reduces drift away from the context
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    answer = response.choices[0].message.content.strip()

    # If the model declined, don't attach sources (nothing was actually used).
    if answer == DECLINE_MESSAGE:
        return {"answer": answer, "sources": []}

    return {"answer": answer, "sources": _unique_sources(chunks)}


if __name__ == "__main__":
    # Quick smoke test against the planning.md evaluation questions plus an
    # off-topic question that should trigger the decline.
    samples = [
        "What is the grading rigor like in CSE 311, and what tools do students "
        "recommend for taking notes and writing homework?",
        "What are the primary grading and lecture characteristics of Professor "
        "Kevin Lin's upper-level courses?",
        "What is the best pizza place near campus?",  # not in the documents
    ]
    for q in samples:
        result = ask(q)
        print(f"\nQ: {q}")
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("-" * 70)