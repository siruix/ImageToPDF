from paddleocr import PaddleOCR
import os
import cv2
import pickle
import numpy as np
from operator import attrgetter
import bisect
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# define the schema of OCR result
# filename | canvas_size | [[pos, pos], [pos, pos], [pos, pos], [pos pos] | text, ...]

class Position:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class TextBox:
    # text | [Position, ..]
    def __init__(self, text, position_list) -> None:
        self.text = text
        self.location = position_list

class FileData:
    # filename | canvas_size | [TextBox, ...]
    def __init__(self, name, canvas_size, textbox_list) -> None:
        self.filename = name
        self.canvas_size = canvas_size
        self.textbox_list = textbox_list

class MyData:
    # [(filename | FileData), ...]
    def __init__(self, logger) -> None:
        self.data = []
        self.logger = logger

    def addRecord(self, filename, textboxs, canvas_size):
        textbox_list = []
        for idx in range(len(textboxs)):
            location = []
            textbox = textboxs[idx][0]
            text = textboxs[idx][1][0]
            for x,y in textbox:
                location.append(Position(x,y))
                
            textbox_list.append(TextBox(text, location)) 
        
        self.data.append(FileData(filename, canvas_size, textbox_list))

    def removeRecord(self, filename):
        pass

    def load(self, in_path):
        # check in_path
        with open(in_path,'rb') as infp:
            self.data = pickle.load(infp)

    def save(self, out_path):
        with open(out_path,'wb') as outfp:
            pickle.dump(self.data, outfp)

    def exportText(self, out_path):
        self.logger.info("Exporting as text file...")
        with open(out_path,'w') as outfp:
            for file in self.data:
                outfp.write(file.filename)
                outfp.write("\n")
                for textbox in file.textbox_list:
                    outfp.writelines(textbox.text)
                    outfp.write("\n")

    def exportPDF(self, out_dir):
        font_chinese = 'STSong-Light'
        pdfmetrics.registerFont(UnicodeCIDFont(font_chinese))
        for file in self.data:
            c = canvas.Canvas(out_dir + "/" + file.filename + ".pdf", file.canvas_size)
            c.setFont(font_chinese, 20) 
            
            for textbox in file.textbox_list:
                pos1, pos2, pos3, pos4 = textbox.location
                left = pos1[0]
                top = pos1[1]
                right = pos2[0]
                bottom = pos2[1]
                c.drawString(file.canvas_size[0], file.canvas_size[1] - top, textbox.text)
        
            c.showPage()
            c.save()

    def getFile(self, pos):
        return self.data[pos]

    def findByFilename(self, filename):
        i = bisect.bisect_left(self.data, filename, key=attrgetter('filename'))
        if self.data[i].filename == filename:
            return i
        else:
            return -1
        
    def searchString(self, word):
        # TODO not tested yet
        files = []
        for file in self.data:
            for textbox in file.textbox_list:
                for text in textbox:
                    i = text.find(word)
                    if i != -1:
                        files.append((file.filename, text))
                    
        return files


    def combine(self, data_to_combine):
        # deduplicate and sort and merge
        data_to_combine.data.sort(key = attrgetter('filename'))
        out_data = []
        i, j = 0, 0
        while i < len(self.data) and j < len(data_to_combine.data):
            if self.data[i].filename < data_to_combine.data[j].filename:
                out_data.append(self.data[i])
                i = i + 1
            elif self.data[i].filename > data_to_combine.data[j].filename:
                out_data.append(data_to_combine.data[j])
                j = j + 1
            else:
                # duplicate
                out_data.append(self.data[i])
                i = i + 1
                j = j + 1

        if i < len(self.data):
            out_data.extend(self.data[i:])
        elif j < len(data_to_combine.data):
            out_data.extend(data_to_combine.data[j:])
        else:
            pass
        
        self.data = out_data




class MyOCR:
    # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
    # You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
    # to switch the language model in order.
    # ocr = PaddleOCR(use_angle_cls=False, lang='ch') # need to run only once to download and load model into memory
    # img_path = 'input/20220914142421_329.jpg'
    # result = ocr.ocr(img_path, det=False, cls=False)
    # for idx in range(len(result)):
    #     res = result[idx]
    #     for line in res:
    #         print(line)
    def __init__(self, args, logger) -> None:
        self.engine = PaddleOCR(**(args.__dict__))
        self.det = args.det
        self.rec = args.rec
        self.cls = args.use_angle_cls
        self.data = MyData(logger)
        self.ocr_data = MyData(logger)
        self.logger = logger

    def setLanguage(self, lang):
        self.lang = lang

    def setImagePath(self, path):
        self.image_path = path

    def config(self, image_path, lang='ch'):
        self.setLanguage(lang)
        self.setImagePath(image_path)
        self.ocr = PaddleOCR(use_angle_cls=False, lang=self.lang)

    def run(self, img_path):
        self.ocr_result = self.engine.ocr(img_path,
                                    det=self.det,
                                    rec=self.rec,
                                    cls=self.cls)
        
        with open(img_path, 'rb') as f:
            img_str = f.read()
            np_arr = np.frombuffer(img_str, dtype=np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        canvas_size = (img.shape[1], img.shape[0])
        img_name = os.path.basename(img_path)
        if self.ocr_result is not None:
            self.ocr_data.addRecord(img_name, self.ocr_result[0], canvas_size)

    def readData(self, in_datafile=None):
        self.data.load(in_datafile)

    def persistData(self, out_datafile, combine_data=False, in_datafile=None):
        if combine_data:
            assert in_datafile is not None 
            assert os.path.exists(in_datafile)
            self.readData(in_datafile)
            self.data.combine(self.ocr_data)
            
        self.data.save(out_datafile)

    def exportData(self, out_datafile):
        self.ocr_data.exportText(out_datafile)

    def generatePDF(self, out_PDFfile):
        self.data.exportPDF(out_PDFfile)