import requests
from bs4 import BeautifulSoup
import os

import rag_engine
from config import PDF_FOLDER


URL = "https://socialjustice.mp.gov.in/Circular/ajaxPaginationData/0"


# --------------------------------------------------------- Get latest page HTML
def fetch_latest_page():

    session = requests.Session()

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://socialjustice.mp.gov.in",
        "Referer": "https://socialjustice.mp.gov.in/circular",
        "User-Agent": "Mozilla/5.0"
    }

    data = {
        "page": "0",
        "cat_id": "",
        "issed_by": "",
        "sTitle": "",
        "csrf_token_id": ""
    }

    r = session.post(URL, headers=headers, data=data)
    r.raise_for_status()

    return r.text


# --------------------------------------------------------- Extract PDF links
def extract_pdf_links(html):

    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".pdf"):
            links.append(href)

    return links


# --------------------------------------------------------- Download only NEW PDFs
def download_new_pdfs(pdf_links):

    os.makedirs(PDF_FOLDER, exist_ok=True)

    existing = set(os.listdir(PDF_FOLDER))

    new_files = []

    for link in pdf_links:

        filename = link.split("/")[-1]

        if filename in existing:
            print(f"Already exists: {filename}")
            continue

        print(f"Downloading NEW PDF: {filename}")

        r = requests.get(link)

        save_path = os.path.join(PDF_FOLDER, filename)

        with open(save_path, "wb") as f:
            f.write(r.content)

        new_files.append(save_path)

    return new_files


# --------------------------------------------------------- Full pipeline
def crawl_latest():

    html = fetch_latest_page()

    pdf_links = extract_pdf_links(html)

    # download only new PDFs
    new_files = download_new_pdfs(pdf_links)

    # embed only newly downloaded PDFs
    for pdf in new_files:
        rag_engine.add_pdf(pdf)

    return len(new_files)


def run_crawler():
    """
    Called by GUI on startup.
    Returns message for GUI.
    """

    print("Checking latest circular page...")

    downloaded = crawl_latest()   # your existing function

    if downloaded == 0:
        return "No new circulars found"

    return f"{downloaded} new circular(s) added"


# --------------------------------------------------------- MAIN (independent test)
def main():
    crawl_latest()


if __name__ == "__main__":
    main()