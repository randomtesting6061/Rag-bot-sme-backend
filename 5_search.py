import chromadb
from openai import OpenAI
import os

# Initialize OpenAI client

def query_chroma_db(query, db_path="./chroma_db", top_k=5):
    """Query a ChromaDB collection directly."""
    print(f"Querying ChromaDB at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: ChromaDB directory {db_path} does not exist!")
        return None
    
    try:
        # Create persistent client
        chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Get the collection
        collection = chroma_client.get_collection("documents")
        print(f"Connected to collection with {collection.count()} documents")
        
        # Create query embedding
        response = client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Display results
        print(f"\nTop {top_k} results for query: '{query}'")
        for i, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        )):
            similarity = 1 - (distance / 2)  # Convert distance to similarity
            print(f"\n{i+1}. Document: {metadata.get('filename', 'Unknown')}")
            print(f"   Similarity: {similarity:.4f}")
            print(f"   Preview: {doc[:150]}..." if len(doc) > 150 else doc)
        
        return results
    
    except Exception as e:
        print(f"Error querying ChromaDB: {str(e)}")
        return None

def generate_response(query, results):
    """Generate a response using the query and results from ChromaDB."""
    if not results or not results["documents"][0]:
        return "No relevant information found."
    
    # Combine documents into context
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    context_parts = []
    for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
        source_info = f"Source: {metadata.get('filename', 'Unknown')}"
        context_parts.append(f"{source_info}\n{doc}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Generate response with OpenAI
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": f"Context information is below.\n\n{context}\n\nQuestion: {query}\n\nIf the context doesn't contain enough information to answer the question, say so."}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"Error: Could not generate response. {str(e)}"

def rag_query_chroma(query, db_path="./chroma_db", top_k=5):
    """Complete RAG query using ChromaDB."""
    # Query ChromaDB
    results = query_chroma_db(query, db_path, top_k)
    
    if not results:
        return "Error: Could not retrieve results from ChromaDB."
    
    # Generate response
    response = generate_response(query, results)
    
    print("\n----- Generated Response -----")
    print(response)
    
    return response

if __name__ == "__main__":
    # Example usage
    query = input("Enter your question: ")
    response = rag_query_chroma(query)