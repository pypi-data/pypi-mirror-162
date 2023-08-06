from select import select
from xml.dom.minidom import Element
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyallied.web.webWaits import customwebDriverwait
# drop downs


class DropDownActions(customwebDriverwait):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def selectDropDownByValue(self, xpath, valueToSelect):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.select_by_value(valueToSelect)
        except Exception as error:
            raise error
    def selectDropDownByIndex(self, xpath, indexToSelect):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.select_by_index(indexToSelect)
        except Exception as error:
            raise error
    def selectDropDownByVisibleText(self, xpath, textToSelect):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.select_by_visible_text(textToSelect)
        except Exception as error:
            raise error
    def deselectAllOptionsInDropDown(self, xpath):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.deselect_all()
        except Exception as error:
            raise error
    def getDefaultSelectedDropDownOptions(self, xpath):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            selectedOptions=[]
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    all_selected_options = select.all_selected_options
                    for i in all_selected_options:
                        if(i.text):
                            selectedOptions.append(i.text)
                        elif(i.get_attribute('value')):
                            selectedOptions.append(i.get_attribute('value'))
                    return selectedOptions
        except Exception as error:
            raise error
    def getAllOptionInDropDown(self, xpath):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            allOptions=[]
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    options = select.options
                    for i in options:
                        if(i.text):
                            allOptions.append(i.text)
                        elif(i.get_attribute('value')):
                            allOptions.append(i.get_attribute('value'))

                    return allOptions
        except Exception as error:
            raise error
    def deselectByIndex(self, xpath, index):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.deselect_by_index(index)
        except Exception as error:
            raise error
    def deselectByValue(self, xpath, value):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.deselect_by_value(value)
        except Exception as error:
            raise error
    def deselectByVisibleText(self, xpath, text):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                #if(elementVisibility):        
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    select.deselect_by_visible_text(text)
        except Exception as error:
            raise error
    def getFirstSelecteOption(self, xpath):
        try:
            elementPresense=super().WaitFor_PresenseOf_Element_Located(xpath)
            #elementVisibility=super().WaitFor_VisibilityOf_Element_Located(xpath)
            firstSelectedOption=[]
            if(elementPresense):
                #if(elementVisibility):        
                    select = Select(self.driver.find_element(By.XPATH, xpath))
                    selectedOption=select.first_selected_option
                    #for i in selectedOption:
                    if(selectedOption.text):
                            firstSelectedOption.append(selectedOption.text)
                    elif(selectedOption.get_attribute('value')):
                            firstSelectedOption.append(selectedOption.get_attribute('value'))

                    return firstSelectedOption 
        except Exception as error:
            raise error                    
