import os
import uuid
from dotenv import load_dotenv

import chromadb
from google import genai
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

import pytesseract
from pdf2image import convert_from_path

from config import *

# ------------------------------------------------------ Settings
POPPLER_PATH = r"C:\poppler\Library\bin"

os.environ["ANONYMIZED_TELEMETRY"] = "False"

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API")
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------------------------------ Embedding Model
embedder = SentenceTransformer(EMBED_MODEL)

# ------------------------------------------------------ Vector DB
db = chromadb.PersistentClient(path=DB_PATH)
collection = db.get_or_create_collection("hindi_rag")


# ------------------------------------------------------ OCR Fallback
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


# ------------------------------------------------------ Load PDF text
def load_pdf(pdf_path):

    text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    except Exception as e:
        print("PDF extraction failed:", e)

    # ---- OCR fallback ----
    if len(text.strip()) < 50:
        print("Using OCR:", os.path.basename(pdf_path))
        text = ocr_pdf(pdf_path)

    return text


# ------------------------------------------------------ Add PDF to vector DB
def add_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    # ---- prevent duplicate embedding ----
    data = collection.get(include=["metadatas"])

    for m in data["metadatas"]:
        if m and m.get("source") == filename:
            print(f"{filename} already embedded.")
            return

    print("Embedding:", filename)

    text = load_pdf(pdf_path)

    if not text.strip():
        print("No text extracted.")
        return

    # chunking
    chunks = [
        text[i:i+800]
        for i in range(0, len(text), 600)
    ]

    embeddings = embedder.encode(chunks).tolist()

    ids = [f"{filename}_{uuid.uuid4()}" for _ in chunks]
    metas = [{"source": filename} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metas
    )

    print("Total vectors:", collection.count())
    print("Done embedding.")


# ------------------------------------------------------ List PDFs
def get_all_pdfs():

    data = collection.get(include=["metadatas"])

    files = set()

    for m in data["metadatas"]:
        if m:
            files.add(m["source"])

    return sorted(list(files))


# ------------------------------------------------------ Retreival
def retrieve(query, selected_pdf=None):

    q_emb = embedder.encode([query]).tolist()

    if selected_pdf:
        results = collection.query(
            query_embeddings=q_emb,
            n_results=5,
            where={"source": selected_pdf}
        )
    else:
        results = collection.query(
            query_embeddings=q_emb,
            n_results=5
        )

    docs = results.get("documents", [[]])[0]

    return "\n".join(docs)


# ------------------------------------------------------ Ask LLM
def ask(query, selected_pdf=None):

    context = retrieve(query, selected_pdf)

    if not context:
        return "No relevant information found."

    prompt = f"""
You are a multilingual government document assistant.

Rules:
- Answer ONLY from context
- Answer in user's language
- If answer not present, say: Information not found.

QUESTION:
{query}

CONTEXT:
{context}

ANSWER:
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text.strip()