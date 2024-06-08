import sys
import json

def reconstruct_text_from_chunks(chunks_with_hashes):
    reconstructed_text = ''
    for chunk_hash, chunk_text in chunks_with_hashes.items():
        reconstructed_text += chunk_text
    return reconstructed_text

def main(json_path, output_path):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        file_name = list(data.keys())[0]
        chunks_with_hashes = data[file_name]
        
        reconstructed_text = reconstruct_text_from_chunks(chunks_with_hashes)
        
        with open(output_path, 'wb') as output_file:  # Используем режим бинарной записи
            output_file.write(reconstructed_text.encode('utf-8'))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <json_path> <output_path>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(json_path, output_path)
