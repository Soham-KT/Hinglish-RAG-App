# RAG Desktop App - Project Documentation

## Overview

A desktop application for Retrieval-Augmented Generation (RAG) that allows users to query PDF documents using natural language. The app features a GUI with drag-and-drop PDF support and multilingual capabilities (optimized for Hindi).

**Date Created:** April 2026
**Python Version:** 3.11

---

## Project Structure

```
RAG Desktop App/
├── app.py              # Application entry point
├── config.py           # Configuration constants
├── embed_manager.py    # PDF embedding module (legacy)
├── gui.py              # Tkinter GUI implementation
├── rag_engine.py       # Core RAG logic (embedding, retrieval, LLM)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (API keys)
├── PDFs/               # Storage for uploaded PDF files
├── chroma_db/          # ChromaDB vector database storage
├── .venv/              # Python virtual environment
└── __pycache__/        # Python bytecode cache
```

---

## Architecture

### Core Components

#### 1. **Entry Point** (`app.py`)
- Initializes the Tkinter application with drag-and-drop support
- Creates the main application window
- Starts the GUI event loop

#### 2. **Configuration** (`config.py`)
| Setting | Value | Description |
|---------|-------|-------------|
| `PDF_FOLDER` | `./PDFs` | Directory for storing uploaded PDFs |
| `DB_PATH` | `./chroma_db` | Path to ChromaDB persistent storage |
| `EMBED_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Embedding model for multilingual support |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Google Gemini model for text generation |

#### 3. **GUI Layer** (`gui.py`)
The `RAGApp` class provides:
- **Chat Interface:** Scrollable text area for conversation history
- **PDF Selector:** Dropdown to filter by specific PDF or search all documents
- **Query Input:** Text entry with Enter key binding
- **Drag & Drop:** Native file drag-and-drop for PDFs
- **Threading:** Background processing for PDF embedding to prevent UI freeze

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `refresh_pdfs()` | Updates dropdown with indexed PDFs |
| `process_pdf(path)` | Embeds a PDF in background thread |
| `browse_pdf()` | Opens file dialog for PDF selection |
| `drop(event)` | Handles drag-and-drop events |
| `ask()` | Sends query to RAG engine |
| `log(msg)` | Appends messages to chat display |

#### 4. **RAG Engine** (`rag_engine.py`)
Core retrieval-augmented generation logic:

**Data Flow:**
```
User Query → Embedding → Vector Search → Context Retrieval → LLM → Answer
```

**Key Functions:**

| Function | Description |
|----------|-------------|
| `load_pdf(path)` | Extracts text from PDF using PyPDF |
| `add_pdf(pdf_path)` | Chunks, embeds, and stores PDF in vector DB |
| `get_all_pdfs()` | Lists all indexed PDF sources |
| `retrieve(query, selected_pdf)` | Semantic search in vector DB |
| `ask(query, selected_pdf)` | Full RAG pipeline: retrieve + generate |

**Chunking Strategy:**
- Chunk size: 800 characters
- Step size: 600 characters (200 char overlap)

#### 5. **Embedding Manager** (`embed_manager.py`)
Legacy module for PDF embedding. Superseded by `rag_engine.py` but contains similar functionality.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `chromadb` | Vector database for semantic search |
| `sentence-transformers` | Multilingual text embeddings |
| `google-generativeai` | Gemini LLM integration |
| `pypdf` | PDF text extraction |
| `pytesseract` | OCR support (available but not currently used) |
| `pillow` | Image processing for OCR |
| `pyinstaller` | Desktop app bundling |
| `tkinterdnd2` | Drag-and-drop Tkinter extension |
| `python-dotenv` | Environment variable management |

---

## How It Works

### 1. PDF Ingestion
1. User adds PDF via drag-drop or file browser
2. PDF is copied to `./PDFs/` directory
3. Text is extracted using PyPDF
4. Text is chunked with overlap
5. Chunks are embedded using SentenceTransformers
6. Embeddings stored in ChromaDB with metadata

### 2. Query Processing
1. User enters question in GUI
2. Query is embedded using same model
3. Top 5 similar chunks retrieved from ChromaDB
4. Context + query sent to Gemini API
5. Response displayed in chat window

### 3. Multilingual Support
- Embedding model supports multiple languages including Hindi
- LLM prompted to respond in same language as query
- Enables Hindi-English code-mixed queries

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API=<your_google_api_key>
```

**Getting a Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Add to `.env` file

---

## Usage

### Running the Application

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Adding Documents
1. **Drag & Drop:** Drag PDF files onto the application window
2. **File Browser:** Click "Add PDF" button and select a file

### Querying
1. Select a specific PDF from dropdown, or keep "All PDFs" selected
2. Type your question and press Enter or click "Ask"
3. View response in the chat window

---

## API Reference

### `rag_engine.add_pdf(pdf_path)`
Add a PDF to the vector database.

**Parameters:**
- `pdf_path` (str): Path to PDF file

### `rag_engine.ask(query, selected_pdf=None)`
Query the RAG system.

**Parameters:**
- `query` (str): User's question
- `selected_pdf` (str, optional): Filter by specific PDF filename

**Returns:**
- `str`: Generated answer from LLM

### `rag_engine.get_all_pdfs()`
Get list of indexed PDFs.

**Returns:**
- `list[str]`: Sorted list of PDF filenames

---

## Known Limitations

1. **Duplicate Detection:** Basic filename-based check may miss duplicates
2. **No PDF Deletion:** Cannot remove indexed documents via GUI
3. **Single Collection:** All documents stored in one ChromaDB collection
4. **Hardcoded Paths:** Relative paths may cause issues in different environments


---

## Security Notes

- **API Key:** The `.env` file contains a Gemini API key. Do not commit to version control.
- **File Operations:** `os.system()` calls in `gui.py` use string interpolation which could be hardened
- **Path Handling:** Consider using `pathlib` for safer path manipulation
