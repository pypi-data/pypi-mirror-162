from pyallied.web.webWaits import customwebDriverwait
import os
import base64
from PIL import Image
class firefox(customwebDriverwait):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    def Uninstall_addon(self,identifier):
        try:
            self.driver.uninstall_addon(identifier)
        except Exception as error:
            raise error
    '''
    Installs Firefox addon.

    Returns identifier of installed addon. This identifier can later be used to uninstall addon.

    Parameters:	
    path – Absolute path to the addon that will be installed.

    Usage:	
    driver.install_addon('/path/to/firebug.xpi')
    '''
    def Install_addon(self,path, temporary=False):
        try:
            self.driver.install_addon(path)
        except Exception as error:
            raise error
    
    def Set_context(self,context):
        try:
            self.driver.set_context(context)
        except Exception as error:
            raise error
    def Get_firefox_profile(self,context):
        try:
           return self.driver.firefox_profile
        except Exception as error:
            raise error
    '''def is_headless(self):
        #if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.headless
        else:
            raise "is headless? is allowed only on firefox" '''
    def Add_extension(self,extension='webdriver.xpi'):
        try:
           return self.driver.firefox_profile.add_extension(extension)
        except Exception as error:
            raise error
    '''sets the preference that we want in the profile.'''        
    def Set_preference(self,key, value):
        try:
            self.driver.firefox_profile.set_preference(key, value)
        except Exception as error:
            raise error      
    def get_default_capabilities(self):
        try:
           return self.driver.firefox_profile.default_capabilities
        except Exception as error:
            raise error  
    def Update_capabilities(self):
        try:
           return self.driver.firefox_profile.update_preferences()
        except Exception as error:
            raise error                          
    def get_binary_instance(self):
        try:
           return self.driver.binary()
        except Exception as error:
            raise error   
    def Set_accept_untrusted_certs(self):
        try:
           return self.driver.firefox_profile.accept_untrusted_certs
        except Exception as error:
            raise error
    def Set_assume_untrusted_cert_issuer(self):
        try:
           return self.driver.firefox_profile.assume_untrusted_cert_issuer
        except Exception as error:
            raise error
    def Get_encoded_Profile(self):
        try:
           return self.driver.firefox_profile.encoded
        except Exception as error:
            raise error
    def Get_Profile_path(self):
        try:
           return self.driver.firefox_profile.path
        except Exception as error:
            raise error
    def Get_Profile_DEFAULT_PREFERENCES(self):
        try:
           return self.driver.firefox_profile.DEFAULT_PREFERENCES 
        except Exception as error:
            raise error
    def Get_Profile_ANONYMOUS_PROFILE_NAME(self):
        try:
           return self.driver.firefox_profile.ANONYMOUS_PROFILE_NAME 
        except Exception as error:
            raise error
    def Get_Profile_port(self):
        try:
           return self.driver.firefox_profile.port 
        except Exception as error:
            raise error
    def Add_command_line_options(self,*args):
        try:
           return self.driver.binary.add_command_line_options(*args) 
        except Exception as error:
            raise error
    def kill_Binary_instance(self,*args):
        try:
           return self.driver.binary.kill() 
        except Exception as error:
            raise error
    def Launch_browser(self,profile, timeout=30):
        try:
           return self.driver.binary.launch_browser(profile, timeout=30) 
        except Exception as error:
            raise error 
    '''
        Gets the full document screenshot of the current window as a base64 encoded string
        which is useful in embedded images in HTML.

        Usage:	
        driver.get_full_page_screenshot_as_base64()
    '''
    def get_fullpage_screenshot_as_base64(self,name):
        try:
            with open(self.__web_Screenshot_Location()+"/"+name+".jpg", "wb") as fh:
                fh.write(base64.urlsafe_b64decode(self.driver.get_full_page_screenshot_as_base64()))             
             
        except Exception as error:
            raise error    

    '''
        Saves a full document screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.get_full_page_screenshot_as_file('/Screenshots/foo.png')
    '''
    def get_fullpage_screenshot_as_File(self,filename:str):
        try:
            return self.driver.get_full_page_screenshot_as_file(self.__web_Screenshot_Location()+"/"+filename+".png") 
        except Exception as error:
            raise error       
    '''get_full_page_screenshot_as_png() → str
        Gets the full document screenshot of the current window as a binary data.

        Usage:	
        driver.get_full_page_screenshot_as_png()
    '''
    def get_fullpage_screenshot_as_PNG(self,name):
        try:
            result_File=self.__web_Screenshot_Location()+"/"+name+".png"
            with open(result_File, "wb") as fh:
                fh.write(self.driver.get_full_page_screenshot_as_png())

             
        except Exception as error:
            raise error    

    ''' 
        Saves a screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.save_screenshot('/Screenshots/foo.png')
    '''
    def screenshot_save_full_page_screenshot(self,filename):
        try:
            return self.driver.save_screenshot(filename)
        except Exception as error:
            raise error
    def __web_Screenshot_Location(self):
        try:
            dir_name=os.getcwd()+"/page_Screenshots"
            os.makedirs(dir_name, exist_ok=True)
            return dir_name
        except FileExistsError:
            pass                
                                                                                                                                                                                                                        