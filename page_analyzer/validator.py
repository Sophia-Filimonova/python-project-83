import validators
from urllib.parse import urlparse


def validate_url(url):

    errors = []
    if url == '':
        errors.append(('Некорректный URL', 'alert alert-danger'))
        errors.append(('URL обязателен', 'alert alert-danger'))
        return errors

    if validators.url(url):
        o = urlparse(url)
        normalized_url = o.scheme + '://' + o.hostname
    else:
        errors.append(('Некорректный URL', 'alert alert-danger'))
        return errors

    if len(normalized_url) > 255:
        errors.append(('URL превышает 255 символов', 'alert alert-danger'))
        return errors

    return errors
