import re

from p360_export.data.type.validate.ValidatorInterface import ValidatorInterface


class EmailValidator(ValidatorInterface):
    def __init__(self) -> None:
        self.__email_regex = r"[^@]+@[^@]+\.[^@]+$"

    def validate(self, value: str) -> bool:
        return re.match(self.__email_regex, value) is not None
