from django.core.exceptions import ValidationError
import re

LETTERS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-'
LETTERS += LETTERS.upper()


def validation_ru_letters(field):
    """Валидация на предмет использования только русских букв или тире"""
    for letter in field:
        if letter not in LETTERS:
            raise ValidationError(
                f'Необходимо использовать только русские буквы и тире')
    return field


def validation_phone(field):
    regex = (r'^((8\+7)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{1}'
             r'[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$')
    if re.match(regex, field) is None:
        raise ValidationError(
            f'Необходимо ввести номер телефона')
    return field
