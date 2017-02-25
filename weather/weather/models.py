import os
import json
import calendar
from datetime import datetime, date
from sqlalchemy import and_
from .. import db, app
from . import openweathermap as owm


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

    def __repr__(self):
        return '<CurrentBasic %r>' % self.location

    def save(self, session_id, location, unit='metric'):
        app.logger.debug('location is {}'.format(location))
        current = owm.CurrentWeather()
        data = current.get(location, unit)
        app.logger.debug('Data is {}'.format(data))
        if data:
            current = current.organize_data(data)
            basic = self.get(session_id, location)
            if basic:
                if (basic.dt != current['datetime']) or \
                   (basic.temp_unit != current['temp_unit']):
                    self.update(basic, current)
            else:
                self.insert(current, session_id)

    def insert(self, current, session_id):
        app.logger.info('Begin to insert current weather:{}'
                        .format(current['location']))
        basic = CurrentBasic(session_id=session_id,
                             location=current['location'],
                             description=current['description'],
                             icon=current['icon'],
                             temperature=current['temperature'],
                             temp_unit=current['temp_unit'],
                             dt=current['datetime'],
                             last_update=datetime.now())
        app.logger.debug('current basic weather:{}'.format(basic))

        db.session.add(basic)
        db.session.commit()
        CurrentDetail().insert(basic, current)

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
        CurrentDetail().update(basic, current)

    def update_description(self, basic, description):
        app.logger.info('Begin to update {0} weather description:{1}'
                        .format(basic.location, description))
        basic.description = description
        basic.amendment = True
        basic.last_update = datetime.now()
        db.session.commit()
        app.logger.info('End of update weather description')
        detail = CurrentDetail().get(basic.id)
        HistoryBasic().save(basic, detail)

    def get_same_unit(self, session_id, location, unit):
        app.logger.info('Begin to query current basic weather:{}'
                        .format(location))
        condition = and_(CurrentBasic.session_id == session_id,
                         CurrentBasic.location == location,
                         CurrentBasic.temp_unit == unit)
        basic = CurrentBasic.query.filter(condition).first()
        app.logger.debug('current basic weather:{}'.format(basic))
        app.logger.info('End of query current basic weather')
        return basic

    def get(self, session_id, location):
        app.logger.info('Begin to query current basic weather:{}'
                        .format(location))
        condition = and_(CurrentBasic.session_id == session_id,
                         CurrentBasic.location == location)
        basic = CurrentBasic.query.filter(condition).first()
        app.logger.debug('current basic weather:{}'.format(basic))
        app.logger.info('End of query current basic weather')
        return basic


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

    def __repr__(self):
        return '<CurrentDetail %r>' % self.basic

    def insert(self, basic, current):
        detail = CurrentDetail(pressure=current['pressure'],
                               humidity=current['humidity'],
                               wind_direction=current['wind_direction'],
                               wind_speed=current['wind_speed'],
                               wind_unit=current['wind_unit'],
                               clouds=current['clouds'],
                               sunrise=current['sunrise'],
                               sunset=current['sunset'],
                               rain=current['rain'],
                               snow=current['snow'],
                               last_update=datetime.now(),
                               basic=basic)
        app.logger.debug('current detail weather:{}'.format(detail))

        db.session.add(detail)
        db.session.commit()
        app.logger.info('End of insert current weather')
        HistoryBasic().save(basic, detail)

    def update(self, basic, current):
        detail = self.get(basic.id)
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
        HistoryBasic().save(basic, detail)

    def get(self, basic_id):
        detail = CurrentDetail.query.filter_by(basic_id=basic_id).first()
        return detail


