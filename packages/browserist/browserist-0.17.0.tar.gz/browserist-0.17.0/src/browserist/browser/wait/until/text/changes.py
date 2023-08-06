from ..... import helper
from .....constant import timeout
from .....model.type.xpath import XPath
from ....get.text import get_text
from ...for_element import wait_for_element


def wait_until_text_changes(driver: object, xpath: str, baseline_text: str, timeout: float = timeout.DEFAULT) -> None:
    def has_text_changed(driver: object, baseline_text: str) -> bool:
        return get_text(driver, xpath) != baseline_text

    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    helper.retry.until_condition_is_true(driver, baseline_text, func=has_text_changed, timeout=timeout)
