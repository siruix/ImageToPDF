import os
import fitz                           # import PyMuPDF

class Rect:
    # rectangle (left, top, right, bottom) in pixels
    def __init__(self, left, top, right, bottom) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


class MyPDFWriter:

    def __init__(self, output_dir) -> None:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.output_dir = output_dir

    def createDocument(self):
        pass

    def setRect(self, rect):
        self.rect = rect

    def writePage(self, text, fontsize = 12, fontname = "Times-Ronam", fontfile = None, align = 0, rect = None):
        if rect:
            self.setRect(rect)
        
        pass

    def saveDocument(self):
        pass

    def closeDocument(self):
        pass