class HistoryBasic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    temperature = db.Column(db.Integer, nullable=False)
    temp_unit = db.Column(db.String(10), nullable=False)
    dt = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    detail = db.relationship('HistoryDetail', backref=db.backref('basic'),
                             uselist=False)

    def __repr__(self):
        return '<HistoryBasic %r>' % self.location

    def save(self, basic, detail):
        condition = and_(HistoryBasic.session_id == basic.session_id,
                         HistoryBasic.location == basic.location,
                         HistoryBasic.temp_unit == basic.temp_unit,
                         HistoryBasic.dt == basic.dt,
                         HistoryBasic.description == basic.description)
        history = HistoryBasic.query.filter(condition).first()
        if not history:
            self.insert(basic, detail)

    def insert(self, basic, detail):
        app.logger.info('Begin to insert history:{}'.format(basic.location))
        history_basic = HistoryBasic(session_id=basic.session_id,
                                     location=basic.location,
                                     description=basic.description,
                                     icon=basic.icon,
                                     temperature=basic.temperature,
                                     temp_unit=basic.temp_unit,
                                     dt=basic.dt,
                                     last_update=datetime.now())
        app.logger.debug('history basic:{}'.format(history_basic))
        db.session.add(history_basic)
        db.session.commit()
        HistoryDetail().insert(history_basic, detail)

    def get(self, session_id):
        app.logger.info('Begin to query history of user:{}'.format(session_id))
        history_basic = HistoryBasic.query.filter_by(
                                     session_id=session_id).all()
        app.logger.debug('history: {}'.format(history_basic))
        app.logger.info('End of query history')
        return history_basic


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

    def __repr__(self):
        return '<HistoryDetail %r>' % self.basic

    def insert(self, history_basic, detail):
        history_detail = HistoryDetail(pressure=detail.pressure,
                                       humidity=detail.humidity,
                                       wind_direction=detail.wind_direction,
                                       wind_speed=detail.wind_speed,
                                       wind_unit=detail.wind_unit,
                                       clouds=detail.clouds,
                                       sunrise=detail.sunrise,
                                       sunset=detail.sunset,
                                       rain=detail.rain,
                                       snow=detail.snow,
                                       last_update=datetime.now(),
                                       basic=history_basic)
        app.logger.debug('history detail:{}'.format(history_detail))
        db.session.add(history_detail)
        db.session.commit()
        app.logger.info('End of insert history')


class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    temp_unit = db.Column(db.String(10), nullable=False)
    daily_list = db.Column(db.PickleType, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Daily %r>' % self.location

    def save(self, session_id, location, unit='metric'):
        daily = owm.DailyWeather()
        data = daily.get(location, unit, 7)
        if data:
            daily = daily.organize_data(data)
            record = self.get(session_id, location)
            if record:
                if (record.daily_list[0]['dt'] != daily['list'][0]['dt']) or \
                   (record.temp_unit != daily['temp_unit']):
                    self.update(record, daily)
            else:
                self.insert(daily, session_id)

    def insert(self, daily, session_id):
        app.logger.info('Begin to insert daily weather:{}'
                        .format(daily['location']))
        weather_daily = Daily(session_id=session_id,
                              location=daily['location'],
                              temp_unit=daily['temp_unit'],
                              daily_list=daily['list'],
                              last_update=datetime.now())

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

    def get_same_unit(self, session_id, location, unit):
        app.logger.info('Begin to query daily weather:{}'.format(location))
        condition = and_(Daily.session_id == session_id,
                         Daily.location == location,
                         Daily.temp_unit == unit)
        daily = Daily.query.filter(condition).first()
        app.logger.info('End of query daily weather:{}'.format(daily))
        return daily

    def get(self, session_id, location):
        app.logger.info('Begin to query daily weather:{}'.format(location))
        condition = and_(Daily.session_id == session_id,
                         Daily.location == location)
        daily = Daily.query.filter(condition).first()
        app.logger.info('End of query daily weather:{}'.format(daily))
        return daily


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

    def load_description():
        filepath = os.path.join(app.root_path, 'description.json')
        with open(filepath, encoding='utf-8') as file:
            text = file.readlines()
            for line in text:
                data = json.loads(line)
                record = Description(data['desc_id'], data['group'],
                                     data['description'])
                db.session.add(record)
                db.session.commit()


class ModelHelper(object):
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
