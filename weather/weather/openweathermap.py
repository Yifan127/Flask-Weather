import requests
from datetime import datetime
import time
import calendar
from .. import app
from .constant import OWP
from .googletz import TZ


class OpenWeatherMap(object):
    def __init__(self, api):
        self.api = api
        self.lang = OWP.LANG
        self.appid = OWP.APPID
        self.timeout = OWP.TIMEOUT

    def get_request(self, params):
        '''get current weather data from open weather map API,
        return the response data'''
        data = {}
        error = None
        try:
            r = requests.get(self.api, params=params, timeout=self.timeout)
            if r.status_code == requests.codes.ok:
                data = r.json()
                return data
            else:
                error = 'Cannot access OpenWeatherMap API!'
                print(error)
        except (requests.Timeout, requests.ConnectionError):
            error = 'Network problem Or Timeout!'
            print(error)

    def set_units(self, unit):
        '''set unit of measure when print weather information'''
        units = {}
        if unit == OWP.IMPERIAL:
            wind_unit = 'miles/hour'
        elif unit == OWP.METRIC:
            wind_unit = 'meter/sec'

        units['temperature'] = unit
        units['wind'] = wind_unit
        units['pressure'] = 'hPa'
        units['percentage'] = '%'
        units['fall'] = 'millimetres'

        return units

    def deg_to_direction(self, deg):
        '''convert wind degree to compass direction'''
        direction = ['N', 'NNE', 'NE', 'ENE',
                     'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW',
                     'W', 'WNW', 'NW', 'NNW']
        value = int((deg / 22.5) + 0.5)
        return direction[value % 16]

    def get_location_ts(self, coord, timestamp):
        '''calculate location local datetime'''
        location = '{:f}, {:f}'.format(coord['lat'], coord['lon'])
        utc_timestamp = timestamp + time.altzone

        tz = TZ()
        location_timestamp = tz.get_location_timestamp(utc_timestamp, location)
        if location_timestamp:
            return location_timestamp
        else:
            return timestamp


class CurrentWeather(OpenWeatherMap):
    def __init__(self):
        super().__init__(OWP.OWM_CURRENT_API)

    def get(self, location, unit):
        '''This function send a request to get current weather information,
        then prints the data'''
        params = {'q': location, 'units': unit,
                  'lang': self.lang, 'appid': self.appid}
        app.logger.debug('Params is {}'.format(params))
        data = self.get_request(params)
        app.logger.debug('Data from OpenWeatherMap is {}'.format(data))
        if data:
            if location == data['name'].lower().strip():
                data['unit'] = params['units']
                return data
            else:
                error = 'Cannot find city: {0}!'.format(location)
                app.logger.debug(error)
        else:
            app.logger.debug('Failed to access OpenWeatherMap!')

    def organize_data(self, data):
        weather = {}
        if data:
            units = self.set_units(data['unit'])
            main = data['main']
            sys = data['sys']
            wind = data['wind']

            weather['location'] = data['name'].lower().strip()
            weather['description'] = data['weather'][0]['description']
            weather['icon'] = data['weather'][0]['icon']

            weather['temperature'] = round(data['main']['temp'])
            weather['temp_unit'] = units['temperature']
            timestamp = self.get_location_ts(data['coord'], data['dt'])
            weather['datetime'] = datetime.fromtimestamp(timestamp)

            weather['pressure'] = int(main['pressure'])
            weather['humidity'] = main['humidity']

            if 'deg' in data['wind']:
                weather['wind_direction'] = self.deg_to_direction(wind['deg'])
            else:
                weather['wind_direction'] = ''

            weather['wind_unit'] = units['wind']
            weather['wind_speed'] = round(wind['speed'])
            weather['clouds'] = data['clouds']['all']

            sunrise = self.get_location_ts(data['coord'], sys['sunrise'])
            sunset = self.get_location_ts(data['coord'], sys['sunset'])
            weather['sunrise'] = datetime.fromtimestamp(sunrise)
            weather['sunset'] = datetime.fromtimestamp(sunset)

            if 'rain' in data:
                weather['rain'] = round(data['rain']['3h'])
            else:
                weather['rain'] = 0

            if 'snow' in data:
                weather['snow'] = round(data['snow']['3h'])
            else:
                weather['snow'] = 0

        return weather


class DailyWeather(OpenWeatherMap):
    def __init__(self):
        super().__init__(OWP.OWM_DAILY_API)

    def get(self, location, unit, cnt=7):
        '''This function sends a request to get daily forecast weather information,
        then prints the data'''
        params = {'q': location, 'units': unit, 'cnt': cnt,
                  'lang': self.lang, 'appid': self.appid}
        data = self.get_request(params)
        if data:
            if location == data['city']['name'].lower().strip():
                data['unit'] = params['units']
                return data
            else:
                error = 'Cannot find city: {0}!'.format(location)
                app.logger.debug(error)
        else:
            app.logger.debug('Failed to access OpenWeatherMap!')

    def organize_data(self, data):
        weather = {}
        if data:
            weather['location'] = data['city']['name'].lower().strip()
            units = self.set_units(data['unit'])
            weather['temp_unit'] = units['temperature']
            weather['list'] = []

            if 'list' in data:
                daily = data['list']
            elif 'List' in data:
                daily = data['List']

            coord = data['city']['coord']
            for day in daily:
                ts = self.get_location_ts(coord, day['dt'])
                dt = datetime.fromtimestamp(ts)
                weekday = calendar.day_abbr[dt.weekday()]
                data = {'dt': dt, 'weekday': weekday,
                        'description': day['weather'][0]['description'],
                        'icon': day['weather'][0]['icon'],
                        'temp_min': round(day['temp']['min']),
                        'temp_max': round(day['temp']['max'])}
                weather['list'].append(data)

        return weather
