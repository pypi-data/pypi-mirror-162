from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore

from .....constant import timeout
from .....exception.timeout import WaitForPageTitleToChangeTimeoutException


def wait_until_page_title_equals(driver: object, page_title: str, timeout: float = timeout.DEFAULT) -> None:
    try:
        WebDriverWait(driver, timeout).until(EC.title_is(page_title))  # type: ignore
    except TimeoutException:
        raise WaitForPageTitleToChangeTimeoutException(driver, page_title) from TimeoutException
