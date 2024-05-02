import re

from rest_framework.validators import ValidationError


def validate_username(value):
    """Валидация данных в поле username."""
    if value.lower() == 'me':
        raise ValidationError('Недопустимое имя для пользователя!'
                              'Выберите любое другое имя кроме "me".')

    if not re.match(r'^[\w.@+-]+\Z', value):
        raise ValidationError('Имя пользователя содержит запрещённые символы!'
                              'Допустимы: любые буквы(от "a" до "z" '
                              'и от "A" до "Z"), цифры от 0 до 9, а также '
                              'знаки: "_", ".", "@", "+", "-".')
