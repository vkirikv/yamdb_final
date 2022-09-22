from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(year):
    """Валидатор для контроля значения года.

    Вводимое значение не должно превышать значение текущего года.

    """
    current_year = timezone.now().year
    if year > current_year:
        raise ValidationError(
            f'Значение года не может превышать {current_year}'
        )
