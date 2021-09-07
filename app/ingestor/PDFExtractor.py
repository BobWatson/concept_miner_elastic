import pdftotext
from ingestor.TextExtractor import TextExtractor

class PDFExtractor(TextExtractor):
    
    @classmethod
    def readContent(cls,file_content):
        pdf = pdftotext.PDF(file_content)
        content = ''.join(pdf)
                
        return content