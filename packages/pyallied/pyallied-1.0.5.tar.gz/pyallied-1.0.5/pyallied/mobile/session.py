#from tkinter import COMMAND
from typing import Union
#from click import command
from pyallied.mobile.pollWait import pollWait
from appium import webdriver 
from pyallied.mobile.mobilecommand import mobile_command
from appium.webdriver.applicationstate import ApplicationState
from appium.webdriver.extensions.device_time import DeviceTime
from appium.webdriver.extensions.location import Location
from appium.webdriver.extensions.settings import Settings
from appium.protocols.webdriver.can_execute_commands import CanExecuteCommands
from appium.webdriver.applicationstate import ApplicationState
from appium.webdriver.mobilecommand import MobileCommand
from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.switch_to import SwitchTo
class session(pollWait,Location,Settings,CanExecuteCommands,AppiumConnection,MobileCommand,ApplicationState):
    
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    def page_source(self):
        self.html=self.driver.page_source
        #print(html)
        return self.html
    def is_ServiceRunning(self):
        return self.driver.AppiumConnection.get_timeout()
    def get_Logs(self,type):
        return self.driver.get_log(type)
    def get_WindowRect(self):
        return self.driver.get_window_rect()
    def get_DesiredCaps(self):
        return self.driver.session
    def goBack(self):
        return self.driver.back()
    def take_Screenshot(self):
        screenshotBase64 = self.driver.get_screenshot_as_base64()
        return screenshotBase64
    def get_Orientation(self):
        return self.driver.orientation    
    def set_Orientation(self,orientation):
        self.driver.orientation = str(orientation)
    def get_GeoLocation(self):
        return self.driver.location

        #locationData=Location.location
        #return locationData
    def set_GeoLocation(self, latitude: Union[float, str], longitude: Union[float, str], altitude: Union[float, str] = None, speed: Union[float, str] = None, satellites: Union[float, str] = None):       
        self.driver.set_location(latitude, longitude, altitude)
    def get_Events(self):
        return self.driver.get_events()
    def get_AppStrings(self):
        return self.driver.app_strings()
    def get_DeviceTime(self):
        return self.driver.get_device_time()
    def get_Settings(self):
        return self.driver.get_settings()    
    def get_AvailableIMEengines(self):
        return self.driver.available_ime_engines
    def is_AppInstalled(self):
        return self.driver.is_app_installed()
    def get_battery_info(self):
        return self.driver.battery_info
    def switch_Context(self):
        self.driver.switch_to.context('WEBVIEW_1')
    def get_Contexts(self):
        return self.driver.contexts
    def Execute_driver_to_Get_Properties(self,command:mobile_command):
        return self.driver.execute(command)        

    

            


         

