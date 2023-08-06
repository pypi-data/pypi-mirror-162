from distutils.log import error
from pyparsing import And
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyallied.web.webWaits import customwebDriverwait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seletools.actions import drag_and_drop




class DragAndDrop(customwebDriverwait):
    # drag and drop
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        '''
        drag_and_drop(source, target)¶
        Holds down the left mouse button on the source element,
        then moves to the target element and releases the mouse button.
        Args:	
        source: The element to mouse down.
        target: The element to mouse up
        '''
    def dragAndDrop(self, sourcexpath, destinationxpath):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            DestinationElementPresense=super().WaitFor_PresenseOf_Element_Located(destinationxpath)
            DestinationElementVisibility=super().WaitFor_VisibilityOf_Element_Located(destinationxpath)
            if(SourceelElementPresense and DestinationElementPresense ):
                if(SourceelElementVisibility and DestinationElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)
                    destination = self.driver.find_element(By.XPATH, destinationxpath)
                    action_chains = ActionChains(self.driver)
                    action_chains.drag_and_drop(sourceElement, destination).perform()
        except Exception as error:
            raise error            
        '''
        drag_and_drop_by_offset(source, xoffset, yoffset)¶
        Holds down the left mouse button on the source element,
        then moves to the target offset and releases the mouse button.
        Args:	
        source: The element to mouse down.
        xoffset: X offset to move to.
        yoffset: Y offset to move to.
        '''
    def dragAndDropByOffset(self, sourcexpath, xoffset, yoffset):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            if(SourceelElementPresense):
                if(SourceelElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)

                    action_chains = ActionChains(self.driver)
                    action_chains.drag_and_drop_by_offset(
                        sourceElement, xoffset, yoffset).pause(5).perform()
        except Exception as error:
            raise error
    def dragElement_ToOffSet_And_Drop(self, sourcexpath, xoffset, yoffset):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            if(SourceelElementPresense):
                if(SourceelElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)

                    action_chains = ActionChains(self.driver)

                    action_chains.move_to_element(sourceElement).pause(1).click_and_hold().pause(2).move_by_offset(xoffset, yoffset).pause(2).release().perform()
        except Exception as error:
            raise error
    def seletools_drag_and_drop_xpath(self, sourcexpath, destinationxpath):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            DestinationElementPresense=super().WaitFor_PresenseOf_Element_Located(destinationxpath)
            DestinationElementVisibility=super().WaitFor_VisibilityOf_Element_Located(destinationxpath)
            if(SourceelElementPresense and DestinationElementPresense ):
                if(SourceelElementVisibility and DestinationElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)
                    destination = self.driver.find_element(By.XPATH, destinationxpath)                    
                    drag_and_drop(self.driver, sourceElement, destination)           
        except Exception as error:
            raise error
    def seletools_drag_and_drop_css(self, source_css, destination_css):
        try:
            SourceelElementPresense=self.__waitFor_presenseOf_element_located(source_css)
            SourceelElementVisibility=self.__waitFor_visibilityOf_element_located(source_css)
            DestinationElementPresense=self.__waitFor_presenseOf_element_located(destination_css)
            DestinationElementVisibility=self.__waitFor_visibilityOf_element_located(destination_css)
            if(SourceelElementPresense and DestinationElementPresense ):
                if(SourceelElementVisibility and DestinationElementVisibility):
                    sourceElement = self.driver.find_element(By.CSS_SELECTOR, source_css)
                    destination = self.driver.find_element(By.CSS_SELECTOR, destination_css)                    
                    drag_and_drop(self.driver, sourceElement, destination)           
        except Exception as error:
            raise error            
    '''
    ATTENTION: you must use CSS selectors for draggable and droppable elements in order for this script to work. 
    It’s related to the way that browser search elements in DOM tree using embedded scripts
    '''        
    def dragAndDrop_cssSelectorOnly_jsExecuter(self,source_css, destination_css):
        try:
            f = open(r"..\..\seleniumpythonactionbot\pyallied\web\dragDrop.js",  "r")
            javascript = f.read()
            f.close()
            self.driver.execute_script(javascript, source_css, destination_css)
        except Exception as error:
            raise error    
    def __waitFor_presenseOf_element_located(self, cssLocator):
        try:
            return WebDriverWait(self.driver, self.customWait).until(EC.presence_of_element_located((By.CSS_SELECTOR, cssLocator)))
        except Exception as error:
            raise error
    def __waitFor_visibilityOf_element_located(self, cssLocator):
        try:
            #print(self.customWait,'------>wait')
            return WebDriverWait(self.driver, self.customWait).until(EC.visibility_of_element_located((By.CSS_SELECTOR, cssLocator)))
        except Exception as error:
            raise error
