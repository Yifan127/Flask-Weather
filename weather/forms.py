from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, validators,\
                    ValidationError
from sqlalchemy import distinct
from weather import db
from weather.models import Description


class WeatherForm(FlaskForm):
    location = StringField(validators=[validators.Length(max=50)])
    unit = RadioField(choices=[('metric', '\u00b0C'), ('imperial', '\u00b0F')],
                      default='metric')
    search = SubmitField(label='Search')
    history = SubmitField(label='History')
    help = SubmitField(label='Help')
    wrong_data = SubmitField(label='Wrong Data?')


class ValidateDescription(object):
    def __init__(self, message=None):
        if not message:
            message = 'Description is not valid, please check help.'
        self.message = message

    def __call__(self, form, field):
        valid_weather = []
        for d in db.session.query(distinct(Description.description)).all():
            d = ''.join(d)
            valid_weather.append(d)

        if field.data.strip() not in valid_weather:
            raise ValidationError(self.message)


class UpdateForm(FlaskForm):
    description_validator = ValidateDescription()
    location = StringField(label='Location')
    description = StringField(label='Description',
                              validators=[validators.InputRequired(
                                          message='Description is required.'),
                                          validators.Length(max=50, message='\
                                          Description cannot be longer than 50\
                                          characters.'),
                                          description_validator])
    update = SubmitField(label='Update')
    back = SubmitField(label='Back')
