from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH =  "C:/Users/mathe/Desktop/teste_rag/chroma_db"

def load_documents(data_path):
    try:
        document_loader = PyPDFDirectoryLoader(data_path)
        return document_loader.load()
    except:
        print("Arquivo não encontrado")

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 80,
        length_function = len,
        is_separator_regex = False
    )
    return text_splitter.split_documents(documents)

def get_embedding_function():
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    return embeddings

def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory = CHROMA_PATH, embedding_function = get_embedding_function()
    )
    
    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include = [])
    existing_ids = set(existing_items["ids"])
    print(f"numero de documentos existented no DB: {len(existing_ids)}")

    new_chunks = []

    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"adicionando novos documentos: {len(new_chunks)}")
        new_chunks_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids = new_chunks_ids)
    else:
        print("nenhum documento adicionado")

    

def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source  = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks

def main():
    document = load_documents("C:/Users/mathe/Desktop/teste_rag/files")
    chunks = split_documents(document)
    add_to_chroma(chunks)
    

if __name__ == "__main__":
    main()