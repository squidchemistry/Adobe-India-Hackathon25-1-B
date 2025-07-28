import fitz  # PyMuPDF: Used for reading and parsing PDF files

def extract_text_per_page(pdf_path):
    """
    Extracts text content from each page of the given PDF file.
    """
    try:
        pdf_document = fitz.open(pdf_path)  # Open the PDF using PyMuPDF
    except Exception as e:
        print(f"❌ Failed to open PDF '{pdf_path}': {e}")
        return []
    
    pages_text = []  # Will hold extracted text and metadata for each page
    for page_index, page in enumerate(pdf_document):
        
        # Extract text using PyMuPDF's text extraction method
        page_text = page.get_text()

        # Append page information as a dictionary
        pages_text.append({
            "page_number": page_index + 1,  # 1-based page numbering
            "text": page_text
        })

    return pages_text
