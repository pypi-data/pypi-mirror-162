from selenium.webdriver.common.by import By

from ... import helper
from ...constant import timeout
from ...model.type.xpath import XPath
from ..wait.for_element import wait_for_element


def get_text(driver: object, xpath: str, timeout: float = timeout.DEFAULT) -> str:
    def get_inner_text_of_element(driver: object, xpath: str) -> str:
        return str(driver.find_element(By.XPATH, xpath).text)  # type: ignore

    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    return helper.retry.get_text(driver, xpath, get_inner_text_of_element)
