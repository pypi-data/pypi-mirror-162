"""Kameleoon Client Configuration"""

from typing import Any, Dict, Optional


class KameleoonClientConfiguration:
    """Client configuration which can be used instead of external configuration file"""

    # pylint: disable=R0913
    def __init__(self,
                 client_id: str = "",
                 client_secret: str = "",
                 actions_configuration_refresh_interval: int = 60,
                 default_timeout: int = 2000,
                 visitor_data_maximum_size: int = 500,
                 environment: Optional[str] = None,
                 multi_threading: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.actions_configuration_refresh_interval = actions_configuration_refresh_interval
        self.default_timeout = default_timeout
        self.visitor_data_maximum_size = visitor_data_maximum_size
        self.environment = environment
        self.multi_threading = multi_threading

    def dict(self) -> Dict[str, Any]:
        """convert object to dict"""
        return dict(vars(self))
