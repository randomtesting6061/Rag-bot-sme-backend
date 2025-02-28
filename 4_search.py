import json
import os
import numpy as np
from openai import OpenAI

# Initialize OpenAI client

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search(query, top_k=5):
    """Search for relevant chunks using simple vector similarity."""
    print(f"Searching for: '{query}'")
    
    # Create query embedding
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding
    
    # Load chunks
    with open("chunks.json", 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} total chunks")
    
    # Load embeddings
    similarities = []
    
    for chunk in chunks:
        chunk_id = chunk["id"]
        embedding_path = f"embeddings/{chunk_id}.json"
        
        if os.path.exists(embedding_path):
            with open(embedding_path, 'r') as f:
                embedding_data = json.load(f)
            
            chunk_embedding = embedding_data["embedding"]
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            
            similarities.append({
                "chunk": chunk,
                "similarity": similarity
            })
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Print top chunks with content preview
    print(f"\nTop {top_k} most relevant chunks:")
    
    for i, result in enumerate(similarities[:top_k]):
        chunk = result["chunk"]
        similarity = result["similarity"]
        
        # Get a preview of the content (first 150 chars)
        content_preview = chunk["content"][:150] + "..." if len(chunk["content"]) > 150 else chunk["content"]
        
        print(f"\n{i+1}. Document: {chunk['document']} (Chunk {chunk['chunk_index']})")
        print(f"   Similarity: {similarity:.4f}")
        print(f"   Preview: {content_preview}")
    
    # Return top_k results
    top_results = similarities[:top_k]
    
    return top_results

def generate_response(query, relevant_chunks):
    """Generate a response using the query and relevant chunks."""
    # Combine the chunks into context
    context_parts = []
    
    for result in relevant_chunks:
        chunk = result["chunk"]
        similarity = result["similarity"]
        
        context_parts.append(f"Source: {chunk['document']} (Relevance: {similarity:.4f})\n{chunk['content']}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Generate response with OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
            {"role": "user", "content": f"Context information is below.\n\n{context}\n\nQuestion: {query}\n\nIf the context doesn't contain enough information to answer the question, say so. and try to explain the usage based on the user company descrption heprovide in query like compamy:"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return completion.choices[0].message.content

def rag_query(query, top_k=3):
    """Full RAG query process."""
    print(f"Query: {query}")
    
    # Search for relevant chunks
    relevant_chunks = search(query, top_k)
    
    if not relevant_chunks:
        return "No relevant information found."
    
    # Display results
    print(f"Found {len(relevant_chunks)} relevant chunks:")
    for i, result in enumerate(relevant_chunks):
        chunk = result["chunk"]
        similarity = result["similarity"]
        print(f"{i+1}. {chunk['document']} (Similarity: {similarity:.4f})")
    
    # Generate response
    response = generate_response(query, relevant_chunks)
    
    return response

if __name__ == "__main__":
    # Example usage
    query = input("Enter your question: ")

    response = rag_query(query)
    print("\nResponse:")
    print(response)