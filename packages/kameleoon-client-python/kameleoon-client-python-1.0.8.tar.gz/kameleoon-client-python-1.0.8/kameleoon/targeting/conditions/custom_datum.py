import re
from typing import Any, Union, Dict

from kameleoon.exceptions import NotFoundError, KameleoonException
from kameleoon.targeting.condition import Condition
from kameleoon.targeting.models import ConditionType, DataType, Operator

__all__ = ["CustomDatum", ]


class CustomDatum(Condition):
    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        if 'customDataIndex' not in json_condition or json_condition['customDataIndex'] is None:
            raise NotFoundError('customDataIndex')
        self.index = json_condition['customDataIndex']
        if 'valueMatchType' not in json_condition or json_condition['valueMatchType'] is None:
            raise NotFoundError('valueMatchType')
        self.operator = json_condition['valueMatchType']
        if 'value' in json_condition and json_condition['value'] is not None:
            self.value = json_condition['value']
        self.type_ = ConditionType["CUSTOM_DATUM"]
        if ('include' not in json_condition or json_condition['include'] is None) and ('isInclude' not in json_condition or json_condition['isInclude'] is None):
            raise NotFoundError('include / isInclude missed')
        self.include = json_condition['include'] if 'include' in json_condition else json_condition['isInclude']

    def check(self, datas) -> bool:
        is_targeted = False
        try:
            custom_data = [x for x in datas if x.instance == DataType["CUSTOM"] and x.id == self.index][-1]
        except IndexError:
            custom_data = None
        if not custom_data:
            is_targeted = self.operator == Operator["UNDEFINED"]
        else:
            if self.operator == Operator["MATCH"]:
                if re.match(self.value, custom_data.value):
                    is_targeted = True
            elif self.operator == Operator["CONTAINS"]:
                if self.value in custom_data.value:
                    is_targeted = True
            elif self.operator == Operator["EXACT"]:
                if self.value == custom_data.value:
                    is_targeted = True
            elif self.operator == Operator["EQUAL"]:
                if float(self.value) == float(custom_data.value):
                    is_targeted = True
            elif self.operator == Operator["GREATER"]:
                try:
                    if float(custom_data.value) > float(self.value):
                        is_targeted = True
                except ValueError:
                    pass
            elif self.operator == Operator["LOWER"]:
                if float(custom_data.value) < float(self.value):
                    is_targeted = True
            elif self.operator == Operator["IS_TRUE"]:
                if custom_data.value == 'true':
                    is_targeted = True
            elif self.operator == Operator["IS_FALSE"]:
                if custom_data.value == 'false':
                    is_targeted = True
            else:
                raise KameleoonException(f"Undefined operator {self.operator}")

        return is_targeted
