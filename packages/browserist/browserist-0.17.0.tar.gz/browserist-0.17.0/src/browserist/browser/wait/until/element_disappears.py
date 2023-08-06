from .... import helper
from ....constant import timeout
from ....model.type.xpath import XPath
from ...check_if.is_displayed import check_if_is_displayed


def wait_until_element_disappears(driver: object, xpath: str, timeout: float = timeout.DEFAULT) -> None:
    xpath = XPath(xpath)
    helper.retry.until_condition_is_false(driver, xpath, func=check_if_is_displayed, timeout=timeout)
