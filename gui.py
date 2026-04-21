from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
import os

import rag_engine
from config import PDF_FOLDER


class RAGApp:

    def __init__(self, root):

        self.root = root
        root.title("Hindi RAG Desktop")
        root.geometry("720x620")

        os.makedirs(PDF_FOLDER, exist_ok=True)

        # CHAT
        self.chat = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.chat.pack(fill="both", expand=True, padx=10, pady=10)

        # PDF SELECTOR
        self.pdf_var = tk.StringVar()
        self.dropdown = ttk.Combobox(root, textvariable=self.pdf_var)
        self.dropdown.pack(fill="x", padx=10, pady=5)

        self.refresh_pdfs()

        # ENTRY
        self.entry = tk.Entry(root)
        self.entry.pack(fill="x", padx=10, pady=5)
        self.entry.bind("<Return>", lambda e: self.ask())

        # BUTTONS
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Button(frame, text="Ask", command=self.ask).pack(side="left", padx=5)
        tk.Button(frame, text="Add PDF", command=self.browse_pdf).pack(side="left", padx=5)

        # DRAG DROP
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", self.drop)

        self.log("Drag & Drop PDF or click Add PDF")

    # ------------------
    def log(self, msg):
        self.chat.insert(tk.END, msg + "\n")
        self.chat.see(tk.END)

    # ------------------
    def refresh_pdfs(self):

        pdfs = rag_engine.get_all_pdfs()

        if not pdfs:
            self.dropdown["values"] = ["All PDFs"]
            self.pdf_var.set("All PDFs")
        else:
            self.dropdown["values"] = ["All PDFs"] + pdfs
            self.pdf_var.set("All PDFs")

    # ------------------
    def process_pdf(self, path):

        self.log(f"\nEmbedding:\n{path}")

        rag_engine.add_pdf(path)

        self.log("✅ PDF Added")

        self.refresh_pdfs()

    # ------------------
    def browse_pdf(self):

        file = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )

        if file:
            save_path = os.path.join(PDF_FOLDER, os.path.basename(file))
            os.system(f'cp "{file}" "{save_path}"')

            threading.Thread(
                target=self.process_pdf,
                args=(save_path,),
                daemon=True
            ).start()

    # ------------------
    def drop(self, event):

        file = event.data.strip("{}")

        if file.endswith(".pdf"):

            save_path = os.path.join(PDF_FOLDER, os.path.basename(file))
            os.system(f'cp "{file}" "{save_path}"')

            threading.Thread(
                target=self.process_pdf,
                args=(save_path,),
                daemon=True
            ).start()

    # ------------------
    def ask(self):

        query = self.entry.get().strip()
        if not query:
            return

        self.entry.delete(0, tk.END)

        selected = self.pdf_var.get()
        if selected == "All PDFs":
            selected = None

        self.log(f"\nYou: {query}")

        def run():
            ans = rag_engine.ask(query, selected)
            self.log(f"\nAI: {ans}\n")

        threading.Thread(target=run, daemon=True).start()