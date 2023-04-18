import os
import importlib
import argparse
from paddleocr import PaddleOCR
ppocr = importlib.import_module('.', 'ppocr')
from ppocr.utils.utility import get_image_file_list
from ppocr.utils.logging import get_logger
from myOCR import MyOCR

logger = get_logger()

def str2bool(v):
    return v.lower() in ("true", "t", "1")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", type=str, default='ch')
    parser.add_argument("--det", type=str2bool, default=True)
    parser.add_argument("--rec", type=str2bool, default=True)
    parser.add_argument("--use_angle_cls", type=str2bool, default=False)
    parser.add_argument("--in_datafile", type=str)
    parser.add_argument("--input_dir", type=str, default="input")
    parser.add_argument("--exportPDF", type=bool, default=False)
    parser.add_argument("--export_pdf_dir", type=str, default="output")
    parser.add_argument("--exportBinary", type=bool, default=False)
    parser.add_argument("--export_binary_filepath", type=str, default="out_data.pkl")
    parser.add_argument("--exportText", type=bool, default=False)
    parser.add_argument("--export_text_filepath", type=str, default="export_data.txt")

    args = parser.parse_args()
    
    ocr_data_file = args.in_datafile
    export_binary_filepath = args.export_binary_filepath
    exportPDF = args.exportPDF
    exportBinary = args.exportBinary
    exportText = args.exportText
    export_text_filepath = args.export_text_filepath

    if exportPDF and not os.path.exists(args.export_pdf_dir):
        os.mkdir(args.export_pdf_dir)

    export_pdf_dir = args.export_pdf_dir

    image_dir = args.input_dir
    image_file_list = get_image_file_list(args.input_dir)
    if len(image_file_list) == 0:
        logger.error('no images find in {}'.format(args.input_dir))

    ocr = MyOCR(args, logger)

    for img_path in image_file_list:
        img_name = os.path.basename(img_path)
        logger.info('{}{}{}'.format('*' * 10, img_path, '*' * 10))
        print('{}{}{}'.format('*' * 10, img_path, '*' * 10))

        ocr.run(img_path)

    # Generate PDF files
    if exportPDF:
        ocr.generatePDF(export_pdf_dir)
    
    if exportBinary:
        ocr.persistData(export_binary_filepath, combine_data=True, in_datafile=ocr_data_file)

    if exportText:
        ocr.exportData(export_text_filepath)