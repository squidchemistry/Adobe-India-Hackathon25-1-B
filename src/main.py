import json
import os
from pdfprocessor import extract_text_per_page
from chuncker import chunk_document
from semantic_matcher import SemanticMatcher

def process_collection(collection_path):
    """
    Processes a single document collection located at `collection_path`.
    It reads the config file, loads each PDF, extracts and chunks text, 
    and saves all chunked data into a JSON file.
    """
    input_json = os.path.join(collection_path, "challenge1b_input.json")
    pdfs_dir = os.path.join(collection_path, "PDFs")

    # Ensures input JSON exists
    if not os.path.exists(input_json):
        print(f"❌ Input JSON not found in {collection_path}")
        return
    
    try:
        with open(input_json, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode JSON in {input_json}: {e}")
        return
    
    pdfs = config["documents"]
    
    all_collection_chunks = []
    
    for doc in pdfs:
        filename = doc["filename"]
        title = doc["title"]

        if not filename:
            print("⚠️ Skipping a document entry due to missing filename.")
            continue
        
        full_path = os.path.join(pdfs_dir, filename)

        if not os.path.exists(full_path):
            print(f"❌ File not found: {full_path}")
            continue
        
        print(f"\n📄 Processing: {title} ({filename}) in {collection_path}")

        try:
            pages = extract_text_per_page(full_path)  # Extract text from PDF page by page
        except Exception as e:
            print(f"❌ Failed to extract text from {filename}: {e}")
            continue
        
        # This will take the list of pages and break them into 4-6 paragraph blocks
        document_chunks = chunk_document(pages, filename=filename, title=title)
        
        # metadata
        num_chunks = len(document_chunks)
        print(f"✅ Document {filename} processed. Generated {num_chunks} chunks.")
        
        all_collection_chunks.extend(document_chunks)
        
    # Outputting all chunks to a JSON file
    output_dir_for_chunks = os.path.join(collection_path, "processed_chunks")
    os.makedirs(output_dir_for_chunks, exist_ok=True)

    collection_dir_name = os.path.basename(os.path.normpath(collection_path)) 
    output_json = os.path.join(output_dir_for_chunks, f"{collection_dir_name}_all_chunks_for_b1.json")

    try:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(all_collection_chunks, f, indent=4)
        print(f"📝 All chunks for collection '{collection_dir_name}' saved to {output_json}")
    except Exception as e:
        print(f"❌ Failed to save chunks to {output_json}: {e}")


def main():
    collections_dir = "collections"
    
    # If 'collections' directory doesn't exist, create and inform user
    if not os.path.exists(collections_dir):
        print(f"Creating missing '{collections_dir}' directory for input collections.")
        os.makedirs(collections_dir)
        print("Please place your collection subdirectories (e.g., 'collections/my_travel_docs/') inside this folder.")
        print("Each collection subdirectory should contain 'challenge1b_input.json' and a 'PDFs' folder.")
        return 

    found_collections = False

    # Loop through each subfolder and process if it's a valid directory
    for collection_name in os.listdir(collections_dir):
        collection_path = os.path.join(collections_dir, collection_name)
        if os.path.isdir(collection_path):
            found_collections = True
            print(f"\n===== Analyzing {collection_name} =====")
            process_collection(collection_path)
    
    if not found_collections:
        print(f"\nNo collections found in '{collections_dir}'. Please set up your input structure as described.")


if __name__ == "__main__":
    main()
