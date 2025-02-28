import json
import tiktoken

# Initialize tokenizer for counting tokens
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    """Count the number of tokens in a text string."""
    return len(encoding.encode(text))

def chunk_text(text, max_tokens=4000):
    """Split text into chunks that fit within token limit."""
    tokens = encoding.encode(text)
    chunks = []
    
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

def chunk_documents():
    # Load documents
    try:
        with open("documents.json", 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        print(f"Loaded {len(documents)} documents")
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        return
    
    # Process each document into chunks
    all_chunks = []
    chunk_id = 0
    
    for doc in documents:
        filename = doc["filename"]
        content = doc["content"]
        token_count = count_tokens(content)
        
        print(f"Processing {filename}, {token_count} tokens")
        
        if token_count > 4000:
            print(f"  Splitting into chunks (token count: {token_count})")
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "document": filename,
                    "chunk_index": i,
                    "content": chunk
                })
                chunk_id += 1
            
            print(f"  Created {len(chunks)} chunks")
        else:
            all_chunks.append({
                "id": f"chunk_{chunk_id}",
                "document": filename,
                "chunk_index": 0,
                "content": content
            })
            chunk_id += 1
            print(f"  Document fits in one chunk")
    
    # Save chunks to disk
    output_file = "chunks.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(all_chunks)} chunks to {output_file}")
    return all_chunks

if __name__ == "__main__":
    chunks = chunk_documents()