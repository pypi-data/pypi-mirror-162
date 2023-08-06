from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore

from .....constant import timeout
from .....exception.timeout import WaitForPageTitleToChangeTimeoutException


def wait_until_page_title_contains(driver: object, page_title_fragment: str, timeout: float = timeout.DEFAULT) -> None:
    try:
        WebDriverWait(driver, timeout).until(EC.title_contains(page_title_fragment))  # type: ignore
    except TimeoutException:
        raise WaitForPageTitleToChangeTimeoutException(driver, page_title_fragment) from TimeoutException
