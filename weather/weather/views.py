from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from .forms import WeatherForm, UpdateForm
from .models import CurrentBasic, CurrentDetail, HistoryBasic,\
                                   Daily, ModelHelper


weather = Blueprint('weather', __name__)


@weather.route('/', methods=['POST', 'GET'])
def index():
    form = WeatherForm()
    session_id = request.cookies.get('session')
    if form.validate_on_submit():
        location = form.location.data.lower().strip()
        unit = form.unit.data
        if form.search.data:
            if location:
                model_basic = CurrentBasic()
                model_detail = CurrentDetail()
                model_daily = Daily()
                basic = model_basic.get_same_unit(session_id, location, unit)
                daily = model_daily.get_same_unit(session_id, location, unit)
                if (basic and daily):
                    if basic.last_update > datetime.now()-timedelta(minutes=5):
                        dt = ModelHelper().process_basic(basic)
                        data = model_detail.get(basic.id)
                        detail = ModelHelper().process_detail(data)
                        return render_template('weather.html', form=form,
                                               dt=dt, basic=basic,
                                               detail=detail,
                                               daily=daily.daily_list)

                model_basic.save(session_id, location, unit)
                model_daily.save(session_id, location, unit)
                basic = model_basic.get(session_id, location)
                daily = model_daily.get(session_id, location)

                if (basic and daily):
                    dt = ModelHelper().process_basic(basic)
                    data = model_detail.get(basic.id)
                    detail = ModelHelper().process_detail(data)
                    return render_template('weather.html', form=form,
                                           dt=dt, basic=basic,
                                           detail=detail,
                                           daily=daily.daily_list)
                else:
                    flash('Cannot find city:{}!'.format(location))
                    return render_template('index.html', form=form)
            else:
                return render_template('index.html', form=form)
        elif form.history.data:
            model_history = HistoryBasic()
            history_basic = model_history.get(session_id)
            history = ModelHelper().process_history(history_basic)
            if history:
                return render_template('history.html', form=form,
                                       history=history)
            else:
                flash('No history record found!')
                return render_template('index.html', form=form)
        elif form.help.data:
            with open('README.md', encoding="utf-8") as file:
                text = file.readlines()
            return render_template('help.html', form=form, help=text)
        elif form.wrong_data.data:
            if location:
                return redirect(url_for('weather.update', location=location))
            else:
                flash('Please enter a location!')
                return render_template('index.html', form=form)
    else:
        return render_template('index.html', form=form)


@weather.route('/update/<location>', methods=['POST', 'GET'])
def update(location):
    form = UpdateForm()
    form.location.data = location
    session_id = request.cookies.get('session')
    if form.validate_on_submit():
        description = form.description.data
        model_basic = CurrentBasic()
        model_detail = CurrentDetail()
        model_daily = Daily()
        basic = model_basic.get(session_id, location)
        if basic:
            model_basic.update_description(basic, description)
            basic = model_basic.get(session_id, location)
            dt = ModelHelper().process_basic(basic)
            data = model_detail.get(basic.id)
            detail = ModelHelper().process_detail(data)
            daily = model_daily.get(session_id, location)
            flash('The weather is successfully updated.')
            return render_template('update.html', form=form, dt=dt,
                                   basic=basic, detail=detail,
                                   daily=daily.daily_list, alert=False)
        else:
            flash('Can not find the location in your search history.\
                   Please go back to index page, search the location \
                   first, then update if the data are wrong!')
            return render_template('update.html', form=form, alert=True)
    else:
        submit = request.args.get('back', '')
        if submit == 'Back':
            return redirect(url_for('weather.index'))
        return render_template('update.html', form=form)
