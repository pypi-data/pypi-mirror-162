from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore

from .....constant import timeout
from .....exception.timeout import WaitForUrlTimeoutException
from .....model.type.url import URL


def wait_until_url_equals(driver: object, url: str, timeout: float = timeout.DEFAULT) -> None:
    url = URL(url)
    try:
        WebDriverWait(driver, timeout).until(EC.url_matches(url))  # type: ignore
    except TimeoutException:
        raise WaitForUrlTimeoutException(driver, url) from TimeoutException
