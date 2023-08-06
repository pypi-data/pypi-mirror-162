from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from ...model.type.xpath import XPath


def check_if_is_enabled(driver: object, xpath: str) -> bool:
    xpath = XPath(xpath)
    try:
        element = driver.find_element(By.XPATH, xpath)  # type: ignore
        return element.is_enabled()  # type: ignore
    except (NoSuchElementException, Exception):
        return False
