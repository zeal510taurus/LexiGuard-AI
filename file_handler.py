import fitz  # PyMuPDF

def read_pdf(file):
    """Extracts text and maintains a list of content per page."""
    try:
        file_bytes = file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        full_text = ""
        pages_content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            full_text += page_text + "\n"
            pages_content.append(page_text)
            
        return {
            "content": full_text.strip(),
            "pages_content": pages_content,
            "pages": len(doc),
            "info": doc.metadata
        }
    except Exception as e:
        return {"error": str(e)}

def read_txt(file):
    content = file.read().decode("utf-8")
    return {"content": content, "pages_content": [content], "pages": 1}

def get_chunks_with_metadata(doc_data, chunk_size=1200, overlap=200):
    """Slices text into chunks while attaching the correct Page Number."""
    chunks = []
    metadatas = []
    
    for pg_idx, pg_text in enumerate(doc_data["pages_content"]):
        # Split page into chunks
        for i in range(0, len(pg_text), chunk_size - overlap):
            chunk = pg_text[i : i + chunk_size]
            if len(chunk) > 50: # Ignore tiny fragments
                chunks.append(chunk)
                metadatas.append({"page": pg_idx + 1}) # Page 1, 2, 3...
                
    return chunks, metadatas