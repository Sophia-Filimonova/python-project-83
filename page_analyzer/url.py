import validators


def validate_url(url):

    errors = []
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
