import os
import re
import requests
from pywinauto import Application
import pygetwindow as gw
from transformers import pipeline
from PyPDF2 import PdfReader

def download_pdf(url, save_dir="downloads"):
    """Download the PDF from a URL and save it locally."""
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)  # Create directory if it doesn't exist

        # Get the filename from the URL
        filename = url.split("/")[-1]
        file_path = os.path.join(save_dir, filename)

        print(f"Downloading PDF from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=1024):
                    pdf_file.write(chunk)
            print(f"PDF downloaded successfully: {file_path}")
            return file_path
        else:
            print(f"Failed to download PDF. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


def summarize_text(text, max_chunk=1000):
    """Summarize long text in chunks."""
    # Use the DistilBART model explicitly
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = [
        summarizer(chunk, max_length=100, min_length=25, do_sample=False)[0]['summary_text']
        for chunk in chunks
    ]
    return " ".join(summaries)


def extract_pdf_text(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text


def get_browser_url(browser_name):
    """Extract the URL or file path from the browser's address bar."""
    try:
        # Connect to the browser application
        app = Application(backend="uia").connect(title_re=browser_name)
        browser_window = app.top_window()

        # Find the address bar element
        address_bar = browser_window.child_window(title="Address and search bar", control_type="Edit")
        url = address_bar.get_value()

        # Validate URL (ensure it's a file path or valid PDF URL)
        if re.match(r"^(https?|file)://", url) or url.endswith(".pdf"):
            return url

    except Exception as e:
        print(f"Error retrieving URL: {e}")
        return None


def detect_active_browser():
    """Detect the active browser window and determine if a PDF is open."""
    windows = gw.getAllTitles()
    for win in windows:
        if "Chrome" in win or "Edge" in win:
            return win
    return None


def analyze_pdf():
    # 1. Detect the active browser window
    browser_window = detect_active_browser()

    if not browser_window:
        print("No browser window detected displaying a PDF.")
        return

    print(f"Detected browser window: {browser_window}")

    # 2. Extract the file path or URL from the address bar
    url_or_path = get_browser_url(browser_window)

    if not url_or_path:
        print("Could not extract URL or file path from the address bar.")
        return

    print(f"Detected URL or file path: {url_or_path}")

    # 3. Handle local PDF files or online PDFs
    if url_or_path.startswith("file://"):
        # Convert file URL to local file path
        pdf_path = url_or_path.replace("file://", "").replace("/", "\\")
    elif re.match(r"^[a-zA-Z]:[\\/]", url_or_path):  # Check for local file paths like C:/ or D:/
        pdf_path = url_or_path.replace("/", "\\")
    elif url_or_path.endswith(".pdf"):
        print("PDF is hosted online. Downloading now...")
        pdf_path = download_pdf(url_or_path)  # Download the online PDF
        if not pdf_path:
            print("Failed to download the PDF.")
            return
    else:
        print("The detected URL does not point to a PDF file.")
        return

    # 4. Extract text from the PDF
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    print(f"Processing PDF: {pdf_path}")
    text = extract_pdf_text(pdf_path)

    # 5. Summarize the text
    print("Summarizing the content...")
    summary = summarize_text(text)
    print("Summary:")
    print(summary)

