import pandas as pd
from difflib import SequenceMatcher

def compute_similarity(a: str, b: str) -> float:
    """Compute correctness/similarity between agent answer and ground truth."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# Your evaluation samples for your RAG pipeline
data = {
    "question": [
        "What key features are present in the autonomous agent application?",
        "How is context retrieved from the database?"
    ],
    "answer": [
        "The application provides a Streamlit UI with custom styling, vector search powered by ChromaDB, and prompt evaluation features.",
        "Context is retrieved by embedding queries and finding similar document vectors stored in ChromaDB."
    ],
    "ground_truth": [
        "The application contains Streamlit UI, custom CSS, Groq LLM integration, and ChromaDB vector search.",
        "Ingested documents stored in chroma_store are queried using ChromaDB vector similarity."
    ]
}

df = pd.DataFrame(data)

# Calculate correctness metric
df["answer_correctness"] = [
    compute_similarity(ans, gt) for ans, gt in zip(df["answer"], df["ground_truth"])
]

# Save metrics securely without touching existing code
df.to_csv("ragas_evaluation_results.csv", index=False)
print("✅ RAG Correctness metrics calculated and saved to 'ragas_evaluation_results.csv' successfully!")