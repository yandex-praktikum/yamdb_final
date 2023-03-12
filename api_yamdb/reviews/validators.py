from django.core.exceptions import ValidationError
from django.utils.timezone import now


def year_validator(value):
    if -5500 >= value > now().year:
        raise ValidationError(
            f'Год создания не должен быть больше {now().year} '
            f'и меньше года появления письменности (5500 год до н.э.)'
        )
