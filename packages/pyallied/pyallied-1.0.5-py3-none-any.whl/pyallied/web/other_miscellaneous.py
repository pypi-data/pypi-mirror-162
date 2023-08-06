from mailbox import Mailbox
from re import A
import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as pl
from PIL import Image, ImageChops, ImageDraw
from pyallied.web.webWaits import customwebDriverwait
import textract
import os
import slate3k
import pandas as pd
import PyPDF2
from imap_tools import MailBox
from imap_tools import AND, OR
from datetime import date
from base64 import b64decode
import codecs


class miscellaneous(customwebDriverwait):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    '''
    returns the embedded text in the image.
    It returns a list of detected text, with each text element containing three types of information. 
    Which are: the text, its bounding box vertices, and the confidence level of the text detection
    '''

    def get_embeddedText_from_image(self, path: str):
        try:
            reader = easyocr.Reader(['en'])
            textList = []
            data = reader.readtext(path)
            for i in data:
                textList.append(i[1])
            #print(type(data),"---obj trype---")
            # return reader.readtext(path)
            return textList
        except Exception as error:
            raise error

    def is_images_same_compare_by_pixel(self, sourceFile, destinationFile):
        try:
            diff_img = ImageChops.difference(Image.open(
                sourceFile), Image.open(destinationFile)).convert('RGB')
            if diff_img.getbbox():
                return False
            else:
                return True
        except Exception as error:
            raise error

    def new_gray(self,size, color):
        img = Image.new('L', size)
        dr = ImageDraw.Draw(img)
        dr.rectangle((0, 0) + size, color)
        return img

    def marking_differences_With_Original_images(self, image_1, image_2, opacity=0.85):
        try:
            img1 = Image.open(
                image_1)
            img2 = Image.open(
                image_2)
            diff = ImageChops.difference(img1, img2)
            diff = diff.convert('L')
            # Hack: there is no threshold in PILL,
            # so we add the difference with itself to do
            # a poor man's thresholding of the mask:
            # (the values for equal pixels-  0 - don't add up)
            thresholded_diff = diff
            for repeat in range(3):
                thresholded_diff = ImageChops.add(
                    thresholded_diff, thresholded_diff)
            h, w = size = diff.size
            mask = self.new_gray(size, int(255 * (opacity)))
            shade = self.new_gray(size, 0)
            new = img1.copy()
            new.paste(shade, mask=mask)
            # To have the original image show partially
            # on the final result, simply put "diff" instead of thresholded_diff bellow
            new.paste(img2, mask=thresholded_diff)
            return new
        except Exception as error:
            raise error

    def pdf_content_reader(self, file1):
        try:
            file = open(file1, 'rb')

            pdfRead = PyPDF2.PdfFileReader(file)
            #print(pdfRead.getDocumentInfo().title,' ----title----')
            output = []
            readData = pdfRead.getPage(0)
            #print(readData.extractText(),' ----single----')
            for page in pdfRead.pages:
                output.append(page.extractText().replace("\n", " "))
            file.close()
            return output
        except Exception as error:
            raise error

    def mail_outlook_search(self, host, port: int, userName, password, searchString: str, searchDate: str = None):
        try:
            mailbox = MailBox(host, port)
            mailbox.login(userName, password)
            #responses =mailbox.idle.wait(timeout=60)
            mailData = {}
            path = ''
            fileName = ''
            #file2 = open(r"D:/Users/sjyothi/Repos/pythonseleniumFramework/testdata/MyFile2.txt", "w+")
            # data=''
            # if responses:
            # print(responses,'-----respon')
            # for msg in mailbox.fetch():
            if(searchDate != None):
                spliData = searchDate.split("/")
                year = int(spliData[0])
                month = int(spliData[1])
                day = int(spliData[2])
                for msg in mailbox.fetch(AND(date=date(year, month, day))):
                    if(msg.subject in searchString):
                        # print(msg.attachments,'--attach---')
                        if(msg.attachments):
                            # print(msg.date.strftime,"----------------yes--------")
                            cwd = os.getcwd()
                            if(not os.path.exists(cwd+"/tmp")):
                                path = os.mkdir(cwd+"/tmp")
                                # print(path,"---path---")
                            else:
                                path = cwd+"/tmp"
                            for att in msg.attachments:
                                # print(pd.DataFrame(data=att.payload),"-----------------------------------")

                                with open(path+'/{}'.format(att.filename), 'wb') as f:
                                    # print('----',att.filename)
                                    fileName = att.filename
                                    f.write(att.payload)

                                mailData[msg.date_str] = msg.text.replace("\r\n", " "), msg.subject, self.pdf_content_reader(
                                    path+"/"+fileName)
                        else:
                            #print(msg.date_str.replace(" ",""),"----------------yes--------")

                            mailData[msg.date_str] = msg.text.replace(
                                "\r\n", " "), msg.subject
                        # break
                # self.pdf_content_reader(path+"/"+fileName)
            else:
                searchDate = date.today()
                Year = date.today().year
                month = date.today().month
                day = date.today().day
                for msg in mailbox.fetch(AND(date=date(Year, month, day))):
                    if(msg.subject in searchString):
                        # print(msg.attachments,'--attach---')
                        if(msg.attachments):
                            # print(msg.date.strftime,"----------------yes--------")
                            cwd = os.getcwd()
                            if(not os.path.exists(cwd+"/tmp")):
                                path = os.mkdir(cwd+"/tmp")
                                # print(path,"---path---")
                            else:
                                path = cwd+"/tmp"
                            for att in msg.attachments:
                                # print(pd.DataFrame(data=att.payload),"-----------------------------------")

                                with open(path+'/{}'.format(att.filename), 'wb') as f:
                                    # print('----',att.filename)
                                    fileName = att.filename
                                    f.write(att.payload)

                                mailData[msg.date_str] = msg.text.replace("\r\n", " "), msg.subject, self.pdf_content_reader(
                                    path+"/"+fileName)
                        else:
                            # print(msg.date.time+"_"+msg.date.today,"----------------yes--------")

                            mailData[msg.date_str] = msg.text.replace(
                                "\r\n", " "), msg.subject
            mailbox.logout()
            return mailData

        except Exception as error:
            raise error

    def mail_outlook_Attachments(self, host, port: int, userName, password, searchString: str, fromAddress: str):
        try:
            mailbox = MailBox(host, port)
            mailbox.login(userName, password, 'INBOX')
            responses = mailbox.idle.wait(timeout=120)
            attachment = []
            if responses:
                for msg in mailbox.fetch(AND(text=searchString, new=True, from_=fromAddress)):
                    for attach in msg.attachments:
                        attachment.append(attach.filename)
            return attachment
        except Exception as error:
            raise error

    def mail_outlook_Attachments_Read(self, host, port: int, userName, password, searchString: str, fromAddress: str):
        try:
            mailbox = MailBox(host, port)
            mailbox.login(userName, password, 'INBOX')
            responses = mailbox.idle.wait(timeout=120)
            attachment_Read = {}
            if responses:
                for msg in mailbox.fetch(AND(text=searchString, new=True, from_=fromAddress)):
                    for attach in msg.attachments:
                        attachment_Read[attach.filename] = attach.payload
                        # attachment_Read.append(attach.payload)
            return attachment_Read
        except Exception as error:
            raise error
