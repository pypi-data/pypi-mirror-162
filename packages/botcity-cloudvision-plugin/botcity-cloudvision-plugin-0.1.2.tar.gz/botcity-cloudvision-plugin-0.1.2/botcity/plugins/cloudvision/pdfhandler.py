from typing import List

import pdf2image


def pdf_to_image(filepath: str, resolution: int = 72) -> List:
    """Converts a PDF to a list PIL Image objects

    Args:
        filepath (str): The PDF file path.
        resolution (int, optional): The resolution to use when converting the PDF to image.
            Defaults to 72.

    Returns:
        List: List of Image objects being one for each page of the PDF.
    """
    return pdf2image.convert_from_path(filepath, dpi=resolution)
