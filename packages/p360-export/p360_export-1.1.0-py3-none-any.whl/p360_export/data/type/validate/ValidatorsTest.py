import unittest

from p360_export.data.type.validate.EmailValidator import EmailValidator
from p360_export.data.type.validate.PhoneNumberValidator import PhoneNumberValidator


class ValidatorsTest:
    def get_phone_number_validator(self):
        return PhoneNumberValidator(
            min_phone_number_digit_count=8,
            max_phone_number_digit_count=15,
            phone_number_regex=r"^(\(?\+?\d{1,3}\)?)([ .\/-]?\d{2,4}){3,4}$",
        )

    def test_valid_emails(self):
        email_validator = EmailValidator()

        valid_emails = ["a.b@email.com", "a2Bss@gmail.com", "a.b@seznam.cz"]

        for email in valid_emails:
            assert email_validator.validate(email)

    def test_invalid_emails(self):
        email_validator = EmailValidator()

        invalid_emails = ["email@email@email.com", "2131332131.com", ".@.com", ""]

        for email in invalid_emails:
            assert not email_validator.validate(email)

    def test_valid_phone_numbers(self):
        phone_number_validator = self.get_phone_number_validator()
        valid_phone_numbers = ["0933123123", "+421915915915", "(034)333 4445-555"]

        for phone_number in valid_phone_numbers:
            assert phone_number_validator.validate(phone_number)

    def test_invalid_phone_numbers(self):
        phone_number_validator = self.get_phone_number_validator()

        invalid_phone_numbers = ["12345678", "++3213213222", "(333)-111-d", ""]

        for phone_number in invalid_phone_numbers:
            assert not phone_number_validator.validate(phone_number)


if __name__ == "__main__":
    unittest.main()
