import json
import time
import os
from openai import OpenAI

# Initialize OpenAI client
# Replace with your actual API key

def generate_embeddings_in_batches():
    # Load chunks
    try:
        with open("chunks.json", 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"Loaded {len(chunks)} chunks")
    except Exception as e:
        print(f"Error loading chunks: {str(e)}")
        return
    
    # Create embeddings directory
    os.makedirs("embeddings", exist_ok=True)
    
    # Process in very small batches to avoid memory issues
    batch_size = 5  # Small batch size to prevent crashes
    
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        batch = chunks[i:batch_end]
        
        print(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} (chunks {i} to {batch_end-1})")
        
        # Extract content for embedding
        batch_texts = [chunk["content"] for chunk in batch]
        batch_ids = [chunk["id"] for chunk in batch]
        
        # Retry logic for API calls
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    input=batch_texts,
                    model="text-embedding-3-small"
                )
                
                batch_embeddings = [embedding.embedding for embedding in response.data]
                
                # Save each embedding individually to avoid memory issues
                for j, (chunk_id, embedding) in enumerate(zip(batch_ids, batch_embeddings)):
                    # Save to individual files
                    with open(f"embeddings/{chunk_id}.json", 'w') as f:
                        json.dump({
                            "id": chunk_id,
                            "embedding": embedding
                        }, f)
                
                success = True
                break  # Break retry loop on success
                
            except Exception as e:
                print(f"Error on attempt {attempt+1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        
        if not success:
            print(f"Failed to process batch after {max_retries} attempts")
        
        # Small delay between batches
        time.sleep(1)
    
    print(f"Generated and saved embeddings for {len(chunks)} chunks")

if __name__ == "__main__":
    generate_embeddings_in_batches()