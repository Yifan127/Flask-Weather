import json
from flask import Blueprint, make_response, request
from flask_restful import Resource, Api, fields, marshal_with, marshal
from weather.weather.models import CurrentBasic, CurrentDetail, Daily


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


# define marshallers
current_detail_fields = {
    'pressure': fields.Integer,
    'humidity': fields.Integer,
    'clouds': fields.Integer,
    'wind': {
        'wind_speed': fields.Integer,
        'wind_unit': fields.String,
        'wind_direction': fields.String
        },
    'sunrise': fields.DateTime,
    'sunset': fields.DateTime,
    'rain': fields.Integer,
    'snow': fields.Integer
}

current_fields = {
    'id':  fields.Integer,
    'location': fields.String,
    'description': fields.String,
    'temperature': fields.Integer,
    'temp_unit': fields.String,
    'dt': fields.DateTime,
    'detail': fields.Nested(current_detail_fields)
}

daily_list_fields = {
    'description': fields.String,
    'temp_min': fields.Integer,
    'temp_max': fields.Integer,
    'dt': fields.DateTime
}

daily_fields = {
    'id':  fields.Integer,
    'location': fields.String,
    'temp_unit': fields.String,
    'daily_list': fields.List(fields.Nested(daily_list_fields))
}


class Current(Resource):
    @marshal_with(current_fields)
    def get(self, location):
        '''get a location's current weather'''
        basic = CurrentBasic.query.filter_by(location=location).first_or_404()
        basic.detail = CurrentDetail.query.filter_by(basic_id=basic.id).first()
        return basic

    @marshal_with(current_fields)
    def put(self, location):
        '''update a location's weather description'''
        basic = CurrentBasic.query.filter_by(location=location).first_or_404()
        print('debug===========:{}'.format(type(basic)))
        CurrentBasic().update_description(basic, request.json['description'])
        return basic


class CurrentList(Resource):
    '''get a list of current weather'''
    def get(self):
        result = CurrentBasic.query.all()
        json_list = [marshal(r, current_fields) for r in result]
        return json_list


class DailyForecast(Resource):
    @marshal_with(daily_fields)
    def get(self, location):
        '''get a location's 7 days weather forecast'''
        daily = Daily.query.filter_by(location=location).first_or_404()
        return daily


api.add_resource(CurrentList, '/api/v1/current')
api.add_resource(Current, '/api/v1/current/<string:location>')
api.add_resource(DailyForecast, '/api/v1/daily/<string:location>')
