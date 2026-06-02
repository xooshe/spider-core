from django.core import validators
from django.utils.deconstruct import deconstructible


@deconstructible
class LocalPhoneNumberValidator(validators.RegexValidator):
    regex = r"^\d{9,12}$"
    message = "enter a valid phone number."
