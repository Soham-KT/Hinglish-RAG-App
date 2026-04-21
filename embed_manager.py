import os
import time
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
from config import PDF_FOLDER, DB_PATH, EMBED_MODEL

os.makedirs(PDF_FOLDER, exist_ok=True)

model = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection("hindi_rag")


# ----------------------------
# PDF TEXT EXTRACTION
# ----------------------------
def extract_text(path):

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

    return text


# ----------------------------
# CHUNKING
# ----------------------------
def chunk_text(text, size=800, overlap=150):

    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap

    return chunks


# ----------------------------
# EMBED SINGLE PDF
# ----------------------------
def embed_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    existing = collection.get()["ids"]

    if any(filename in i for i in existing):
        print(f"{filename} already indexed.")
        return

    print("Embedding:", filename)

    start = time.time()

    text = extract_text(pdf_path)

    chunks = chunk_text(text)

    embeddings = model.encode(chunks).tolist()

    ids = [f"{filename}_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    print("Embedded in", round(time.time()-start,2), "sec")