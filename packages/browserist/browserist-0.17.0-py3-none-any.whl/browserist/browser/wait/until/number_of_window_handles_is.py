from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore

from ....constant import timeout
from ....exception.timeout import WaitForWindowTimeoutException


def wait_until_number_of_window_handles_is(driver: object, expected_handles: int, timeout: float = timeout.DEFAULT) -> None:
    if expected_handles < 0:
        raise ValueError("Expected handles must be greater than or equal to 0.")
    try:
        WebDriverWait(driver, timeout).until(EC.number_of_windows_to_be(expected_handles))  # type: ignore
    except TimeoutException:
        raise WaitForWindowTimeoutException() from TimeoutException
