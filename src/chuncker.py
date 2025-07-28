def chunk_document(pages: list, filename: str, title: str) -> list:
    """
    Splits the document's page texts into paragraph-based chunks. Each chunk contains 4 to 6 paragraphs and 
    carries metadata like page number, chunk ID, filename, and title.
    """

    all_chunks = []  # Final list to hold all generated chunks
    chunk_id_counter = 0  # Used to assign unique chunk IDs per document

    for page in pages:
        page_number = page["page_number"]
        page_text = page["text"]

        # Split the page text into paraagraphs based on double newLines
        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
        
        current_paragraph_block = []
        
        for i, para in enumerate(paragraphs):
            current_paragraph_block.append(para)
            
            #Condition to form a chunk:
            #Chunk is created only when:
            #There are between 4 and 6 paragraphs in the block, OR
            #It's the last paragraph of the page, and there are some remaining paragraphs in the block.
          
            if (len(current_paragraph_block) >= 4 and len(current_paragraph_block) <= 6) or \
               (i == len(paragraphs) - 1 and current_paragraph_block):
                
                chunk_text = "\n\n".join(current_paragraph_block)
                chunk__id_counter += 1
                
                chunk = {
                    "document_filename": filename,
                    "document_title": title,
                    "page_number": page_number,
                    "chunk_text": chunk_text,
                    "chunk_id": f"{filename}_page{page_number}_chunk{chunk_id_counter}"
                }
                all_chunks.append(chunk)
                current_paragraph_block = []  # Reset for the next block

    return all_chunks
