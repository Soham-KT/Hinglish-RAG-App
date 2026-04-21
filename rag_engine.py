import os
from dotenv import load_dotenv
import chromadb
from google import genai
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from config import *

# --------------------------------------------------------- Loading env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API")

client = genai.Client(api_key=GEMINI_API_KEY)

# --------------------------------------------------------- Embedding Model
embedder = SentenceTransformer(EMBED_MODEL)

# --------------------------------------------------------- Vector DB
db = chromadb.PersistentClient(path=DB_PATH)
collection = db.get_or_create_collection("hindi_rag")


# --------------------------------------------------------- Load PDF Text
def load_pdf(path):

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

    return text


# --------------------------------------------------------- Add PDF
def add_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    print("Embedding:", filename)

    text = load_pdf(pdf_path)

    chunks = [
        text[i:i+800]
        for i in range(0, len(text), 600)
    ]

    embeddings = embedder.encode(chunks).tolist()

    import uuid
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


# --------------------------------------------------------- List PDFs
def get_all_pdfs():

    data = collection.get(include=["metadatas"])

    files = set()

    for m in data["metadatas"]:
        if m:
            files.add(m["source"])

    return sorted(list(files))



# --------------------------------------------------------- Retreive
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

    docs = results["documents"][0]

    return "\n".join(docs)



# --------------------------------------------------------- Ask LLM
def ask(query, selected_pdf=None):

    context = retrieve(query, selected_pdf)

    prompt = f"""
You are a multilingual assistant.
Answer in same language.

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

    return response.text