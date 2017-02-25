import requests
from .constant import GTZ


class TZ():
    def __init__(self):
        self.api = GTZ.GOOGLE_TZ
        self.language = GTZ.LANGUAGE
        self.key = GTZ.KEY
        self.timeout = GTZ.TIMEOUT

    def get_location_timestamp(self, timestamp, location):
        '''get current weather data from open weather map API,
        return the response data'''
        error = None
        params = {'location': location, 'timestamp': timestamp,
                  'language': self.language, 'key': self.key}
        try:
            r = requests.get(self.api, params=params, timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                data = r.json()
                dstOffset = data['dstOffset']
                rawOffset = data['rawOffset']
                location_timestamp = timestamp + dstOffset + rawOffset
                return location_timestamp
            else:
                error = 'Fail to access Google Time Zone API!'
                print(error)
        except (requests.Timeout, requests.ConnectionError):
            error = 'Network problem or OpenWeatherMap API connection timeout!'
            print(error)
