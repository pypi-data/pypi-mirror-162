import re

from p360_export.data.type.validate.ValidatorInterface import ValidatorInterface


class PhoneNumberValidator(ValidatorInterface):
    def __init__(self, min_phone_number_digit_count: int, max_phone_number_digit_count: int, phone_number_regex: str):
        self.__min_phone_number_digit_count = min_phone_number_digit_count
        self.__max_phone_number_digit_count = max_phone_number_digit_count
        self.__phone_number_regex = phone_number_regex

    def validate(self, value: str) -> bool:
        digit_count = sum(c.isdigit() for c in value)
        has_allowed_digit_count = self.__min_phone_number_digit_count < digit_count < self.__max_phone_number_digit_count

        return re.match(self.__phone_number_regex, value) is not None and has_allowed_digit_count
