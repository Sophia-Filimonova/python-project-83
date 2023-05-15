import validators
from typing import List


def validate_url(url: str) -> List[str]:

    errors = []
    if not (isinstance(url, str)):
        errors.append('Неверный тип данных аргумента')
        return errors

    if url == '':
        errors.append('Некорректный URL')
        errors.append('URL обязателен')
        return errors

    if not validators.url(url):
        errors.append('Некорректный URL')
        return errors

    if len(url) > 255:
        errors.append('URL превышает 255 символов')
        return errors

    return errors
