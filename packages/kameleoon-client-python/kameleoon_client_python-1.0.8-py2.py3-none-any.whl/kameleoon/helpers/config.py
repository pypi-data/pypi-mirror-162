import os
from typing import Any, Dict, Optional

import yaml

from kameleoon.client_configuration import KameleoonClientConfiguration


def config(configuration_path: str="", configuration_object: Optional[KameleoonClientConfiguration]=None) -> Dict[str, Any]:
    from kameleoon.exceptions import ConfigurationNotFoundException

    """ This function reads the configuration file. """
    if not os.path.exists(configuration_path) and not configuration_object:
        raise ConfigurationNotFoundException("No config file {} or config object is found".format(configuration_path))
    config_ = {}
    if configuration_object:
        config_ = configuration_object.dict()
    else:
        with open(configuration_path, 'r') as yml_file:
            config_ = yaml.load(yml_file, Loader=yaml.SafeLoader)
    return config_