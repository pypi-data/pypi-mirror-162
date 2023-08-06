import imp
from typing import Optional, Union

from pyallied.web.print_page_options import PrintOptions
from pyallied.web.webWaits import customwebDriverwait
from pyallied.web.log_type import log_type
from pyallied.web.file_detector import FileDetector
import os
import base64
from PIL import Image
from selenium.webdriver.remote.file_detector import UselessFileDetector
class Browser(customwebDriverwait):
    def __init__(self,driver):
        super().__init__(driver)
        self.driver=driver
        '''
        returns capabilities list
        '''    
    def get_desired_capabilities_Of_driver(self):
        try:
            return self.driver.capabilities
        except Exception as error:
            raise error              

    ''' closes the session''' 
    def close_driver(self):
        try:
            self.driver.close()
        except Exception as error:
            raise error          
    ''' quit the driver ''' 
    def quit_driver(self):
        try:
            self.driver.quit()
        except Exception as error:
            raise error          
    '''Goes one step backward in the driver history.''' 
    def go_back(self):
        try:
            self.driver.back()
        except Exception as error:
            raise error          
    '''Delete all cookies in the scope of the session.'''
    def delete_all_Cookies(self):
        try:
            self.driver.delete_all_cookies()
        except Exception as error:
            raise error                               
    '''Deletes a single cookie with the given name. '''
    def delete_a_Cookie(self,name):
        try:
            self.driver.delete_cookie(name)
        except Exception as error:
            raise error          
    '''
    Asynchronously Executes JavaScript in the current window/frame.

    Args:	
    script: The JavaScript to execute.
    *args: Any applicable arguments for your JavaScript.
    Usage:	
    script = "var callback = arguments[arguments.length - 1]; " \
            "window.setTimeout(function(){ callback('timeout') }, 3000);"
    driver.execute_async_script(script)
    '''
    def Execute_Async_Script(self,script: str, *args):
        try:
            self.driver.execute_async_script(script,*args)
        except Exception as error:
            raise error          
    '''
    Synchronously Executes JavaScript in the current window/frame.

    Args:	
    script: The JavaScript to execute.
    *args: Any applicable arguments for your JavaScript.
    Usage:	
    driver.execute_script('return document.title;')
    ''' 
    def Execute_Script(self,script: str, *args):
        try:
            self.driver.execute_script(script,*args)
        except Exception as error:
            raise error  
    '''
    Sends a command to be executed by a command.CommandExecutor.

    Args:	
    driver_command: The name of the command to execute as a string.
    params: A dictionary of named parameters to send with the command.
    Returns:	
    The command’s JSON response loaded into a dictionary object.
    '''
    def Execute_Command(self,driver_command: str, params: dict = None):
        try:
            self.driver.execute(driver_command,params)
        except Exception as error:
            raise error
    '''
    Overrides the current file detector (if necessary) in limited context. Ensures the original file detector is set afterwards.

    Example:

    with webdriver.file_detector_context(UselessFileDetector):
    someinput.send_keys(‘/etc/hosts’)
    Args:	
    file_detector_class - Class of the desired file detector. If the class is different
    from the current file_detector, then the class is instantiated with args and kwargs and used as a file detector during the duration of the context manager.
    args - Optional arguments that get passed to the file detector class during
    instantiation.
    kwargs - Keyword arguments, passed the same way as args.    
    '''  
    #def File_Detector_Context(self,file_detector_class, *args, **kwargs):
       
    '''
    Goes one step forward in the browser history.

    Usage:	
    driver.forward()
    ''' 
    def Forward(self):
        try:
            self.driver.forward()
        except Exception as error:
            raise error           
    '''
    Invokes the window manager-specific ‘full screen’ operation
    '''
    def FullScreen_Window(self):
        try:
            self.driver.fullscreen_window()
        except Exception as error:
            raise error
    def Get_Cookie(self,name):
        try:
            return self.driver.get_cookie(name)
        except Exception as error:
            raise error
    def Get_Credentials(self):
        try:
            return self.driver.get_credentials()
        except Exception as error:
            raise error 
    def Get_Log(self,log_type):
        try:
            return self.driver.get_log(log_type)
        except Exception as error:
            raise error
    def Get_pinned_Scripts(self):
        try:
            return self.driver.get_pinned_scripts()
        except Exception as error:
            raise error
             
    def Get_page_load_timeout(self):
        try:
            return self.driver.timeouts.page_load
        except Exception as error:
            raise error    
    def Get_implicit_wait_timeout(self):
        try:
            return self.driver.timeouts.implicit_wait
        except Exception as error:
            raise error
    def Get_script_timeout(self):
        try:
            return self.driver.timeouts.script
        except Exception as error:
            raise error
    def Get_Virtual_authenticator_id(self):
        try:
            return self.driver.virtual_authenticator_id
        except Exception as error:
            raise error

    def Get_Title(self):
        try:
            return self.driver.title
        except Exception as error:
            raise error
    def Set_implicitly_wait(self,time_to_wait):
        try:
            self.driver.implicitly_wait(time_to_wait)
        except Exception as error:
            raise error
    def Pin_script(self,script, script_key=None):
        try:
            if(script_key!=None):
                self.driver.pin_script(script,script_key)
            else:
                 self.driver.pin_script(script)   
        except Exception as error:
            raise error
    '''Takes PDF of the current page. The driver makes a best effort to return a PDF based on the provided parameters'''        
    def Print_Page(self,print_options: Optional[PrintOptions] = None):
        try:
            self.driver.print_page(print_options)
        except Exception as error:
            raise error
    def Refresh(self):
        try:
            self.driver.refresh()
        except Exception as error:
            raise error
    '''Removes all credentials from the authenticator.'''        
    def Remove_all_credentials(self):
        try:
            self.driver.remove_all_credentials()
        except Exception as error:
            raise error
    ''' Removes a credential from the authenticator.'''        
    def Remove_credential(self,credential_id: Union[str, bytearray]):
        try:
            self.driver.remove_credential(credential_id)
        except Exception as error:
            raise error
    def Remove_virtual_authenticator(self):
        try:
            self.driver.remove_virtual_authenticator()
        except Exception as error:
            raise error
    '''
        Set the amount of time to wait for a page load to complete
    before throwing an error.
    Args:	
    time_to_wait: The amount of time to wait
    Usage:	
    driver.set_page_load_timeout(30)
    '''        
    def Set_page_load_timeout(self,time_to_wait):
        try:
            self.driver.set_page_load_timeout(time_to_wait) 
        except Exception as error:
            raise error
    '''Set the amount of time that the script should wait during an
    execute_async_script call before throwing an error.
    Args:	
    time_to_wait: The amount of time to wait (in seconds)
    Usage:	
    driver.set_script_timeout(30)
    '''         
    def set_script_timeout(self,time_to_wait):
        try:
            self.driver.set_script_timeout(time_to_wait) 
        except Exception as error:
            raise error
    '''
    Sets whether the authenticator will simulate success or fail on user verification. 
    verified: True if the authenticator will pass user verification, False otherwise.
    '''         
    def Set_user_Verified(self,verified: bool):
        try:
            self.driver.set_user_verified(verified)
        except Exception as error:
            raise error
    '''
    Sets the x,y position of the current window. (window.moveTo)

    Args:	
    x: the x-coordinate in pixels to set the window position
    y: the y-coordinate in pixels to set the window position
    Usage:	
    driver.set_window_position(0,0)
    
    '''        
    def Set_window_position(self,x, y, windowHandle='current'):
        try:
            self.driver.set_window_position(x,y)
        except Exception as error:
            raise error
    '''
    Sets the x, y coordinates of the window as well as height and width of the current window. This method is only supported for W3C compatible browsers; other browsers should use set_window_position and set_window_size.

    Usage:	
    driver.set_window_rect(x=10, y=10)
    driver.set_window_rect(width=100, height=200)
    driver.set_window_rect(x=10, y=10, width=100, height=200)
    '''        
    def Set_window_rect(self,x=None, y=None, width=None, height=None):
        try:
            self.driver.set_window_rect(x,y,width,height)
        except Exception as error:
            raise error 
    '''
    Sets the width and height of the current window. (window.resizeTo)

    Args:	
    width: the width in pixels to set the window to
    height: the height in pixels to set the window to
    Usage:	
    driver.set_window_size(800,600)
    '''
    def Set_window_size(self,width, height, windowHandle='current'):
        try:
            self.driver.set_window_size(width, height)
        except Exception as error:
            raise error
    '''Called before starting a new session. This method may be overridden to define custom startup behavior.'''        
    def Start_client(self):
        try:
            self.driver.start_client()
        except Exception as error:
            raise error
    '''
    Creates a new session with the desired capabilities.

    Args:	
    capabilities - a capabilities dict to start the session with.
    browser_profile - A selenium.webdriver.firefox.firefox_profile.FirefoxProfile object. Only used if Firefox is requested.
    '''        
    def Start_session(self,capabilities: dict, browser_profile=None):
        try:
            if(browser_profile!=None):
                self.driver.start_session(capabilities,browser_profile)
            else:
                self.driver.start_session(capabilities)   
        except Exception as error:
            raise error
    '''Called after executing a quit command. This method may be overridden to define custom shutdown behavior.'''        
    def Stop_client(self):
        try:
            self.driver.stop_client()
        except Exception as error:
            raise error 
    def Unpin(self,script_key):
        try:
            self.driver.unpin(script_key)
        except Exception as error:
            raise error
    '''Returns a ApplicationCache Object to interact with the browser app cache'''        
    def Get_application_cache(self):
        try:
            return self.driver.application_cache
        except Exception as error:
            raise error 
    '''Returns the URL of the current page.'''        
    def Get_current_url(self):
        try:
            return self.driver.current_url
        except Exception as error:
            raise error
    '''Returns the handle of the current window.''' 
    def Get_current_window_handle(self):
        try:
            return self.driver.current_window_handle
        except Exception as error:
            raise error 
    '''returns the drivers current desired capabilities being used'''        
    def Get_desired_capabilities(self):
        try:
            return self.driver.desired_capabilities
        except Exception as error:
            raise error
    def Get_desired_capabilities(self):
        try:
            return self.driver.desired_capabilities
        except Exception as error:
            raise error
    def Set_file_detector(self,detectorType:UselessFileDetector):
        try:
            self.driver.file_detector=detectorType
        except Exception as error:
            raise error
    def Get_Page_Source(self):
        try:
            return self.driver.page_source
        except Exception as error:
            raise error
    def get_command_line_args(self):
        try:
            return self.driver.service.command_line_args()
        except Exception as error:
            raise error 
    def get_assert_process_still_running(self):
        try:
            return self.driver.service.assert_process_still_running()
        except Exception as error:
            raise error
    def get_is_connectable(self):
        try:
            return self.driver.service.is_connectable()
        except Exception as error:
            raise error
    def Send_remote_shutdown_command(self):
        try:
             self.driver.service.send_remote_shutdown_command()
        except Exception as error:
            raise error
    '''
    Starts the Service.

    Exceptions:	
    WebDriverException : Raised either when it can’t start the service or when it can’t connect to the service
    '''         
    def start_service(self):
        try:
             self.driver.service.start()
        except Exception as error:
            raise error
    def stop_service(self):
        try:
             self.driver.service.stop()
        except Exception as error:
            raise error
    def get_service_url(self):
        try:
            return self.driver.service.service_url
        except Exception as error:
            raise error 
    def get_driver_name(self):
        try:
            return self.driver.name
        except Exception as error:
            raise error
    def get_orientation(self):
        try:
            return self.driver.orientation
        except Exception as error:
            raise error
    def get_timeouts(self):
        try:
            return self.driver.timeouts
        except Exception as error:
            raise error
    def get_screenshot_base64(self,name): 
        try:
            with open(self.__Screenshot_Location()+"/"+name+".jpg", "wb") as fh:
                fh.write(base64.urlsafe_b64decode(self.driver.get_screenshot_as_base64()))            
            
        except Exception as error:
            raise error
    def get_screenshot_png(self,name): 
        try:
            with open(self.__Screenshot_Location()+"/"+name+".png", "wb") as fh:
                fh.write(self.driver.get_screenshot_as_png())            
            
        except Exception as error:
            raise error
    def get_screenshot_file(self,name): 
        try:
            self.driver.get_screenshot_as_file(self.__Screenshot_Location()+"/"+name+'.png')
            
        except Exception as error:
            raise error                        
    def __Screenshot_Location(self):
        try:
            dir_name=os.getcwd()+"/page_Screenshots"
            os.makedirs(dir_name, exist_ok=True)
            return dir_name
        except FileExistsError:
            pass                                                                                                                                                                               