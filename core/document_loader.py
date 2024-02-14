from PyPDF2 import PdfReader
from document import RAWDocument


def load_pdf(file):
    return PdfReader(file)


def read_docs_batch(files: list):
    return [load_pdf(file) for file in files]


def get_text_by_page(pdf_reader: PdfReader):
    pages = []
    for i, page in enumerate(pdf_reader.pages):
        text_extracted = page.extract_text()

        if text_extracted:
            page_number = str(i)
            text_extracted = (
                "==INICIO PAGINA "
                + page_number
                + "=="
                + text_extracted
                + "==FIN PAGINA "
                + page_number
                + "=="
            )
            pages.append(text_extracted)
    return pages


def get_RAW_documents(files: list):
    raw_docs = []
    for pdf in read_docs_batch(files):
        pages = get_text_by_page(pdf)
        raw_docs.append(RAWDocument(pages))
    return raw_docs
