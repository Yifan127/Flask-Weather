from datetime import datetime, date, timedelta
import calendar
from sqlalchemy import and_
from weather import db, app
import weather.openweathermap as owm


class CurrentBasic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    temp_unit = db.Column(db.String(10), nullable=False)
    dt = db.Column(db.DateTime, nullable=False)
    amendment = db.Column(db.Boolean, nullable=False, default=False)
    last_update = db.Column(db.DateTime, nullable=False)
    detail = db.relationship('CurrentDetail', backref=db.backref('basic'),
                             uselist=False)

    def __init__(self, session_id, location, description, icon, temperature,
                 temp_unit, dt):
        self.session_id = session_id
        self.location = location
        self.description = description
        self.icon = icon
        self.temperature = temperature
        self.temp_unit = temp_unit
        self.dt = dt
        self.last_update = datetime.now()

    def __repr__(self):
        return '<CurrentBasic %r>' % self.location


class CurrentDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('current_basic.id'))

    pressure = db.Column(db.Integer, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    wind_direction = db.Column(db.String(10))
    wind_speed = db.Column(db.Integer, nullable=False)
    wind_unit = db.Column(db.String(10), nullable=False)
    clouds = db.Column(db.Integer, nullable=False)
    sunrise = db.Column(db.DateTime, nullable=False)
    sunset = db.Column(db.DateTime, nullable=False)
    rain = db.Column(db.Integer)
    snow = db.Column(db.Integer)
    last_update = db.Column(db.DateTime, nullable=False)

    def __init__(self, pressure, humidity, wind_direction, wind_speed,
                 wind_unit, clouds, sunrise, sunset, rain, snow, basic):
        self.pressure = pressure
        self.humidity = humidity
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.wind_unit = wind_unit
        self.clouds = clouds
        self.sunrise = sunrise
        self.sunset = sunset
        self.rain = rain
        self.snow = snow
        self.last_update = datetime.now()
        self.basic = basic

    def __repr__(self):
        return '<CurrentDetail %r>' % self.basic


class HistoryBasic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    temp_unit = db.Column(db.String(10), nullable=False)
    dt = db.Column(db.DateTime, nullable=False)
    amendment = db.Column(db.Boolean, nullable=False, default=False)
    last_update = db.Column(db.DateTime, nullable=False)
    detail = db.relationship('HistoryDetail', backref=db.backref('basic'),
                             uselist=False)

    def __init__(self, session_id, location, description, icon, temperature,
                 temp_unit, dt):
        self.session_id = session_id
        self.location = location
        self.description = description
        self.icon = icon
        self.temperature = temperature
        self.temp_unit = temp_unit
        self.dt = dt
        self.last_update = datetime.now()

    def __repr__(self):
        return '<HistoryBasic %r>' % self.location


class HistoryDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('history_basic.id'))

    pressure = db.Column(db.Integer, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    wind_direction = db.Column(db.String(10))
    wind_speed = db.Column(db.Integer, nullable=False)
    wind_unit = db.Column(db.String(10), nullable=False)
    clouds = db.Column(db.Integer, nullable=False)
    sunrise = db.Column(db.DateTime, nullable=False)
    sunset = db.Column(db.DateTime, nullable=False)
    rain = db.Column(db.Integer)
    snow = db.Column(db.Integer)
    last_update = db.Column(db.DateTime, nullable=False)

    def __init__(self, pressure, humidity, wind_direction, wind_speed,
                 wind_unit, clouds, sunrise, sunset, rain, snow, basic):
        self.pressure = pressure
        self.humidity = humidity
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.wind_unit = wind_unit
        self.clouds = clouds
        self.sunrise = sunrise
        self.sunset = sunset
        self.rain = rain
        self.snow = snow
        self.last_update = datetime.now()
        self.basic = basic

    def __repr__(self):
        return '<HistoryDetail %r>' % self.basic


class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    temp_unit = db.Column(db.String(10), nullable=False)
    daily_list = db.Column(db.PickleType, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    def __init__(self, session_id, location, temp_unit, daily_list):
        self.session_id = session_id
        self.location = location
        self.temp_unit = temp_unit
        self.daily_list = daily_list
        self.last_update = datetime.now()

    def __repr__(self):
        return '<Daily %r>' % self.location


class Description(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc_id = db.Column(db.Integer, nullable=False)
    group = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(50), nullable=False)

    def __init__(self, desc_id, group, description):
        self.desc_id = desc_id
        self.group = group
        self.description = description

    def __repr__(self):
        return '<Weather description %r>' % self.description


class BaseMode(object):
    def __init__(self, session_id):
        self.current = owm.CurrentWeather()
        self.session_id = session_id

    def process_basic(self, basic):
        ''' convert datetime to string format with weekday'''
        weekday = calendar.day_name[basic.dt.weekday()]
        dt = weekday + ' ' + basic.dt.strftime('%Y-%m-%d %H:%M:%S')
        return dt

    def process_detail(self, detail):
        '''return a dict with all detailed data with units'''
        weather = {}
        weather['Pressure'] = (detail.pressure, 'hPa')
        weather['Humidity'] = (detail.humidity, '%')
        weather['Wind Direction'] = (detail.wind_direction)
        weather['Wind Speed'] = (detail.wind_speed, detail.wind_unit)
        weather['Clouds'] = (detail.clouds, '%')
        weather['Sunrise'] = (detail.sunrise.strftime('%H:%M:%S'))
        weather['Sunset'] = (detail.sunset.strftime('%H:%M:%S'))
        weather['Rain'] = (detail.rain, 'mm')
        weather['Snow'] = (detail.snow, 'mm')
        return weather


class CurrentModel(BaseMode):
    def __init__(self, session_id, location, unit='metric'):
        super().__init__(session_id)
        self.location = location
        self.unit = unit

    def save(self):
        data = self.current.get_weather(self.location, self.unit)
        if isinstance(data, dict):
            current = self.current.organize_data(data)
            basic = self.get_basic()
            if basic:
                if basic.temp_unit != current['temp_unit']:
                    self.update(basic, current)
                if basic.last_update < datetime.now()-timedelta(minutes=5):
                    self.update(basic, current)
                elif basic.dt != current['datetime']:
                    self.update(basic, current)
            else:
                self.insert(current)

    def insert(self, current):
        app.logger.info('Begin to insert current weather:{}'
                        .format(current['location']))
        basic = CurrentBasic(self.session_id,
                             current['location'],
                             current['description'],
                             current['icon'],
                             current['temperature'],
                             current['temp_unit'],
                             current['datetime'])
        app.logger.debug('current basic weather:{}'.format(basic))

        detail = CurrentDetail(current['pressure'],
                               current['humidity'],
                               current['wind_direction'],
                               current['wind_speed'],
                               current['wind_unit'],
                               current['clouds'],
                               current['sunrise'],
                               current['sunset'],
                               current['rain'],
                               current['snow'],
                               basic)
        app.logger.debug('current detail weather:{}'.format(detail))

        db.session.add(basic)
        db.session.add(detail)
        db.session.commit()
        app.logger.info('End of insert current weather')

        model = HistoryModel(self.session_id)
        model.save(basic, detail)

    def update(self, basic, current):
        app.logger.info('Begin to update current weather:{}'
                        .format(basic.location))
        if (basic.amendment is False) or (basic.amendment is True and
                                          basic.dt.date() != date.today()):
            basic.description = current['description']
            basic.amendment = False
        basic.icon = current['icon']
        basic.temperature = current['temperature']
        basic.temp_unit = current['temp_unit']
        basic.dt = current['datetime']
        basic.last_update = datetime.now()
        app.logger.debug('current basic weather:{}'.format(basic))
        db.session.commit()

        detail = CurrentDetail.query.filter_by(basic_id=basic.id).first()
        if detail:
            detail.pressure = current['pressure']
            detail.humidity = current['humidity']
            detail.wind_direction = current['wind_direction']
            detail.wind_speed = current['wind_speed']
            detail.wind_unit = current['wind_unit']
            detail.clouds = current['clouds']
            detail.sunrise = current['sunrise']
            detail.sunset = current['sunset']
            detail.rain = current['rain']
            detail.snow = current['snow']
            detail.last_update = datetime.now()
            app.logger.debug('current detail weather:{}'.format(detail))
            db.session.commit()
        app.logger.info('End of update current weather')

        model = HistoryModel(self.session_id)
        model.save(basic, detail)

    def update_description(self, basic, description):
        app.logger.info('Begin to update {0} weather description:{1}'
                        .format(basic.location, description))
        basic.description = description
        basic.amendment = True
        basic.last_update = datetime.now()
        db.session.commit()
        app.logger.info('Begin to update weather description')

    def get_basic(self):
        app.logger.info('Begin to query current basic weather:{}'
                        .format(self.location))
        condition = and_(CurrentBasic.session_id == self.session_id,
                         CurrentBasic.location == self.location)
        basic = CurrentBasic.query.filter(condition).first()
        app.logger.debug('current basic weather:{}'.format(basic))
        app.logger.info('End of query current basic weather')
        return basic

    def get_detail(self, basic_id):
        detail = CurrentDetail.query.filter_by(basic_id=basic_id).first()
        return detail


class HistoryModel(BaseMode):
    def __init__(self, session_id):
        super().__init__(session_id)

    def save(self, basic, detail):
        condition = and_(HistoryBasic.session_id == basic.session_id,
                         HistoryBasic.location == basic.location,
                         HistoryBasic.temp_unit == basic.temp_unit,
                         HistoryBasic.dt == basic.dt)
        history = HistoryBasic.query.filter(condition).first()
        if not history:
            self.insert(basic, detail)

    def insert(self, basic, detail):
        app.logger.info('Begin to insert history:{}'.format(basic.location))
        history_basic = HistoryBasic(basic.session_id,
                                     basic.location,
                                     basic.description,
                                     basic.icon,
                                     basic.temperature,
                                     basic.temp_unit,
                                     basic.dt)
        app.logger.debug('history basic:{}'.format(history_basic))
        history_detail = HistoryDetail(detail.pressure,
                                       detail.humidity,
                                       detail.wind_direction,
                                       detail.wind_speed,
                                       detail.wind_unit,
                                       detail.clouds,
                                       detail.sunrise,
                                       detail.sunset,
                                       detail.rain,
                                       detail.snow,
                                       history_basic)
        app.logger.debug('history detail:{}'.format(history_detail))
        db.session.add(history_basic)
        db.session.add(history_detail)
        db.session.commit()
        app.logger.info('End of insert history')

    def get(self):
        app.logger.info('Begin to query history of user:{}'
                        .format(self.session_id))
        history_basic = HistoryBasic.query.filter_by(
                        session_id=self.session_id).all()
        history = self.process_history(history_basic)
        app.logger.debug('history: {}'.format(history))
        app.logger.info('End of query history')
        return history

    def process_history(self, history_basic):
        history = []
        if history_basic:
            for basic in history_basic:
                detail = HistoryDetail.query.filter_by(
                                       basic_id=basic.id).first()
                if detail:
                    record = {'basic': basic, 'detail': detail}
                    dt = self.process_basic(basic)
                    detail = self.process_detail(detail)
                    record = {'dt': dt, 'basic': basic, 'detail': detail}
                    history.append(record)
        return history


class DailyModel(object):
    def __init__(self, session_id, location, unit='metric'):
        self.daily = owm.DailyWeather()
        self.session_id = session_id
        self.location = location
        self.unit = unit

    def save(self):
        data = self.daily.get_weather(self.location, self.unit, 7)
        if isinstance(data, dict):
            daily = self.daily.organize_data(data)
            record = self.get()
            if record:
                if record.temp_unit != daily['temp_unit']:
                    self.update(record, daily)
                if record.last_update < datetime.now()-timedelta(minutes=5):
                    self.update(record, daily)
                elif record.daily_list[0]['dt'] != daily['list'][0]['dt']:
                    self.update(record, daily)
            else:
                self.insert(daily)
        else:
            return data

    def insert(self, daily):
        app.logger.info('Begin to insert daily weather:{}'
                        .format(daily['location']))
        weather_daily = Daily(self.session_id, daily['location'],
                              daily['temp_unit'], daily['list'])

        db.session.add(weather_daily)
        app.logger.debug('daily weather: {}'.format(weather_daily))
        db.session.commit()
        app.logger.info('End of insert daily weather')

    def update(self, daily_record, daily):
        app.logger.info('Begin to update daily weather:{}'
                        .format(daily_record.location))
        daily_record.temp_unit = daily['temp_unit']
        daily_record.daily_list = daily['list']
        daily_record.last_update = datetime.now()
        db.session.commit()
        app.logger.info('Begin to update daily weather')

    def get(self):
        condition = and_(Daily.session_id == self.session_id,
                         Daily.location == self.location)
        daily = Daily.query.filter(condition).first()
        return daily
