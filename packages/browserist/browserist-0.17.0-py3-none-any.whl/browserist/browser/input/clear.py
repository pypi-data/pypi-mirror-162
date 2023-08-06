from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from ...constant import timeout
from ...exception.element import NoElementFoundException
from ...exception.timeout import WaitForElementTimeoutException
from ...model.type.xpath import XPath
from ..wait.for_element import wait_for_element


def input_clear(driver: object, xpath: str, timeout: float = timeout.DEFAULT) -> None:
    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    try:
        input_field_element = driver.find_element(By.XPATH, xpath)  # type: ignore
        input_field_element.clear()
    except TimeoutException:
        raise WaitForElementTimeoutException(driver, xpath) from TimeoutException
    except NoSuchElementException:
        raise NoElementFoundException(driver, xpath) from NoSuchElementException
