import io
import pypdf
import docx

async def parse_file_content(file_content: bytes, filename: str) -> str:
    """
    Parse content from PDF or DOCX file bytes.
    """
    text = ""
    filename = filename.lower()
    
    try:
        if filename.endswith('.pdf'):
            # Parse PDF
            pdf_file = io.BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        elif filename.endswith('.docx'):
            # Parse DOCX
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
        else:
            # Assume text file if not PDF/DOCX
            text = file_content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"Error parsing file {filename}: {e}")
        return ""

    return text
