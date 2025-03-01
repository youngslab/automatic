
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# exception
from selenium.common.exceptions import TimeoutException

# types
from typing import Union, List

from .elements import *
from ..common import wait
import automatic.common as common
from ..common.exceptions import *
import time

# sampling elements
import random

# table
import pandas as pd
from io import StringIO

from automatic.utils import Logger, LOGGER_AUTOMATIC

def get_or(a, b) -> int:
    return a if a else b

logger = Logger.get(LOGGER_AUTOMATIC)

class Context(common.Context):
    def __init__(self, driver: WebDriver, *, timeout, differ):
        self.__driver = driver
        self.__current_frame = None
        self.__default_window_handle = driver.current_window_handle
        self.__timeout = timeout
        self.__differ = differ

    def get(self, desc: Descriptor):
        if is_element(desc):
            return self.get_element(desc)
        elif is_window(desc):
            return self.get_window_handle(desc)
        elif is_alert(desc):
            return self.get_alert(desc)
        elif is_default_frame(desc):
            return desc
        else:
            # TODO: exception
            return None

    def get_all(self, desc: Descriptor):
        if is_element(desc):
            return self.get_elements(desc)
        else:
            # NotSupportedOperation
            return None

    def get_element(self, desc: Descriptor) -> Union[WebElement, None]:
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            if hasattr(desc, 'visible') and not desc.visible:
                return WebDriverWait(self.__driver, timeout).until(
                    lambda d: d.find_element(desc.by(), desc.path()))
            else:
                es = self.get_elements(desc)
                if len(es) == 0:
                    logger.debug("Failed to find an element")
                    return None
                elif len(es) > 1:
                    logger.debug("Multiple items are found")
                    return None
                else:
                    return es[0]
                # return WebDriverWait(self.__driver, timeout).until(
                #     EC.element_to_be_clickable((desc.by(), desc.path())))
        except TimeoutException:
            return None
        except Exception as e:
            logger.debug(f"ERROR: Failed to get an element xx. type={type(e)} e={e}")
            return None

    def get_elements(self, desc: Descriptor) -> List[WebElement]:
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            if hasattr(desc, 'visible') and not desc.visible:
                return WebDriverWait(self.__driver, timeout).until(
                    lambda d: [element for element in
                            d.find_elements(desc.by(), desc.path())])
            else:    
                return WebDriverWait(self.__driver, timeout).until(
                    lambda d: [element for element in
                            d.find_elements(desc.by(), desc.path())
                            if element.is_displayed() and element.is_enabled()
                                ])
        except Exception as e:
            logger.debug(f"ERROR: Failed to get elements.{type(e)} {e}")
            return []

    def get_window_handle(self, desc: Descriptor):
        timeout = get_or(desc.timeout(), self.__timeout)
        if desc.by() == "title":
            return self.__get_window_handle_with_title(desc.path(), timeout)
        elif desc.by() == "url":
            return self.__get_window_handle_with_url(desc.path(), timeout)
        else:
            # TODO: report failure
            return None
        
    def __get_current_window_handle(self):
        try:
            return self.__driver.current_window_handle
        except:
            self.set_default_window()
            return self.__driver.current_window_handle

    def __get_window_handle_with_title(self, title, timeout):
        def _get_window_handle(driver: WebDriver, title: str):
            current = self.__get_current_window_handle()
            result = None
            handles = driver.window_handles
            # handles.remove(current)
            for handle in handles:
                driver.switch_to.window(handle)
                if driver.title.find(title) >= 0:
                    result = handle
                    break
            driver.switch_to.window(current)
            return result
        return wait(lambda: _get_window_handle(self.__driver, title), timeout=timeout)

    def __get_window_handle_with_url(self, url, timeout):
        def _get_window_handle(driver: WebDriver, title: str):
            current = self.__get_current_window_handle()
            result = None
            handles = driver.window_handles
            # handles.remove(current)
            for handle in handles:
                driver.switch_to.window(handle)
                if driver.current_url.find(url) >= 0:
                    result = handle
                    break
            driver.switch_to.window(current)
            return result

        return wait(lambda: _get_window_handle(self.__driver, url), timeout=timeout)

    def close_other_windows(self):
        """
        Close all windows exept for default one. 
        """
        current = self.__driver.current_window_handle
        handles = self.__driver.window_handles
        handles.remove(current)
        for handle in handles:
            if current == handle:
                continue
            self.__driver.switch_to.window(handle)
            self.__driver.close()
        self.__driver.switch_to.window(current)

    def get_alert(self, desc: Descriptor):
        timeout = get_or(desc.timeout(), self.__timeout)
        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.alert_is_present(), "Can not find an alert window")

            alert = self.__driver.switch_to.alert
            if not desc.path() in alert.text:
                return None
            return alert
        except Exception:
            # print(f"ERROR: Failed to get an alert. {e}")
            return None

    def get_default_window_handle(self):
        return self.__default_window_handle

    def get_text(self, element) -> str:
        if isinstance(element, WebElement):
            return element.text
        else:
            # TODO: report error
            return ""

