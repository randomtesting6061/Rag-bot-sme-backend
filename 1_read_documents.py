import os
import json
import re

def read_text_files(path):
    """Read text files from a directory and save their content."""
    print(f"Reading text files from directory: {path}")
    
    # Check if directory exists
    if not os.path.exists(path):
        print(f"ERROR: Directory '{path}' does not exist!")
        return []
    
    # Check if directory is accessible
    if not os.access(path, os.R_OK):
        print(f"ERROR: Directory '{path}' is not readable!")
        return []
    
    all_documents = []
    
    try:
        all_files = os.listdir(path)
        txt_files = [f for f in all_files if f.endswith('.txt')]
        print(f"Found {len(txt_files)} text files")
        
        if len(txt_files) == 0:
            print(f"WARNING: No .txt files found in {path}")
            print(f"Available files: {all_files}")
        
        for filename in txt_files:
            print(f"Processing file: {filename}")
            file_path = os.path.join(path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    print(f"  Read {len(content)} characters from {filename}")
                    
                    if content:
                        # Remove excessive newlines
                        cleaned_content = re.sub(r'\n{3,}', '\n\n', content)
                        print(f"  Cleaned content: removed {content.count('\\n') - cleaned_content.count('\\n')} newlines")
                        
                        all_documents.append({
                            "filename": filename,
                            "content": cleaned_content
                        })
                        print(f"  Added document: {filename}")
                    else:
                        print(f"  File {filename} is empty, skipping")
            except Exception as e:
                print(f"  ERROR reading file {filename}: {str(e)}")
    except Exception as e:
        print(f"ERROR accessing directory {path}: {str(e)}")
    
    # Save documents to disk
    output_file = "documents.json"
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, output_file)
    
    print(f"Attempting to save to: {output_path}")
    print(f"Current directory: {current_dir}")
    print(f"Can write to current directory: {os.access(current_dir, os.W_OK)}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_documents, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(all_documents)} documents to {output_file}")
    except Exception as e:
        print(f"ERROR saving to {output_file}: {str(e)}")
    
    return all_documents

if __name__ == "__main__":
    # Try to use an absolute path if the relative path doesn't work
    documents_directory = "./docs"  # Change to your directory
    print(f"Starting document processing from: {documents_directory}")
    
    # Get absolute path
    abs_path = os.path.abspath(documents_directory)
    print(f"Absolute path: {abs_path}")
    
    documents = read_text_files(documents_directory)
    
    if not documents:
        print("No documents were processed. Trying with absolute path...")
        documents = read_text_files(abs_path)
    
    print(f"Process complete. Documents processed: {len(documents)}")