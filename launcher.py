from app import main

if __name__ == "__main__":
    main()

# to build exe: 
# pyinstaller --clean --noconfirm --onefile --windowed --collect-all tkinterdnd2 --collect-all chromadb --collect-all torch --collect-all transformers --collect-all sentence_transformers --add-data ".env;." --add-data "PDFs;PDFs" --add-data "chroma_db;chroma_db" launcher.py