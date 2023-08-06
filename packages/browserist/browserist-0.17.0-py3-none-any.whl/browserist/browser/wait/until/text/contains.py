import re

from ..... import constant, helper
from .....constant import timeout
from .....model.type.xpath import XPath
from ....get.text import get_text
from ...for_element import wait_for_element


def wait_until_text_contains(driver: object, xpath: str, regex: str, timeout: float = timeout.DEFAULT) -> None:
    def does_element_text_contain(driver: object, xpath: str, regex: str) -> bool:
        text = get_text(driver, xpath, constant.timeout.BYPASS)
        return bool(re.search(regex, text, re.IGNORECASE))

    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    helper.retry.until_condition_is_true(driver, xpath, regex, func=does_element_text_contain, timeout=timeout)
