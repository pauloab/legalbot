from PyPDF2 import PdfReader
from etl.document import Document


def load_pdf(file):
    return PdfReader(file)


def get_text_by_page(pdf_reader: PdfReader):
    pages = []
    for i, page in enumerate(pdf_reader.pages):
        text_extracted = page.extract_text()

        if text_extracted:
            page_number = str(i)
            text_extracted = (
                "==INICIO PAGINA "
                + page_number
                + "==\n"
                + text_extracted
                + "\n==FIN PAGINA "
                + page_number
                + "==\n"
            )
            pages.append(text_extracted)
    return pages
