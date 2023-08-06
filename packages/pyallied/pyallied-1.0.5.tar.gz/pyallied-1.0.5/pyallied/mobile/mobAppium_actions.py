import base64
from distutils.log import error
from typing import Dict,Optional,List,Any
from base64 import b64encode
from xmlrpc.client import boolean
from selenium.webdriver.common.utils import is_url_connectable
from selenium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.protocols.webdriver.can_execute_scripts import CanExecuteScripts
import polling2
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver import ActionChains
from pyallied.mobile.logTypes import logTypes
from pyallied.mobile.AndroidPoweOptions import android_poweroptions
from pyallied.mobile.key_event_keyCodes import key_codes
from appium.webdriver.extensions import keyboard
from pyallied.mobile.gsm import GsmCallActions
from pyallied.mobile.gsm import GsmSignalStrength
from pyallied.mobile.gsm import GsmVoiceState
from pyallied.mobile.network import NetSpeed
from pyallied.mobile.mobAppium import mobAppium
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.extensions.action_helpers import ActionHelpers
from appium.webdriver.common.multi_action import MultiAction

import textwrap


class mobAppium_actions(mobAppium):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    def click(self,locatorType, locator):
        try:
            element=super().find_elementBy(locatorType, locator)
            element.click()
        except Exception as error:
            raise error              
    '''Simulates typing into the element.

    Parameters
    value – A string for typing.

    Returns
    appium.webdriver.webelement.WebElement
    '''
    def send_Keys(self,locatorType, locator,*value: str):
        try:
            element=super().find_elementBy(locatorType, locator)
            element.send_keys(*value)
        except Exception as error:
            raise error                
    '''Clears text.

    Override for Appium

    Returns
    appium.webdriver.webelement.WebElement
    '''          
    def clear(self,locatorType, locator):
        try:
            element=super().find_elementBy(locatorType, locator)
            element.clear()
        except Exception as error:
            raise error           
    def get_text(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.text
        except Exception as error:
            raise error
    '''Get an element's tag name

    '''            
    def get_tagName(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.tag_name
        except Exception as error:
            raise error 
    '''Get the value of an element's attribute
    '''            
    def get_attribute(self,locatortype,locator,attributeName:str):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.get_attribute(attributeName)
        except Exception as error:
            raise error 
    '''Determine if a form or form-like element (checkbox, select, etc...) is selected
    '''            
    def is_Selected(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.is_selected()
        except Exception as error:
            raise error 
    '''Determine if an element is currently enabled
    '''
    def is_Enabled(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.is_enabled()
        except Exception as error:
            raise error 
    '''Determine if an element is currently displayed
    '''
    def is_Displayed(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.is_displayed()
        except Exception as error:
            raise error
    '''propertylocation: Dict[str, float]
        Retrieves the current location
        Returns
        A dictionary whose keys are
        latitude (float)

        longitude (float)

        altitude (float)
    '''
    def get_location(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.location
        except Exception as error:
            raise error  
    '''Determine an element's size in pixels''' 
    def get_Element_size_inPixel(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.size
        except Exception as error:
            raise error 
    '''Gets dimensions and coordinates of an element
    ''' 
    def get_Element_dimensions_coordinates(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.rect
        except Exception as error:
            raise error 
    '''Query the value of a web element's computed CSS property
    ''' 
    def get_value_of_css_property(self,locatortype,locator,cssProperty:str):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.value_of_css_property(cssProperty)
        except Exception as error:
            raise error
    '''Determine an element's location on the screen once it has been scrolled into view (mainly an internal command and not supported by all clients)
    Gets the location of an element relative to the view.

    Usage:
    location = element.location_in_view
    x = location[‘x’]
    y = location[‘y’]
    Returns
    The location of an element relative to the view

    Return type
    dict
    
    '''
    def get_location_in_view(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.location_in_view
        except Exception as error:
            raise error 
    '''Submit a FORM element'''
    def submit_Form_element(self,locatortype,locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            return element.submit()
        except Exception as error:
            raise error 
    '''Gets the active element of the current session'''
    def get_active_element(self):
        try:
            element=self.driver.switch_to.active_element
            return element
        except Exception as error:
            raise error             
    '''Move the mouse by an offset of the specificed element'''
    def Move_the_mouse_by_an_offset(self,locatortype, locator,x_offset:int,y_offset:int):
        try:
            element=super().find_elementBy(locatortype, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(element, x_offset, y_offset)
            actions.perform()
        except Exception as error:
            raise error
    '''Click any mouse button at the current mouse coordinates
    '''        
    def Move_the_mouse_toEleement_click(self,locatortype, locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click()
            actions.perform()
        except Exception as error:
            raise error 
    '''Click any mouse button at the current mouse coordinates
    '''        
    def Move_the_mouse_toEleement_SubElement_click(self,locatortype, locator_1,locator_2):
        try:
            element_1=super().find_elementBy(locatortype, locator_1)
            element_2=super().find_elementBy(locatortype, locator_2)
            actions = ActionChains(self.driver)
            actions.move_to_element(element_1)
            actions.click(element_2)
            actions.perform()
        except Exception as error:
            raise error             
    '''Double-clicks at the current mouse coordinates (set by moveto).
    '''                   
    def Move_the_mouse_toEleement_double_click(self,locatortype, locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.double_click()
            actions.perform()
        except Exception as error:
            raise error 
    '''Click and hold the left mouse button at the current mouse coordinates
    '''
    def Move_the_mouse_toEleement_click_and_hold(self,locatortype, locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click_and_hold()
            actions.perform()
        except Exception as error:
            raise error
    '''Releases the mouse button previously held'''
    def Move_the_mouse_toEleement_release(self,locatortype, locator):
        try:
            element=super().find_elementBy(locatortype, locator)
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click_and_hold()
            actions.move_to_element(element)
            actions.release()
            actions.perform()
        except Exception as error:
            raise error
    '''Single tap on the touch enabled device''' 
    def single_tap_element(self,locatortype, locator):
        try:
            if super().find_elementBy(locatortype, locator):
                element=super().find_elementBy(locatortype, locator)
                actions = TouchAction(self.driver)
                actions.tap(element)
                actions.perform()
        except Exception as error:
            raise error
    '''Double tap on the touch screen using finger motion events
    ''' 
    def double_tap_element(self,locatortype, locator):
        try:
            if super().find_elementBy(locatortype, locator):
                element=super().find_elementBy(locatortype, locator)
                actions = TouchAction(self.driver)
                actions.tap(element,count=2)
                actions.perform()
        except Exception as error:
            raise error 
    
    '''Finger down/press on the screen'''  
    def finger_press_and_move(self,locatortype, locator,x_offset:int,y_offset:int):
        try:
            if super().find_elementBy(locatortype, locator):
                element=super().find_elementBy(locatortype, locator)
                actions = TouchAction(self.driver)
                actions.press(element)
                actions.wait(2)
                actions.move_to(x=x_offset, y=y_offset)
                actions.wait(1)
                actions.perform()
        except Exception as error:
            raise error
    '''Finger up on the screen''' 
    def finger_press_move_Release(self,locatortype, locator,x_offset:int,y_offset:int):
        try:
            if super().find_elementBy(locatortype, locator):
                element=super().find_elementBy(locatortype, locator)
                actions = TouchAction(self.driver)
                actions.press(element)
                actions.wait(2)
                actions.move_to(x=x_offset, y=y_offset)
                actions.wait(2)
                actions.release()
                actions.perform()
        except Exception as error:
            raise error
    '''Long press on the touch screen using finger motion events
    ''' 
    def finger_long_Press(self,locatortype, locator,duration:int):
        try:
            if super().find_elementBy(locatortype, locator):
                element=super().find_elementBy(locatortype, locator)
                actions = TouchAction(self.driver)
                actions.long_press(element,duration=duration)
                actions.perform()
        except Exception as error:
            raise error
    '''Scroll on the touch screen using finger based motion events
    Scrolls from one element to another
    ''' 
    def finger_touch_scroll(self,locatortype, locator_1,locator_2):
        try:
            if super().find_elementBy(locatortype, locator_1) and super().find_elementBy(locatortype, locator_2) :
                element_1=super().find_elementBy(locatortype, locator_1)
                element_2=super().find_elementBy(locatortype, locator_2)
                actions = ActionHelpers(self.driver)
                actions.scroll(element_1,element_2)
                
        except Exception as error:
            raise error
    '''Flick on the touch screen using finger motion events
        Flick from one point to another point.
    ''' 
    def finger_touch_flick(self, start_x: int, start_y: int, end_x: int, end_y: int):
        try:
                actions = ActionHelpers(self.driver)
                actions.flick(start_x,start_y,end_x,end_y)
                
        except Exception as error:
            raise error
    '''Flick on the touch screen using finger motion events
        Flick from one point to another point.
    ''' 
    def finger_Multi_touchAction(self, start_x: int, start_y: int, end_x: int, end_y: int):
        print('TODO') 
    '''Change focus to another window (Web context only)
    ''' 
    def switch_toWindow(self,windowHandle):
        try:
            self.driver.switch_to.window(windowHandle)
        except Exception as error:
            raise error 
    '''Close the current window (Web context only)
    ''' 
    def close_window(self):
        try:
            self.driver.close()
        except Exception as error:
            raise error  
    '''Retrieve the current window handle (Web context only)
    '''           
    def get_current_window_handle(self):
        try:
            return self.driver.current_window_handle
        except Exception as error:
            raise error
    '''Retrieve the all window handles (Web context only)
    '''              
    def get_all_window_handles(self):
        try:
            return self.driver.window_handles
        except Exception as error:
            raise error 
    '''Get the current page title (Web context only)
    '''              
    def get_title(self):
        try:
            return self.driver.title
        except Exception as error:
            raise error 
    '''Get the size of the specified window (Web context only)
    '''
    def get_windowSize_Dimensions(self,windowHandle=None):
        try:
            if (windowHandle !=None):
                return self.driver.get_window_size(windowHandle)
            else:
                return self.driver.get_window_size()   
        except Exception as error:
            raise error
    '''set the size of the current window (Web context only)
    '''
    def set_windowSize_Dimensions(self,width,height,windowHandle: str = 'current'):
        try:

                self.driver.set_window_size(width,height,windowHandle)
  
        except Exception as error:
            raise error 
    '''Get the position of the specified window (Web context only)
    '''
    def get_window_position(self,windowHandle=None):
        try:
            if (windowHandle !=None):
                return self.driver.get_window_position(windowHandle)
            else:
                return self.driver.get_window_position()   
        except Exception as error:
            raise error 
    '''Change the position of the specified window (Web context only)
    '''
    def set_window_position(self,x,y,windowHandle: str = 'current'):
        try:
            self.driver.set_window_position(x,y,windowHandle)
  
        except Exception as error:
            raise error  
    '''Maximize the specified window (Web context only)
    '''
    def maximize_window(self):
        try:
            self.driver.maximize_window()
  
        except Exception as error:
            raise error
    '''Navigate to a new URL (Web context) or open an Appium deep link (Native)
    ''' 
    def goto_url(self,url:str):
        try:
            self.driver.get(url)
  
        except Exception as error:
            raise error
    '''Navigate to a new URL (Web context) or open an Appium deep link (Native)
    ''' 
    def get_current_url(self):
        try:
            return self.driver.current_url
  
        except Exception as error:
            raise error
    '''Navigate backwards in the browser history, if possible (Web context only'''
    def navigate_back(self):
        try:
            return self.driver.back()
  
        except Exception as error:
            raise error 
    '''Navigate forwards in the browser history, if possible (Web context only'''
    def navigate_forward(self):
        try:
            return self.driver.forward()
  
        except Exception as error:
            raise error 
    '''Refresh the current page. (Web context only)
    '''                                                   
    def refresh_current_page(self):
        try:
            return self.driver.refresh()
  
        except Exception as error:
            raise error
    '''Retrieve all cookies visible to the current page (Web context only)
    '''                                                   
    def get_cookies(self):
        try:
            return self.driver.get_cookies()
  
        except Exception as error:
            raise error
    '''Set a cookie (Web context only)
    '''                                                   
    def set_cookies(self,cookie:Dict[str,str]):
        try:
             self.driver.add_cookie()
  
        except Exception as error:
            raise error
    '''Delete the cookie with the given name (Web context only)''' 
    def delete_cookie(self,cookieName:str):
        try:
            self.driver.delete_cookie(cookieName)

  
        except Exception as error:
            raise error 
    '''Delete all cookies visible to current page (Web context only)'''  
    def delete_All_cookie(self):
        try:
            self.driver.delete_all_cookies()

  
        except Exception as error:
            raise error
    '''Change focus to another frame on the page (Web context only)
    Switches focus to the specified frame, by index, name, or webelement.

        :Args:

        frame_reference: The name of the window to switch to, an integer representing the index, or a webelement that is an (i)frame to switch to.
        :Usage:
            :

        driver.switch_to.frame('frame_name')
        driver.switch_to.frame(1)
        driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])
    '''
    def switchTo_Frame(self,frame_reference: Any):
        try:
            self.driver.switch_to.frame(frame_reference)
  
        except Exception as error:
            raise error 
    '''Change focus to the parent context (Web context only)''' 
    def switch_to_parent_Frame(self):
        try:
            self.driver.switch_to.parent_frame()
  
        except Exception as error:
            raise error
    '''Inject a snippet of JavaScript into the page for execution in the context of the currently 
    selected frame (Web context only''' 
    def driver_execute_async_script(self,script):
        try:
            self.driver.execute_async_script(script)
  
        except Exception as error:
            raise error
    '''Inject a snippet of JavaScript into the page for execution in the context of the currently 
    selected frame (Web context). Run a native mobile command (Native Context).
    ex:self.driver.execute_script("mobile: scroll", {'direction': 'down'})
   ''' 
    def driver_execute_script(self,script):
        try:
            self.driver.execute_script(script)
  
        except Exception as error:
            raise error                                                                   
