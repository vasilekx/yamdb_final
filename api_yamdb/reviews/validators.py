# reviews/validators.py

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


def validate_year(year):
    current_year = datetime.now().year
    if year > current_year:
        raise ValidationError(
            f'{year} год не может быть больше, чем {current_year}!'
        )


def validate_username(value):
    for regex, inverse_match in settings.USERNAME_REGEXES:
        RegexValidator(
            regex=regex,
            message=_(f'{value} - недопустимое имя пользователя.'),
            inverse_match=inverse_match
        )(value)
