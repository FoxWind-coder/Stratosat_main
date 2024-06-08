import sys
import json
import hashlib

def split_text_into_chunks(text, chunk_size=10):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()[:3]

def main(file_path):
    file_name = file_path.split('/')[-1].split('.')[0]
    chunks_with_hashes = {}
    
    with open(file_path, 'r') as file:
        text = file.read()
        chunks = split_text_into_chunks(text)
        
        for i, chunk in enumerate(chunks):
            chunk_hash = generate_hash(chunk)
            chunks_with_hashes[chunk_hash] = chunk
            
    output = {file_name: chunks_with_hashes}
    
    with open(f"{file_name}.json", 'w') as json_file:
        json.dump(output, json_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    main(file_path)
