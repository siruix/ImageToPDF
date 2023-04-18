from src.MyPDFWriter import MyPDFWriter
from src.MyPDFWriter import Rect

if __name__ == "__main__":
    filepath = "output/some.pdf"
    text = "This text is written by Python. "
    myPDFWriter = MyPDFWriter()
    myPDFWriter.open(filepath)
    myPDFWriter.setPage(0)
    myRect = Rect(10, 10, 10, 10)
    myPDFWriter.setRect(myRect)
    myPDFWriter.writePage(text)
    myPDFWriter.saveDocument()
