"""
ocr pipelines
"""
import os
import json
import zipfile
from zipfile import ZipFile
import boto3
import easyocr
import pytesseract
from pytesseract import Output
from PIL import Image
from PIL import ImageSequence
from pdf2image import convert_from_path
from .config import OUTPUT_PATH
from .config import EXTENSION_LIST
from config import S3_BUCKET_NAME

SESSION = boto3.Session()
S3 = SESSION.resource('s3')


def upload_file_to_s3(local_file_path):
    """
    Upload files to s3

    Args:
        local_file_path (str): file path

    """
    try:
        # saving file to s3
        for filename in os.listdir(local_file_path):
            s3_path = os.path.join(local_file_path, filename)
            S3.meta.client.upload_file(s3_path, S3_BUCKET_NAME, s3_path)
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


class EasyocrPipeline:
    """
    Easy ocr pipeline
    """

    def create_json(self, result, file):
        """
        json file save
        """
        try:
            dictionary = {}
            # create proper json to store in json file
            dictionary = [{'left': int(i[0][0][0]),
                           'top':int(i[0][1][1]),
                           'right':int(i[0][2][0]),
                           'bottom':int(i[0][3][1]),
                           'text':i[1],
                           'confidence':i[-1]} for i in result]
            # get json file path
            json_name = os.path.splitext(file)[0]
            # create json log file
            with open(json_name+".json", "w") as outfile:
                json.dump(dictionary, outfile)
        except Exception as error:
            return error

    def image_read(self, path, images):
        """
        Read the image and give text

        Args:
            path (string): _description_
            images (object): _description_
        """
        try:
            path = os.path.basename(path)
            # get file name
            file_name = os.path.splitext(path)[0]
            # get folder path
            folder_path = OUTPUT_PATH+file_name
            # get file extension
            file_extension = os.path.splitext(path)[-1].lower()
            # create folder if not exists
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # iterate image
            for index, img in enumerate(images):
                if file_extension == '.tif' or file_extension == '.pdf':
                    file_path = file_name+'('+str(index)+').jpg'
                else:
                    file_path = path
                file_path = os.path.join(folder_path, file_path)
                # save image
                img.save(file_path)
                reader = easyocr.Reader(['hi', 'en'])
                # read the image data
                result = reader.readtext(file_path, width_ths=0)
                # function to create json
                self.create_json(result, file_path)
            # upload file into s3
            upload_file_to_s3(folder_path)
        except Exception as error:
            return error

    def image_process(self, path):
        """
        Image process

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            img = Image.open(path)
            images = ImageSequence.Iterator(img)
            # read the image
            self.image_read(path, images)
        except Exception as error:
            return error

    def pdf_process(self, path):
        """
        PDF processing

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            # convert the pdf into images
            images = convert_from_path(path)
            # read the image
            self.image_read(path, images)
        except Exception as error:
            return error

    def zip_process(self, path):
        """
        zip processing method

        Args:
            path (string): file path
            reader (object): easy ocr object
        """
        try:
            # read the zip file
            with ZipFile(path, 'r') as zip_file:
                for file in zip_file.namelist():
                    zip_file.extract(file, OUTPUT_PATH)
                    extension = os.path.splitext(file)[-1].lower()
                    if extension in EXTENSION_LIST:
                        self.image_process(OUTPUT_PATH+file)
                    elif extension == '.pdf':
                        self.pdf_process(OUTPUT_PATH+file)
                    else:
                        return "Invalid Extension"
        except Exception as error:
            return error
