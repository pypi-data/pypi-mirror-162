""" Kameleoon data module"""
import random
from enum import Enum, IntEnum
from typing import Optional, Literal
from urllib.parse import quote

from kameleoon.exceptions import KameleoonException

ALPHA_NUMERIC_CHARS = 'abcdef0123456789'
NONCE_LENGTH = 16


class DataType(Enum):
    """Data types"""
    CUSTOM: str = "CUSTOM"
    BROWSER: str = "BROWSER"
    CONVERSION: str = "CONVERSION"
    INTEREST: str = "INTEREST"
    PAGE_VIEW: str = "PAGE_VIEW"


class BrowserType(IntEnum):
    """Browser types"""
    CHROME: int = 0
    INTERNET_EXPLORER: int = 1
    FIREFOX: int = 2
    SAFARI: int = 3
    OPERA: int = 4
    OTHER: int = 5


def get_nonce() -> str:
    """Generates alphanumeric characters"""
    return ''.join(random.choice(ALPHA_NUMERIC_CHARS) for i in range(NONCE_LENGTH))


class Data:
    """Base data class"""

    def __init__(self) -> None:
        self.nonce: str = get_nonce()
        self.sent: bool = False

    def to_dict(self):
        """Convert class instance to dict"""
        return self.__dict__

    def obtain_full_post_text_line(self) -> str:
        """
        obtain full post text line
        :return:
        """
        raise NotImplementedError

    @classmethod
    def encode(cls, to_encode: str) -> str:
        """
        Encode string to send into URL
        :param to_encode: string which need to encoded
        :type to_encode: str
        :return:
        """
        return quote(to_encode, safe="~()*!.'")


class CustomData(Data):
    """ Custom data."""
    def __init__(self, id: int, value: str):
        """
        :param id: Index / ID of the custom data to be stored. This field is mandatory.
        :type id: int
        :param value: Value of the custom data to be stored. This field is mandatory.
        :type value: str

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
        """
        # pylint: disable=invalid-name,redefined-builtin
        self.id = str(id)
        self.value: str = value
        self.instance = DataType.CUSTOM.value
        super().__init__()

    def obtain_full_post_text_line(self) -> str:
        encoded_value = self.encode(f'[["{self.value}",1]]')
        return f"eventType=customData&index={self.id}&valueToCount={encoded_value}&overwrite=true&nonce={self.nonce}"


class Browser(Data):
    """ Browser data."""

    def __init__(self, browser_type: Literal[
            BrowserType.CHROME, BrowserType.INTERNET_EXPLORER,
            BrowserType.FIREFOX, BrowserType.SAFARI,
            BrowserType.OPERA, BrowserType.OTHER]):
        """
        :param browser_type: Browser type, can be: CHROME, INTERNET_EXPLORER, FIREFOX, SAFARI, OPERA, OTHER

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
        """
        self.browser = browser_type
        self.instance = DataType.BROWSER.value
        super().__init__()

    def obtain_full_post_text_line(self) -> str:
        if self.browser < 0:
            raise KameleoonException("Browser not recognized")
        return f"eventType=staticData&browser={self.browser}&nonce={self.nonce}"


class PageView(Data):
    """Page view"""
    def __init__(self, url: str, title: str, referrer: Optional[int] = None):
        """
        :param url: Url of the page
        :type url: str
        :param title: Title of the page
        :type title: str
        :param referrer: Optional field - Referrer id
        :type referrer: Optional[int]

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
        """
        self.url = url
        self.title = title
        self.referrer = referrer
        self.instance = DataType.PAGE_VIEW.value
        super().__init__()

    def obtain_full_post_text_line(self) -> str:
        referrer_string = f"&referrers=[{self.referrer}]" if self.referrer else ""
        return f"eventType=page&href={self.encode(self.url)}&title={self.title}&keyPages=[]{referrer_string}&nonce={self.nonce}"    # noqa: E501


class Conversion(Data):
    """Conversion"""
    def __init__(self, goal_id: int, revenue: float = 0.0, negative: bool = False):
        """
        :param goal_id: Id of the goal associated to the conversion
        :type goal_id: int
        :param revenue: Optional field - Revenue associated to the conversion, defaults to 0.0
        :type revenue: float
        :param negative: Optional field - If the revenue is negative. By default it's positive, defaults to False
        :type negative: bool

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))

        """
        self.goal_id = goal_id
        self.revenue = revenue
        self.negative = negative
        self.instance = DataType.CONVERSION.value
        super().__init__()

    def obtain_full_post_text_line(self) -> str:
        return f"eventType=conversion&goalId={self.goal_id}&revenue={self.revenue}&negative={self.negative}&nonce={self.nonce}"  # noqa: E501


class Interest(Data):
    """Interest"""
    def __init__(self, index: int):
        """
        :param index: Index of the interest
        :type index: int

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Interest(1))
        """
        self.index = index
        self.instance = DataType.INTEREST.value
        super().__init__()

    def obtain_full_post_text_line(self) -> str:
        return f"eventType=interests&indexes=[{self.index}]&fresh=true&nonce={self.nonce}"
