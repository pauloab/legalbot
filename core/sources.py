from dotenv import load_dotenv
load_dotenv()
import os

DATA_DIR=os.environ.get("DATA_DIR")

PDF_FILES = [
    DATA_DIR+"RPOS.pdf",
    DATA_DIR+"RGPA.pdf",
]


def get_legal_documents():
    return PDF_FILES


DEFAULT_CONTEXT = """Eres un bot de la Universidad Técnica de Machala que contesta dudas sobre normas legales internas de la universidad."""