# ---------------------
# ----- UTILITY -------
# ---------------------
        
    def __activate_window(self, desc):
        handle = self.get_window_handle(desc)
        self.set_current_window(handle)


    def __activate(self, desc: Descriptor, isParent=False):
        if not desc:
            return

        # activate a parent
        parent = desc.parent()
        if parent:
            self.__activate(parent, True)

        if not isParent:
            return 

        # parent: Default frame
        if is_default_frame(desc):
            self.set_default_window()
            self.set_default_frame()
            return

        # get element
        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "activate")

        # parent: Window
        if is_window(desc):
            self.__activate_window(desc)
        elif isinstance(elem, WebElement):
            if elem.tag_name.lower() in ["frame", "iframe"]:
                if not desc.parent():
                    self.set_default_window()
                self.set_current_frame(elem)

        else:
            raise InvalidOperationException(desc, "activate")

    def __type(self, element: WebElement, text: str):
        # if not 
        try:
            element.clear()
        except Exception as e:
            pass
            
        # if element.get_attribute('value'):
        #     return False
        try:
            element.send_keys(text)
            return True
        except:
            pass 
        try:
            self.__driver.execute_script(f'arguments[0].value = "{text}"', element)
            return True
        except:
            return False

    def __click(self, element: WebElement):
        if not self.__driver or not element:
            return False
        try:
            element.click()
        except:
            self.__driver.execute_script("arguments[0].click();", element)
        return True


# ----------------------
# ------ CLICKS --------
# ----------------------


    def __differ_time(self, desc: Descriptor):
        differ = desc.differ()
        differ = differ if differ else self.__differ
        if differ != 0:
            time.sleep(differ)

    def click(self, descriptor: Descriptor):
        self.__differ_time(descriptor)

        self.__activate(descriptor)

        elem = self.get(descriptor)
        if not elem:
            raise ElementNotFoundException(descriptor, "click")

        if not isinstance(elem, WebElement):
            raise InvalidOperationException(descriptor, "click")
        
        if not self.__click(elem):
            raise OperationFailureException(descriptor, "click")

    def clicks(self, descriptor: Descriptor, *, num_samples=None):
        
        self.__differ_time(descriptor)

        # activate
        self.__activate(descriptor)

        # get all elements
        elems = self.get_all(descriptor)
        if not elems:
            raise ElementNotFoundException(descriptor, "click")

        # sample
        if num_samples:
            elems = random.sample(elems, k=num_samples)

        # execution
        for elem in elems:
            # differ
            self.__differ_time(descriptor)
            if not self.__click(elem):
                raise OperationFailureException(descriptor, "click")

# ---------------------
# ------ TYPES --------
# ---------------------
    def type(self, desc: Descriptor, text):
        self.__differ_time(desc)

        # activate
        self.__activate(desc)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "type")

        if not isinstance(elem, WebElement):
            return False
        
        if not self.__type(elem, text):
            raise OperationFailureException(desc, "click")

    def __table(self, elem: WebElement):
        try:
            return pd.read_html(StringIO(elem.get_attribute('outerHTML')))[0]
        except ValueError as e:
            logger.warning("Can't read table from given element. e={e}")
            return None

    def table(self, desc: Descriptor):
        self.__differ_time(desc)

        self.__activate(desc)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "table")

        # TODO: validate its tag is table
        return self.__table(elem)

# ---------------------
# ------ select--------
# ---------------------

    def __select(self, element: WebElement, text: str):
        select = Select(element)
        if not select:
            return False
        select.select_by_visible_text(text)
        return True

    def select(self, desc: Descriptor, text):

        self.__differ_time(desc)

        # activate
        self.__activate(desc)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "select")

        if not isinstance(elem, WebElement):
            return False

        if not self.__select(elem, text):
            return OperationFailureException(desc, "select")

    def accept(self, desc: Descriptor):
        if not desc:
            raise Exception("Descriptor should not be none")
        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "accept")
        logger.debug(f"accept: {elem.text}")
        elem.accept()
        
    def dismiss(self, desc: Descriptor):
        if not desc:
            raise Exception("Descriptor should not be none")
        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "dismiss")
        logger.debug(f"dismiss: {elem.text}")
        elem.dismiss()

    def execute_script(self, script, element):
        if not (script and element):
            return False
        self.__driver.execute_script(script, element)
        return True

    def go(self, target: Url):
        if not target.parent():
            self.set_default_window()
        else:
            self.__activate(target.parent(), True)

        if target.by() == "url":
            self.__driver.get(target.path())
            return True
        else:
            # NotSupportedDescriptor
            return False

    def get_url(self):
        return self.__driver.current_url

    def set_current_window(self, handle):
        try:
            if self.__driver.current_window_handle == handle:
                return
        except:
            pass
        self.__driver.switch_to.window(handle)

    def set_default_window(self):
        try:
            if self.__driver.current_window_handle == self.__default_window_handle:
                return
        except:
            pass
        self.__driver.switch_to.window(self.__default_window_handle)

    def set_current_frame(self, frame: WebElement):
        if frame:
            self.__current_frame = frame
            self.__driver.switch_to.frame(frame)
        else:
            self.__current_frame = None
            self.__driver.switch_to.default_content()

    def set_default_frame(self):
        if self.__current_frame:
            self.__driver.switch_to.default_content()

    def exist(self, desc: Descriptor) -> bool:
        """ 
        Special case not to rasie exception. So need to call lower-level APIs
        """
        try:
            self.__differ_time(desc)
            self.__activate(desc)
            if isinstance(desc, Xpath) and desc.multiple:
                elems = self.get_elements(desc)
                return True if elems and len(elems) >= 0 else False
            else:
                elem = self.get(desc)
                return True if elem else False
        except:
            return False

    def count(self, desc: Descriptor) -> int:
        """
        return How many elements for the descriptor
        """
        try:
            self.__activate(desc)
            elems = self.get_all(desc)
            return len(elems) if elems else 0
        except Exception as e:
            print(e)
            return 0
        

    def text(self, desc: Descriptor) -> str:
        self.__differ_time(desc)

        self.__activate(desc)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(desc, "text")

        return elem.text
