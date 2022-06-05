from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
ADMINS = env.list('ADMINS')
API_KEY = env.str('Key')
API_HOST = 'hotels4.p.rapidapi.com'
BASE_URL = 'https://hotels4.p.rapidapi.com'

headers = {
    'x-rapidapi-host': API_HOST,
    'x-rapidapi-key': API_KEY
}

locales = {
    'en': {
        'locale': 'en_US',
        'currency': 'USD'
    },
    'ru': {
        'locale': 'ru_RU',
        'currency': 'RUR'
    }
}

MAX_HOTELS_TO_SHOW = 15
MAX_PHOTO_TO_SHOW = 10
