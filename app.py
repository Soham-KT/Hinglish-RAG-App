from tkinterdnd2 import TkinterDnD
from gui import RAGApp

def main():
    root = TkinterDnD.Tk()   
    app = RAGApp(root)
    root.mainloop()