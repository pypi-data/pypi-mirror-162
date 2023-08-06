from ..... import helper
from .....constant import timeout
from .....model.type.url import URL
from ....get.url.current import get_current_url


def wait_until_url_changes(driver: object, baseline_url: str, timeout: float = timeout.DEFAULT) -> None:
    def has_url_changed(driver: object, baseline_url: str) -> bool:
        return get_current_url(driver) != baseline_url

    baseline_url = URL(baseline_url)
    helper.retry.until_condition_is_true(driver, baseline_url, func=has_url_changed, timeout=timeout)
