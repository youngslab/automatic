# pyautogui
import pyautogui
import pyperclip
import autoit
import pytesseract
from PIL import ImageGrab
import cv2
import numpy as np
import os

from automatic.common import Descriptor
import automatic.common as common
from automatic.common.exceptions import *
from automatic.win32.elements import Image, is_window, Control, Title, Text

from typing import Union
from pyscreeze import Point

from automatic.utils import Logger, LOGGER_AUTOMATIC

logger = Logger.get(LOGGER_AUTOMATIC)

pyautogui.FAILSAFE = False

def get_or(a, b) -> int:
    return a if a else b

class Context(common.Context):
    def __init__(self,* ,timeout=60, differ=0, confidence=.9, grayscale=True):
        self.__timeout = timeout 
        self.__differ = differ
        self.__confidence = confidence
        self.__grayscale = grayscale

# ---------------------
# ----- Activate ------
# ---------------------
        
    def __activate_window(self, window, timeout):
        """
        Using Autoit APIs, wait until a window activated.
        """
        try:
            autoit.win_wait(window, timeout=timeout)
        except Exception as e:
            print(f"ERROR: Failed to find a window. window={window}, e={e}")
            return False

        try:
            autoit.win_activate(window, timeout=timeout)
        except Exception as e:
            print(
                f"ERROR: Failed to activate a window. window={window}, e={e}")
            return False

        return autoit.win_active(window)

    def __activate(self, desc: Descriptor):
        if not desc:
            raise Exception("Descriptor should not be none")
        
        # activate a parent
        parent = desc.parent()
        if parent:
            self.__activate(parent)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(self, desc, "activate")

        if is_window(desc):
            timeout = get_or(desc.timeout(), self.__timeout)
            self.__activate_window(elem, timeout)


    def get_position(self, desc:Image) -> Union[Point, None]:
        """
        Get a center position of the image
        """
        timeout = get_or(desc.timeout(), self.__timeout)
        grayscale = desc.grayscale() if desc.grayscale() else self.__grayscale
        confidence = desc.confidence() if desc.confidence() else self.__confidence
        return common.wait(lambda: pyautogui.locateCenterOnScreen(
           desc.path(), grayscale=grayscale, confidence=confidence), timeout=timeout)

    def get_position_from_text(self, desc:Text) -> Union[Point, None]:
        """
        Get a center of the text
        """
        timeout = get_or(desc.timeout(), self.__timeout)
        parent = desc.parent()
        if not parent:
            raise Exception("Descriptor should not be none")
        if not isinstance(parent, Title):
            raise Exception("Parent should be Title object")

        # To make sure that tesseract installed. Otherwise, it raise exception.
        found = False
        try:
            _ = pytesseract.get_tesseract_version()
            found = True
        except:
            pass

        if not found:
            try:
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                _ = pytesseract.get_tesseract_version()
                found = True
            except:
                pass
        
        if not found:
            raise Exception("tesseract is not found in your path. Please check your environment.")

        def _get_position(title, text):
            # 1. windows coordinate
            bbox = autoit.win_get_pos(title)
            # 2. capture
            screenshot = ImageGrab.grab(bbox=bbox) # (left, top, right, bottom)
            # 3. preprocessing
            # OpenCV는 BGR 색상 체계를 사용하므로 RGB로 변환
            image_np = np.array(screenshot)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
            gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            # 4. ocr
            config='-l kor+eng'
            data = pytesseract.image_to_data(gray_image, config=config, output_type=pytesseract.Output.DICT)
            # 5. get position
            for i, word in enumerate(data['text']):
                if word == text:
                    x = data['left'][i] + data['width'][i] / 2
                    y = data['top'][i] + data['height'][i] / 2
                    return Point(bbox[0] + x, bbox[1] + y)
            return None

        return common.wait(lambda: _get_position(parent.path(), desc.path()), timeout=timeout)

    def get(self, desc:Descriptor):
        if isinstance(desc, Image):
            return self.get_position(desc)

        if isinstance(desc, Control):
            return desc
        
        if isinstance(desc, Title):
            return desc.path()

        if isinstance(desc, Text):
            return self.get_position_from_text(desc)

        return None

# ---------------------
# ----- UTILITY -------
# ---------------------
    
    def click(self, desc: Descriptor):
        self.__activate(desc)

        elem = self.get(desc)
        if not elem:
            raise ElementNotFoundException(self, desc, "click")

        self.wait(desc)

        if isinstance(elem, Point):
            self.__click_point(elem)
        elif isinstance(elem, Control):
            self.__click_control(elem)
        else:
            raise InvalidOperationException(self, desc, "click")

    def __click_control(self, ctrl: Control):
        if not ctrl:
            return

        parent = ctrl.parent()
        if not parent:
            raise Exception(f"Control should have parent. {ctrl}")
        
        # 1. parent exisits? 
        if not autoit.win_exists(parent.path()):
            logger.error("Parent window is not found.")
            raise ElementNotFoundException(self, parent, "click")
        else:
            try:
                autoit.control_get_text(parent.path(), ctrl.path())
            except Exception as e:
                logger.error("Control is not found. " + str(e))
                raise ElementNotFoundException(self, parent, "click")
             
        if not autoit.control_click(parent.path(), ctrl.path()):
            logger.error(f"Control is not clicked. win={parent.path()}, ctrl={ctrl.path()}")
            


    def __click_point(self, pos: Point):
        if pos is None:
            return
        logger.debug(f"Click at {pos}")
        pyautogui.click(pos)

    def type(self, desc: Descriptor, text):
        self.click(desc)
        logger.debug("Typing: " + text)
        pyautogui.typewrite(text)

    def capture(self, base_filename="capture"):
        """
        Captures the current screen and saves it as an image.
        Files are saved in the ~/.iaa/log/ directory.
        """
        # Ensure the log directory exists
        log_dir = os.path.join(os.path.expanduser("~"), ".iaa", "log")
        os.makedirs(log_dir, exist_ok=True)

        # Define file path
        screenshot_filepath = os.path.join(log_dir, f"{base_filename}.png")

        # Capture screenshot
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_filepath)
            logger.info(f"Screenshot saved to {screenshot_filepath}")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")

        return [screenshot_filepath]
