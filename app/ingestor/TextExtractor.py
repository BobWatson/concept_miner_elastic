from chardet import detect
import codecs

class TextExtractor:
    @classmethod
    def getContent(cls, file_name):
        
        encoding = ""
        
        with open(file_name, 'rb') as f:
            rawdata = f.read()
            encoding = detect(rawdata)['encoding']
            
        with codecs.open(file_name, 'rb', encoding=encoding, errors='ignore') as file_content:
            content = cls.readContent(file_content)
        
        return content
    
    @classmethod
    def readContent(cls,file_content):
        return file_content.read()