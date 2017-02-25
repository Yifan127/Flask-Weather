# Open Weather Map API
class OWP(object):
    OWM_CURRENT_API = 'http://api.openweathermap.org/data/2.5/weather'
    OWM_DAILY_API = 'http://api.openweathermap.org/data/2.5/forecast/daily'
    APPID = '3b18b44c5812ec5a52af7df8e840a43e'
    LANG = 'en'  # display language
    METRIC = 'metric'  # temperature unit c
    IMPERIAL = 'imperial'  # temperature unit f
    ICONURL = 'http://openweathermap.org/img/w/'
    TIMEOUT = 5


# Google Time Zone API
class GTZ(object):
    GOOGLE_TZ = 'https://maps.googleapis.com/maps/api/timezone/json'
    KEY = 'AIzaSyDvVwPR9NFb-KAwLifSXchnno-UjGPlfWo'  # API key
    LANGUAGE = 'en'  # display language
    TIMEOUT = 5
