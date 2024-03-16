
# pyautogui
import pyautogui
import pyperclip
import autoit
import pytesseract
from PIL import ImageGrab

from automatic.common import Descriptor
import automatic.common as common
from automatic.common.exceptions import *
from automatic.win32.elements import Image, is_window, Control, Title, Text

from typing import Union
from pyscreeze import Point

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
            raise ElementNotFoundException(desc, "activate")

        if is_window(desc):
            timeout = get_or(desc.timeout(), self.__timeout)
            self.__activate_window(elem, timeout)


    def get_position(self, desc:Image) -> Union[Point, None]:
        """
        Get a center position of the image
        """
        timeout = get_or(desc.timeout(), self.__timeout)
        return common.wait(lambda: pyautogui.locateCenterOnScreen(
           desc.path(), grayscale=desc.grayscale(), confidence=desc.confidence()), timeout=timeout)

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
        _ = pytesseract.get_tesseract_version()

        def _get_position(title, text):
            # 1. windows coordinate
            bbox = autoit.win_get_pos(title)
            # 2. capture
            screenshot = ImageGrab.grab(bbox=bbox) # (left, top, right, bottom)
            # 3. ocr
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            # 4. get position
            for i, word in enumerate(data['text']):
                if word == desc.path():
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
            raise ElementNotFoundException(desc, "click")

        self.wait(desc)

        if isinstance(elem, Point):
            self.__click_point(elem)
        elif isinstance(elem, Control):
            self.__click_control(elem)
        else:
            raise InvalidOperationException(desc, "click")

    def __click_control(self, ctrl: Control):
        if not ctrl:
            return

        parent = ctrl.parent()
        if not parent:
            raise Exception(f"Control should have parent. {ctrl}")
        
        autoit.control_click(parent.path(), ctrl.path())


    def __click_point(self, pos: Point):
        if pos is None:
            return
        pyautogui.click(pos)

    def type(self, desc: Descriptor, text):
        self.click(desc)
        pyautogui.typewrite(text)

