import re


def locale_check(text: str) -> str:
    """
   Возвращает наименование языка на котором делается запрос
    """
    if re.match(r'[a-z]', text):
        return 'en'
    elif re.match(r'[а-я]', text):
        return 'ru'
