"""
tessaract ocr pipeline
"""
import os
import json
import zipfile
import boto3
import pytesseract
from pytesseract import Output
from PIL import Image
from PIL import ImageSequence
from pdf2image import convert_from_path
from .config import OUTPUT_PATH
from .config import EXTENSION_LIST
from config import S3_BUCKET_NAME

S3 = boto3.client('s3')


def upload_file_to_s3(local_file_path):
    """
    Upload files to s3

    Args:
        local_file_path (str): file path

    """
    try:
        # saving file to s3
        for filename in os.listdir(local_file_path):
            S3.meta.client.upload_file(
                local_file_path+'/'+filename, S3_BUCKET_NAME, local_file_path+'/'+filename)
    except Exception as error:
        return error


class TessaractOcr:
    """
    tesseract ocr
    """

    def extract_text_from_image(self, image, file_name, index):
        """
        extracting text from images
        Args:
            image (object): image object
            file_name (str): name of file
            index (int): index no of pages
        """
        try:
            # removing extension from input file name for output file initial name
            file_name = os.path.basename(file_name)
            output_filename = os.path.splitext(file_name)[0]
            # processing image using Tessaract Ocr
            process_image = pytesseract.image_to_data(
                image, output_type=Output.DICT)
            temp_path = OUTPUT_PATH+output_filename
            if not os.path.exists(temp_path):
                os.makedirs(OUTPUT_PATH+output_filename)
            # writing output to json file
            with open(temp_path+'/' + output_filename+'('+str(index) + ')' + '.json', 'w') as f:
                json_list = []
                for left, top, width, height, text, conf in zip(process_image.get('left'),
                                                                process_image.get(
                                                                    'top'),
                                                                process_image.get(
                                                                    'width'),
                                                                process_image.get(
                                                                    'height'),
                                                                process_image.get(
                                                                    'text'),
                                                                process_image.get('conf')):
                    # removing empty values from output
                    if float(conf) > 0:
                        output_json = {'left': left, 'top': top, 'right': left+width,
                                       'bottom': top+height, 'text': text, 'confidence':
                                       round(float(conf), 2)}
                        json_list.append(output_json)
                f.write(json.dumps(json_list))
                path = temp_path+'/'+output_filename+'('+str(index)+').jpg'
                image.save(path)

            upload_file_to_s3(temp_path)
        except Exception as error:
            return error

    def image_processing(self, input_file):
        """
        image processing

        Args:
            input_file (str): input file name
        """
        try:
            file_name = Image.open(input_file)
            # processing image using Tessaract Ocr
            for index, page in enumerate(ImageSequence.Iterator(file_name)):
                self.extract_text_from_image(page, input_file, index)
        except Exception as error:
            return error

    def pdf_processing(self, input_file):
        """
        pdf processing

        Args:
            input_file (str): input file name
        """
        try:
            images = convert_from_path(input_file)
            for index, image in enumerate(images):
                self.extract_text_from_image(image, input_file, index)
        except Exception as error:
            return error

    def zip_processing(self, input_file):
        """
        zip processing

        Args:
            input_file (str): input file name
        """
        try:
            # reading zip file
            with zipfile.ZipFile(input_file, mode="r") as file_list:
                # getting list of file inside zip
                # iterating over each file of zip
                for file in file_list.namelist():
                    file_list.extract(file, OUTPUT_PATH)  # saving file
                    # getting extension of file
                    extension = os.path.splitext(file)[-1].lower()
                    # if extesnion is image then calling image processing
                    if extension in EXTENSION_LIST:
                        self.image_processing(OUTPUT_PATH+file)
                    # else calling pdf procssing
                    elif extension == '.pdf':
                        self.pdf_processing(OUTPUT_PATH+file)
                    else:
                        return "Invalid extension"
        except Exception as error:
            return error
