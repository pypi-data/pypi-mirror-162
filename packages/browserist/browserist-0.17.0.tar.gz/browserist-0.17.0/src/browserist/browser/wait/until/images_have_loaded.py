from selenium.webdriver.common.by import By

from .... import helper
from ....constant import timeout
from ....model.type.xpath import XPath
from ..for_element import wait_for_element


def wait_until_images_have_loaded(driver: object, xpath: str, timeout: float = timeout.DEFAULT) -> None:
    def are_all_images_loaded(driver: object, elements: list[object]) -> bool:
        return all(helper.image.is_element_loaded(driver, element) is not False for element in elements)

    xpath = XPath(xpath)
    wait_for_element(driver, xpath, timeout)
    elements: list[object] = driver.find_elements(By.XPATH, xpath)  # type: ignore
    helper.retry.until_condition_is_true(driver, elements, func=are_all_images_loaded, timeout=timeout)
