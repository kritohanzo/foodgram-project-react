import re
from typing import Union

from django.core.exceptions import ValidationError


def validate_username(value: str) -> Union[str, ValidationError]:
    """Функция-валидатор, проверяет,
    что пользователь корректно указал username.

    Подразумевается, что username может состоять
    только из букв латинского алфавита,
    цифр и нижнего подчёркивания.
    """
    if value.lower() == "me":
        raise ValidationError("Недопустимое имя пользователя!")
    regex = re.compile("[^a-zA-Z0-9_]+")
    if regex.search(value):
        raise ValidationError("Некорректные символы в username")
    return value
