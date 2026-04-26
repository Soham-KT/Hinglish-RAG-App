import os
import time
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import pytesseract
from pdf2image import convert_from_path

from config import PDF_FOLDER, DB_PATH, EMBED_MODEL

# ------------------------------------------------------ config
POPPLER_PATH = r"C:\poppler\Library\bin"

os.makedirs(PDF_FOLDER, exist_ok=True)

model = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("hindi_rag")


# ------------------------------------------------------ Text extraction with OCR fallback
def extract_text(pdf_path):

    text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    except Exception as e:
        print("PDF text extraction failed:", e)

    # ---------- If empty → OCR ----------
    if len(text.strip()) < 50:
        print("Using OCR:", os.path.basename(pdf_path))
        text = ocr_pdf(pdf_path)

    return text


# ------------------------------------------------------ OCR Function
def ocr_pdf(pdf_path):

    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    text = ""

    for img in images:
        page_text = pytesseract.image_to_string(
            img,
            lang="hin+eng"
        )
        text += page_text + "\n"

    return text


# ------------------------------------------------------ Chunking
def chunk_text(text, size=800, overlap=150):

    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap

    return chunks


# ------------------------------------------------------ Embed PDF
def embed_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    existing = collection.get()["ids"]

    if any(filename in i for i in existing):
        print(f"{filename} already indexed.")
        return

    print("Embedding:", filename)

    start = time.time()

    text = extract_text(pdf_path)

    if not text.strip():
        print("No text found.")
        return

    chunks = chunk_text(text)

    embeddings = model.encode(chunks).tolist()

    ids = [f"{filename}_{i}" for i in range(len(chunks))]

    metas = [{"source": filename} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metas
    )

    print("Embedded in", round(time.time() - start, 2), "sec")