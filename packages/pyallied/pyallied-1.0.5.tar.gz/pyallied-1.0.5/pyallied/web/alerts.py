from select import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome import service
from pyallied.web.webWaits import customwebDriverwait
class driverAlerts(customwebDriverwait):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver



    #alerts
    # Use this class to interact with alert prompts. 
    # It contains methods for dismissing, accepting, inputting, and getting text from alert prompts.   
    def acceptAlert(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                Alert(self.driver).accept()
        except Exception as error:
            raise error                
    def dismissAlert(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                Alert(self.driver).dismiss() 
        except Exception as error:
            raise error                
    def getAlertText(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                alertText=Alert(self.driver).text
                return alertText
        except Exception as error:
            raise error                
    def sendKeystoAlert(self,keysToSend):
        try:
            alertPresence= super().WaitForAlert_is_present()
            alert=self.driver.switch_to.alert
            alert.send_keys(keysToSend)
            #name_prompt = Alert(self.driver)
            #name_prompt.send_keys(keysToSend)
        except Exception as error:
            raise error            
    # Special Keys
    #The Keys implementation.
    ''' yet to complete'''
    #Touch Actions
    ''' yet to complete'''






