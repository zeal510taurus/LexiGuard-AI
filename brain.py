import chromadb
from chromadb.utils import embedding_functions

# Use the default lightweight embedding model
embed_fn = embedding_functions.DefaultEmbeddingFunction()
client = chromadb.PersistentClient(path="./lexi_brain_db")

def save_to_brain(chunks, metadatas, doc_name):
    """Stores chunks and their corresponding page numbers."""
    # Ensure a clean collection for each new document or append to master
    collection = client.get_or_create_collection(
        name="document_intelligence", 
        embedding_function=embed_fn
    )
    
    ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def query_brain(question, n_results=4):
    """Finds the 4 most relevant snippets and their page sources."""
    collection = client.get_collection(
        name="document_intelligence", 
        embedding_function=embed_fn
    )
    
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    context_blocks = []
    source_pages = []
    
    for i in range(len(results['documents'][0])):
        text = results['documents'][0][i]
        page = results['metadatas'][0][i]['page']
        
        context_blocks.append(f"[SOURCE: PAGE {page}]\n{text}")
        source_pages.append(page)
        
    # Remove duplicates and sort pages
    unique_pages = sorted(list(set(source_pages)))
    
    return "\n\n---\n\n".join(context_blocks), unique_pages