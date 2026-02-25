from pypdf import PdfReader
from fastapi import HTTPException


def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Encrypted PDFs are not supported"
            )

        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        return full_text

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract PDF text: {str(e)}"
        )