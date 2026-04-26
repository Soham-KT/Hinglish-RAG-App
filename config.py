import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

PDF_FOLDER = "./PDFs"
DB_PATH = "./chroma_db"

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

GEMINI_MODEL = "gemini-2.5-flash"