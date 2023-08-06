from select import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyallied.web.webWaits import customwebDriverwait

class frameAndWindow(customwebDriverwait):

    def __init__(self, driver):
        #self.driver = driver
        super().__init__(driver)
        self.driver=driver
    def Get_Window_handles(self):
        try:
            return self.driver.window_handles
        except Exception as error:
            raise error
    def Get_window_Position(self):
        try:
            return self.driver.get_window_position()
        except Exception as error:
            raise error
    def Get_window_size(self):
        try:
            return self.driver.get_window_size()
        except Exception as error:
            raise error
    def Minimize_window(self):
        try:
            self.driver.minimize_window()
        except Exception as error:
            raise error
    def Maximize_window(self):
        try:
            self.driver.maximize_window()
        except Exception as error:
            raise error            

    # switch to window
    # ex: <a href="somewhere.html" target="windowName">Click here to open a new window</a>

    def switchToWindowUsingName(self, windowName):
        try:
            self.driver.switch_to.window(windowName)
        except Exception as error:
            raise error
    def switchtoWindowUsingHandle(self, windowNumber):
        try:
            current_window = self.driver.current_window_handle
            ListOfHandles = self.driver.window_handles
            if(current_window != ListOfHandles[windowNumber]):
                self.driver.switch_to.window(ListOfHandles[windowNumber])
        except Exception as error:
            raise error                
    # frame switch, It’s possible to access subframes by separating the path with a dot,
    # and you can specify the frame by its index too. That is: driver.switch_to_frame("frameName.0.child")
    # would go to the frame named “child” of the first subframe of the frame called “frameName”. All frames are evaluated as if from *top*.

    def switchToFrame(self, xpath):
        try:
            return super().WaitFor_frame_to_be_available_and_switch_to_it(xpath)
        except Exception as error:
            raise error        
    # Once we are done with working on frames, we will have to come back to the parent
    # frame which can be done using:

    def switchToParentFrame(self):
        try:
            self.driver.switch_to.default_content()
        except Exception as error:
            raise error
    def switch_To_Frame_ByXpath(self,frameXpath):
        try:
            #self.driver.presence_of_element_located(frameXpath)
            if(self.driver.presence_of_element_located(frameXpath)) :
                element=self.driver.find_element(By.XPATH, frameXpath)
                self.driver.switch_to.frame(element)
        except Exception as error:
            raise error
    def switch_To_Frame_ByIndex(self,index:int):
        try:

            self.driver.switch_to.frame(index)
        except Exception as error:
            raise error
    def switch_To_Frame_ByName(self,name):
        try:
            self.driver.switch_to.frame(name)
        except Exception as error:
            raise error       
    def switch_To_Parent_Frame(self):
        try:

            self.driver.switch_to.parent_frame()
        except Exception as error:
            raise error                                                    
    # navigating
