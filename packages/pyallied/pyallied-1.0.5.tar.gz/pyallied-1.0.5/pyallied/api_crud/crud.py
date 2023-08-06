import ast
import requests
import xlrd
import pandas as pd
import json
import numpy as np
import base64
import tweepy

class crud:

    def __init__(self):
        pass
    #def twitterPost(self):


    def crudCall(self,testLocation,testcaseId):
        #"D:/Users/sjyothi/Repos/SeleniumActionBot/pyseleniumbot/api/apiList.xlsx","Test_1"
        print(testcaseId)
        dictdata=crud.__readData_toDict(self,testLocation,testcaseId)
        headersDict={}
        #print(dictdata)
        dataH=str(dictdata["headers"]).split(",")
        for data in dataH:
            headersDict[str(data.split(":")[0])]=str(data.split(":")[1])
            #print(str(data.split(":")[0]))

        #print(headersDict)
        #print(ast.literal_eval(str(dictdata["headers"]).replace("‘","'")))
        if dictdata["crud_type"]=="POST":
            if( "multipart" in dictdata["headers"]):
                files = {'file': open(dictdata["multipart_data"], 'rb')}
                f=open(dictdata["data"])
                

                
                data=json.dumps(json.load(f)[testcaseId])
                
                respo=requests.post(dictdata["api_signature"],headers=headersDict,data=data,files=files)
                #print(respo.json())
                return respo
                print('')
            else:
                f=open(dictdata["data"])
                
                data=json.dumps(json.load(f)[testcaseId])
                
                respo=requests.post(dictdata["api_signature"],headers=headersDict,data=data)
                #print(respo.json())
                return respo
        if dictdata["crud_type"]=="GET":
            #f=open(dictdata["data"])
            
            #data=json.dumps(json.load(f)[testcaseId])
            
            respo=requests.get(dictdata["api_signature"],headers=headersDict)
            
            #print(respo.json())
            return respo
        if dictdata["crud_type"]=="DELETE":
            #f=open(dictdata["data"])
            
            #data=json.dumps(json.load(f)[testcaseId])
            
            respo=requests.delete(dictdata["api_signature"])
            
            #print(respo.json())
            return respo
        if dictdata["crud_type"]=="PUT":
            f=open(dictdata["data"])
                
            data=json.dumps(json.load(f)[testcaseId])
                
            respo=requests.put(dictdata["api_signature"],headers=headersDict,data=data)
            return respo                        





    def __readData(self,dataLocation:str):
        # Give the location of the file
        loc = ("path of file")
        
        # To open Workbook
        wb = xlrd.open_workbook(dataLocation)
        sheet = wb.sheet_by_index(0)
    
        
        # For row 0 and column 0
        #print(sheet.row_values(1))
        return sheet.cell_value(0, 0)
    def __readData_toDict(self,dataLocation:str,testcaseid:str):
        '''
        xls = pd.read_excel(dataLocation)
        dataDict=xls.set_index("testcase_id").to_dict("index")
        dataJson= xls.set_index("testcase_id").to_json(orient="index")
        
        jsonFormat=json.loads(dataJson)

        return dataDict.get(testcaseid)
        '''
        xls = pd.ExcelFile(dataLocation)
        
        sheets = xls.sheet_names
        for sheet in sheets:
            xls = pd.read_excel(dataLocation,sheet_name=sheet)
            dataDict=xls.set_index("testcase_id").to_dict("index")
            if(dataDict.get(testcaseid)):
                print(dataDict.get(testcaseid))
                return dataDict.get(testcaseid)
                        
        xls.close()