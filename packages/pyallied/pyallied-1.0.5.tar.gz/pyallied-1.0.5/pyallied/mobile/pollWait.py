import polling2, time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

class pollWait:
    def __init__(self,driver):
          self.driver=driver
    def with_findElements_byXpath(self,xpath):
        try:
            polling2.poll(lambda: self.driver.find_elements(AppiumBy.XPATH, xpath),ignore_exceptions=(NoSuchElementException,), step=5, timeout=30)
        except Exception:
            return Exception
    def with_findElement_byXpath(self,xpath):
        try:
            polling2.poll(lambda: self.driver.find_element(AppiumBy.XPATH, xpath),ignore_exceptions=(NoSuchElementException,), step=5, timeout=30)
        except Exception:
            return Exception
           