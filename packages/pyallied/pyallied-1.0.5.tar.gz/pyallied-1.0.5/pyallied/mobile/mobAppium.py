import base64
from distutils.log import error
from typing import Dict,Optional,List,Any
from base64 import b64encode
from xmlrpc.client import boolean
#from selenium.webdriver.common.utils import is_url_connectable
from selenium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common import utils
from appium.protocols.webdriver.can_execute_scripts import CanExecuteScripts
import polling2
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException
from appium.webdriver.extensions.keyboard import Keyboard
from pyallied.mobile.logTypes import logTypes
from pyallied.mobile.AndroidPoweOptions import android_poweroptions
from pyallied.mobile.key_event_keyCodes import key_codes
from appium.webdriver.extensions import keyboard
from pyallied.mobile.gsm import GsmCallActions
from pyallied.mobile.gsm import GsmSignalStrength
from pyallied.mobile.gsm import GsmVoiceState
from pyallied.mobile.network import NetSpeed

import textwrap


class mobAppium:
    def __init__(self, driver):
        self.driver = driver
        '''
        Returns information about whether a remote end is in a state in which it can create new sessions 
        and can additionally include arbitrary meta information that is specific to the implementation.
        usage: selenium.webdriver.common.utils.is_url_connectable(port)


        '''

    def get_Remote_Driver_Status(self, port):
        utils.is_url_connectable(port)

        '''
        Execute a variety of native, mobile commands that aren't associated with a specific endpoint

        Syntax is execute("mobile: <commandName>", <JSON serializable argument>)
        
        useage: self.driver.execute_script("mobile: scroll", {'direction': 'down'})


        '''

    def execute_Mobile_Command(self, Mobilecommand: str, parameters: Dict[str, any]):
        self.driver.execute_script(Mobilecommand, parameters)
        '''
        The server should attempt to create a session that most closely matches the desired and required capabilities.

        JSONWP Spec Required capabilities have higher priority than desired 
        capabilities and must be set for the session to be created
        W3C Spec capabilities.alwaysMatch must be set for session to be created; 
        capabilities.firstMatch must match at least one (the first one to match will be used)

        useage:
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '7.0',
            'deviceName': 'Android Emulator',
            'automationName': 'UiAutomator2',
            'app': PATH('/path/to/app')
            }
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)

        '''

    def create_NewSession(self, hostAddress: str, desired_caps: Dict[str, str]):
        self.driver = webdriver.Remote(hostAddress, desired_caps)
        '''
        end the session
        '''

    def end_Session(self):
        self.driver.quit()
        ''' Returns dict of capabilities '''

    def get_Session_Capabilities(self):
        desired_caps = self.driver.session
        ''' 
        Navigate backwards in the driver history, if possible (Web context only)

        '''

    def go_Back(self):
        self.driver.back()
        '''
        Take a screenshot of the current viewport/window/page
        Takes a screenshot of the viewport in a native context (iOS, Android) and 
        takes a screenshot of the window in web context

        Note that some platforms may have settings that prevent screenshots from being taken, 
        for security reason. One such feature is the Android FLAG_SECURE layout parameter


        '''

    def take_screenshot(self):
        screenshotBase64 = self.driver.get_screenshot_as_base64()
        return screenshotBase64

        '''
        Get the current application hierarchy XML (app) or page source (web)
        In a web context, the source returns the source HTML of the current window. 
        In a native context (iOS, Android, etc...) it will return the application hierarchy XML.

        This method is useful for inspecting your application hierarchy and using that to write selectors

        (NOTE: iOS and Android don't have standard ways of defining their application source, 
        so on calls to 'Get Page Source' Appium traverses the app hierarchy and creates an XML document. 
        Thus, getting the source can often be an expensive and time-consuming operation)


        '''

    def get_PageSource(self):
        source = self.driver.page_source
        return source
        '''
        Configure the amount of time that a particular type of operation can execute for before they are aborted


        '''

    def set_PageLoad_Timeout(self, timeout: int):
        self.driver.set_page_load_timeout(timeout)

        '''Set the amount of time, in milliseconds, that asynchronous scripts executed by execute async are 
        permitted to run before they are aborted (Web context only)
        
        '''

    def set_scriptLoad_Timeout(self, timeout: int):
        self.driver.set_script_timeout(timeout)
        '''
        Set the amount of time the driver should wait when searching for elements
        '''

    def set_Implicit_Wait_Timeout(self, timeout: int):
        self.driver.implicitly_wait(5)  # waits 5 seconds
        '''
        Inject a snippet of JavaScript into the page for execution in the context of the currently 
        selected frame (Web context only)
        
        Args:	
        script: The JavaScript to execute.
        *args: Any applicable arguments for your JavaScript.
        Usage:	
        script = "var callback = arguments[arguments.length - 1]; " \
                "window.setTimeout(function(){ callback('timeout') }, 3000);"
        driver.execute_async_script(script
        '''

    def execute_Async_Script(self, script: str, *args):
        self.driver.execute_async_script(script,*args)

        '''
        execute_script(script, *args)¶
        Synchronously Executes JavaScript in the current window/frame.

        Args:	
        script: The JavaScript to execute.
        *args: Any applicable arguments for your JavaScript.
        Usage:	
        driver.execute_script('return document.title;')
        '''

    def execute_Script(self, script: str, *args):
        self.driver.execute_script(script,*args)
        '''
        Get the current device/driver orientation
        '''

    def get_Orientation(self):
        orientation = self.driver.orientation
        return orientation
        '''
        Set the current device/driver orientation
        '''

    def set_Orientation(self, orientation: str):
        self.driver.orientation = orientation

        '''
        Get the current geo location
        '''

    def get_geoLocation(self):
        location = self.driver.location()
        return location

    def find_elementBy(self, locatorType, locator):
        #print('print----',self.__with_findElement(locatorType, locator))
        return self.__with_findElement(locatorType, locator)

    def find_elements_By(self, locatorType: str, locator: any):

        #print (self.__with_findElements(self,locatorType, locator))
        return self.__with_findElements(locatorType, locator)

    def __with_findElements(self, locatorType, locator):

        if locatorType == "XPATH":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.XPATH, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                #print(elements," elemet is")
                return elements
            except Exception as error:
                #print(error," error is")
                return error
        if locatorType == "ANDROID_UIAUTOMATOR":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception as error:
                return error
        if locatorType == "ANDROID_VIEWTAG":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.ANDROID_VIEWTAG, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception as error:
                return error
        if locatorType == "ANDROID_DATA_MATCHER":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.ANDROID_DATA_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception as error:
                return error
        if locatorType == "ANDROID_VIEW_MATCHER":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.ANDROID_VIEW_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=5, timeout=30)
                return elements
            except Exception as error:
                return error
        if locatorType == "ACCESSIBILITY_ID":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception as error:
                return error
        if locatorType == "IMAGE":
            try:
                elements = polling2.poll(lambda: self.driver.find_elements(AppiumBy.IMAGE, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception as error:
                return error

    def __with_findElement(self, locatorType, locator):

        if locatorType == "XPATH":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.XPATH, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                
                return element
            except Exception as error:
                return error
        if locatorType == "ANDROID_UIAUTOMATOR":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception as error:
                return error
        if locatorType == "ANDROID_VIEWTAG":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.ANDROID_VIEWTAG, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception as error:
                return error
        if locatorType == "ANDROID_DATA_MATCHER":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.ANDROID_DATA_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception as error:
                return error
        if locatorType == "ANDROID_VIEW_MATCHER":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.ANDROID_VIEW_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=5, timeout=30)
                return element
            except Exception as error:
                return error
        if locatorType == "ACCESSIBILITY_ID":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception as error:
                return error
        if locatorType == "IMAGE":
            try:
                element = polling2.poll(lambda: self.driver.find_element(AppiumBy.IMAGE, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception as error:
                return error
    def getLog_Types(self):
        try:
            log_types = self.driver.log_types
            return log_types
        except Exception as error:
            raise error    
            
    '''Get the log for a given log type. Log buffer is reset after each request

    '''            
    def getLogs(self,logType:logTypes):
        try:
            logs = self.driver.get_log(logType)
            return error
        except Exception as error:
            raise error 
    '''
    Log a custom event on the Appium server. (Since Appium 1.16.0)

    Parameters
    vendor – The vendor to log

    event – The event to log

    Usage:
    driver.log_event(‘appium’, ‘funEvent’)

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘LogEvent’]
    '''        
    def Log_Event(self,vendor: str, event: str):
        try:
            self.driver.logEvent(vendor, event)  
        except Exception as error:
            raise error
    '''
    Retrieves events information from the current session (Since Appium 1.16.0)

    Parameters
    type – The event type to filter with
    
    '''        
    def Get_Event(self,type: Optional[List[str]] = None):
        try:
            self.driver.logEvent(type)  
        except Exception as error:
            raise error
    '''
    Set settings for the current session.

    For more on settings, see: https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md

    Parameters
    settings – dictionary of settings to apply to the current test session
    '''                    
    def Update_Settings(self,settings: Dict[str, Any]):
        try:
            self.driver.update_settings(settings)  
        except Exception as error:
            raise error 
    '''
    Returns the appium server Settings for the current session.

    Do not get Settings confused with Desired Capabilities, they are separate concepts. 
    See https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md

    Returns
    Current settings
    '''        
    def Get_settings(self):
        try:
            self.driver.get_settings()  
        except Exception as error:
            raise error
    '''
            execute_driver(script: str, script_type: str = 'webdriverio', timeout_ms: Optional[int] = None)→ Any
        Run a set of script against the current session, allowing execution of many commands in one Appium request. Please read http://appium.io/docs/en/commands/session/execute-driver for more details about the acceptable scripts and the output format.

        Parameters
        script – The string consisting of the script itself

        script_type – The name of the script type. Defaults to ‘webdriverio’.

        timeout_ms – The number of ms Appium should wait for the script to finish before killing it due to timeout_ms.

        Usage:
        self.driver.execute_driver(script=’return [];’)
        self.driver.execute_driver(script=’return [];’, script_type=’webdriverio’)
        self.driver.execute_driver(script=’return [];’, script_type=’webdriverio’, timeout_ms=10000)
        Returns
        The result of the script. It has ‘result’ and ‘logs’ keys.

        Return type
        ExecuteDriver.Result

        Raises
        WebDriverException – If something error happenes in the script. The message has the original error message.
    
    '''        
    def execute_Driver(self,script: str, script_type: str = 'webdriverio', timeout_inms: Optional[int] = None):
        try:
            if(timeout_inms!=None):
                self.driver.execute_driver(script=textwrap.dedent(script),script_type='webdriverio',timeout_ms=timeout_inms)
            else:
                self.driver.execute_driver(script=textwrap.dedent(script),script_type='webdriverio')     
        except Exception as error:
            raise error
    def install_app(self,apkPath:str):
        try:
            self.driver.install_app(apkPath)
        except Exception as error:
            raise error 
    def isApp_installed(self, AppName:str):
        try:
            self.driver.is_app_installed(AppName)
        except Exception as error:
            raise error  
    def Launch_App(self):
        try:
            self.driver.launch_app()
        except Exception as error:
            raise error
    '''
    Description
    Send the currently active app to the background, and either return after a certain amount of time, 
    or leave the app deactivated. There are 3 types of parameters which may be passed to this method:

    An object that looks like {"seconds": secs}, where secs is an integer designating how long, in seconds, 
    to background the app for. -1 means to deactivate the app entirely.

    null, which means to deactivate the app entirely.

    Deprecated An integer: how long, in seconds, to background the app for. 
    -1 means to deactivate the app entirely.
    iOS tests with XCUITest can also use the mobile: terminateApp method to 
    terminate the current app (see detailed documentation), and the mobile: 
    activateApp to activate an existing application on the device under test
    and moves it to the foreground (see detailed documentation).

    '''
    def sendApp_To_Background(self):
        try:
            self.driver.background_app(10)
        except Exception as error:
            raise error  
    def close_App(self):
        try:
            self.driver.close_app()
        except Exception as error:
            raise error
    def reset_App(self):
        try:
            self.driver.reset()
        except Exception as error:
            raise error
    def RemoveApp(self):
        try:
            self.driver.remove_app('com.example.AppName');

        except Exception as error:
            raise error
    def activate_App(self,app:str):
        try:
            self.driver.activate_app(app)
            #self.driver.activate_app('io.appium.android.apis') 
        except Exception as error:
            raise error
    def Terminate_App(self, app:str):
        try:
            self.driver.terminate_app('com.apple.Preferences')
        except Exception as error:
            raise error
    '''iOS tests with XCUITest can also use the mobile: queryAppState method. See detailed documentation.

    '''
    def get_App_state(self,state:str):
        try:
            state_app=self.driver.query_app_state(state)
            return state_app
        except Exception as error:
            raise error
    def get_app_Strings(self):
        try:
            appStrings = self.driver.app_strings("en", "/path/to/file")
            return appStrings
        except Exception as error:
            raise error 
    def End_Test_Coverage(self,intent:str, path:str):
        try:
            self.driver.end_test_coverage(intent, path)

        except Exception as error:
            raise error
    '''Get the content of the system clipboard

    '''
    def get_Clipboard(self):
        try:
            self.driver.get_clipboard()
        except Exception as error:
            raise error
    def get_ClipboardTest(self):
        try:
            self.driver.get_clipboard_text()
        except Exception as error:
            raise error
    def set_ClipBoard(self,textToset:str):
        try:
            self.driver.set_clipboard(textToset)
        except Exception as error:
            raise error
    def set_Clipboard_Text(self,TextToSet:str):
        try:
            self.driver.set_clipboard_text(TextToSet)
        except Exception as error:
            raise error 
    '''
    For Android emulator. To set the state of the battery charger to connected or not.

    '''
    def Set_Power_ac_forEmulator(self,powerMode:android_poweroptions):
        try:
            self.driver.set_power_ac(powerMode)
        except Exception as error:
            raise error 
    '''Emulate power capacity change on the connected emulator.

    '''
    def set_power_capacity_forEmulator(self,percentage:int):
        try:
            self.driver.set_power_capacity(50)
        except Exception as error:
            raise error
    '''Place a file onto the device in a particular place

    '''        
    def push_file_To_Device_From_Location(self,destinationPath:str,data:str):
        try:
            self.driver.push_file(destinationPath, base64.b64encode(data).decode('utf-8'))
        except Exception as error:
            raise error    
                      
    '''Retrieve a file from the device's file system


    '''        
    def pull_file_from_Device(self,filePathInDevice:str):
        try:
            filein_base64=self.driver.pull_file(filePathInDevice)
            return filein_base64

        except Exception as error:
            raise error
    '''Retrieve a folder from the device's file system

    ''' 
    def pull_folder_from_Device(self,filePathInDevice:str):
        try:
            folderin_base64=self.driver.pull_folder(filePathInDevice)
            return folderin_base64

        except Exception as error:
            raise error
    def shake_device(self):
        try:
            self.driver.shake()
        except Exception as error:
            raise error
    def lock_device(self):
        try:
            self.driver.lock()
        except Exception as error:
            raise error
    def unlock_device(self):
        try:
            self.driver.unlock()
        except Exception as error:
            raise error
    def isDevice_Locked(self):
        try:
            self.driver.is_locked()
        except Exception as error:
            raise error 
    '''See https://developer.android.com/reference/android/view/KeyEvent.html for reference of available Android key code values
    Sends a keycode to the device.

        Android only. Possible keycodes can be found in http://developer.android.com/reference/android/view/KeyEvent.html.

        Parameters
        keycode – the keycode to be sent to the device

        metastate – meta information about the keycode being sent

        flags – the set of key event flags

        Returns
        Self instance

        Return type
        Union[‘WebDriver’, ‘Keyboard’]
    
    '''          
    def press_Key_code(self,keycode: int, metastate: Optional[int] = None, flags: Optional[int] = None):
        try:
            #print('---')
            self.driver.press_keycode(keycode,metastate,flags)

        except Exception as error:
            raise error
    '''
    Sends a long press of keycode to the device.

    Android only. Possible keycodes can be found in http://developer.android.com/reference/android/view/KeyEvent.html.

    Parameters
    keycode – the keycode to be sent to the device

    metastate – meta information about the keycode being sent

    flags – the set of key event flags

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘Keyboard’]
    '''        
    def Logng_press_Key_code(self,keycode: int, metastate: Optional[int] = None, flags: Optional[int] = None):
        try:
            self.driver.long_press_keycode(keycode,metastate,flags)

        except Exception as error:
            raise error 
    '''
    Hides the software keyboard on the device.

    In iOS, use key_name to press a particular key, or strategy. In Android, no parameters are used.

    Parameters
    key_name – key to press

    key –

    strategy – strategy for closing the keyboard (e.g., tapOutside)

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘Keyboard’]
    '''
    def Hide_Key_Board(self,key_name: Optional[str] = None, key: Optional[str] = None, strategy: Optional[str] = None):
        try:
            self.driver.hide_keyboard(key_name,key,strategy)
        except Exception as error:
            raise error 
    '''
    Attempts to detect whether a software keyboard is present

    Returns
    True if keyboard is shown
    '''
    def is_keyboard_Shown(self):
        try:
            self.driver.is_keyboard_shown()
        except Exception as error:
            raise error
    '''
    Sends a keycode to the device.

    Android only. Possible keycodes can be found in http://developer.android.com/reference/android/view/KeyEvent.html.

    Parameters
    keycode – the keycode to be sent to the device

    metastate – meta information about the keycode being sent

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘Keyboard’]
    '''
    def key_Event(self,keycode: key_codes, metastate: Optional[int] = None):
        try:
            self.driver.keyevent(keycode,metastate)
        except Exception as error:
            raise error                           
    '''
    Switch the state of the WiFi service. Since Android Q, a method to change the WiFi service state has been restricted. 
    #12327 Please toggle the state via UI instead of this method. The UI flow depends on devices. 
    # Please make sure to encode the correct UI flow on your target device under test
    '''
    def toggle_wifi_Service(self):
        try:
            self.driver.toggle_wifi()
        except Exception as error:
            raise error    
    '''
    Switch the state of the location service
    ''' 
    def toggle_location_Services(self):
        try:
            self.driver.toggle_location_services()
        except Exception as error:
            raise error              

    '''
    Simulate an SMS message (Emulator only)
    ''' 
    def send_sms_emulatorOnly(self,number:str,message:str):
        try:
            self.driver.send_sms(number, message)
        except Exception as error:
            raise error    
    '''
    Make GSM call (Emulator only)
    '''
    def make_GSM_call_emulatorOnly(self, number:str,callActions:GsmCallActions ):
        try:
            self.driver.makeGsmCall("5551234567", callActions) 
        except Exception as error:
            raise error    
    '''Set GSM signal strength (Emulator only)

    ''' 
    def set_GSM_signal_strength_emulatorOnly(self,signalStrength:GsmSignalStrength):
        try:
            self.driver.set_gsm_signal(signalStrength) 
        except Exception as error:
            raise error 
    '''Set GSM voice state (Emulator only)

    '''        
    def set_GSM_signal_emulatorOnly(self,gsmVoice:GsmVoiceState):
        try:
            self.driver.set_gsm_voice(gsmVoice)
        except Exception as error:
            raise error 
    '''Set network speed (Emulator only)
    '''                            
    def set_network_speed_emulatorOnly(self,netSpeed:NetSpeed):
        try:
            self.driver.set_network_speed(netSpeed)
        except Exception as error:
            raise error 
    '''
    Returns the information of the system state which is supported to read as like cpu, memory, network traffic, and battery
    ex: self.driver.get_performance_data(‘my.app.package’, ‘cpuinfo’, 5)
    Android only.

    Parameters
    package_name – The package name of the application

    data_type – The type of system state which wants to read. It should be one of the supported performance data types. Check get_performance_data_types() for supported types

    data_read_timeout – The number of attempts to read
    '''        
    def get_performance_Data(self,package_name: str, data_type: str, data_read_timeout: Optional[int] = None):
        try:
           return self.driver.get_performance_data(package_name,data_type,data_read_timeout)
        except Exception as error:
            raise error
    '''Returns the information types of the system state which is supported to read as like cpu, memory, network traffic, and battery.
    . 
    '''         
    def get_performance_data_Types(self):
        try:
           return self.driver.get_performance_data_types()
        except Exception as error:
            raise error  
    '''Start recording screen

    '''              
    def start_recording_Screen(self):
        try:
            self.driver.start_recording_screen()
        except Exception as error:
            raise error
    '''Stop recording screen

    '''        
    def stop_recording_Screen(self):
        try:
            self.driver.stop_recording_screen()
        except Exception as error:
            raise error 
    '''Simulate touchId on iOS Simulator

    Parameters
    match – Simulates a successful touch (True) or a failed touch (False)

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘HardwareActions’]
    '''  
    def touch_id_ios_simulator(self,match:boolean):
        try:
            self.driver.touch_id(match)
        except Exception as error:
            raise error
    '''Toggle enroll touchId on iOS Simulator

    Returns
    Self instance

    Return type
    Union[‘WebDriver’, ‘HardwareActions’]
    '''        
    def toggle_touch_id_enrollment_ios_simulator(self):
        try:
            self.driver.toggle_touch_id_enrollment()
        except Exception as error:
            raise error        
    '''Open Android notifications (Emulator only)'''
    def open_notifications_andriod_emulatorOnly(self):
        try:
            self.driver.open_notifications()
        except Exception as error:
            raise error
    '''Retrieve visibility and bounds information of the status and navigation bars
        

        Android only.

        Returns
        A dictionary whose keys are
        statusBar
        visible

        x

        y

        width

        height

        navigationBar
        visible

        x

        y

        width

        height
    '''
    def get_system_Bars(self):        
        try:
            return self.driver.get_system_bars()
        except Exception as error:
            raise error 
    '''Returns the date and time from the device.

        Returns
        The date and time

        Return type
        str
    '''        
    def get_device_Time(self):        
        try:
            return self.driver.device_time
        except Exception as error:
            raise error                                  
    def get_device_Time(self,format: Optional[str] = None):        
        try:
            
            return self.driver.device_time(format)
        except Exception as error:
            raise error 
    '''Retrieve display density(dpi) of the Android device
    Get the display density, Android only

        Returns
        The display density of the Android device(dpi)

        Usage:
        self.driver.get_display_density()

        Returns
        The display density

        Return type
        int
    '''
    def get_display_density_android(self):        
        try:
            
            return self.driver.get_display_density()
        except Exception as error:
            raise error              
    '''Authenticate users by using their finger print scans on supported emulators.
        Authenticate users by using their finger print scans on supported Android emulators.

        Parameters
        finger_id – Finger prints stored in Android Keystore system (from 1 to 10)

        Returns
        TODO
    '''                                  
    def finger_print_android_emulator(self,finger_id: int):        
        try:
            
            return self.driver.finger_print(finger_id)
        except Exception as error:
            raise error                              

