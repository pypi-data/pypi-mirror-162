import re

from ..... import constant, helper
from .....constant import timeout
from .....model.type.xpath import XPath
from ....get.text import get_text
from ...for_element import wait_for_element


def wait_until_text_equals(driver: object, xpath: str, regex: str, timeout: float = timeout.DEFAULT) -> None:
    def is_element_text(driver: object, xpath: str, regex: str) -> bool:
        text = get_text(driver, xpath, constant.timeout.BYPASS)
        return bool(re.match(regex, text))

    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    helper.retry.until_condition_is_true(driver, xpath, regex, func=is_element_text, timeout=timeout)
