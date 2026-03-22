# Create a new file: setup_rag.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

def build_knowledge_base():
    print("Loading RAG datasets...")
    desc_df = pd.read_csv("symptom_Description.csv")
    prec_df = pd.read_csv("symptom_precaution.csv")

    # Merge descriptions and precautions on the Disease column
    merged_df = pd.merge(desc_df, prec_df, on="Disease", how="inner")

    documents = []
    metadata = []

    print("Formatting documents...")
    for _, row in merged_df.iterrows():
        disease = row['Disease']
        desc = row['Description']
        # Combine precautions, ignoring NaN/nulls
        precautions = [str(row[f'Precaution_{i}']) for i in range(1, 5) if pd.notna(row.get(f'Precaution_{i}'))]
        prec_text = ", ".join(precautions)

        # Create the rich text chunk for the vector database
        doc_text = f"Disease: {disease}. Description: {desc}. Recommended precautions: {prec_text}."
        documents.append(doc_text)
        metadata.append({"disease": disease})

    print("Generating Embeddings with MiniLM...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(documents)

    print("Building FAISS Vector Index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Save to disk for offline use
    faiss.write_index(index, "medical_knowledge.index")
    with open("rag_metadata.json", "w") as f:
        json.dump(documents, f)
        
    print(f"Successfully embedded {len(documents)} diseases into the Vector DB!")

if __name__ == "__main__":
    build_knowledge_base()