from flask import Blueprint, render_template, redirect, url_for, flash,\
                  request
from weather.forms import WeatherForm, UpdateForm
from weather.models import CurrentModel, HistoryModel, DailyModel


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
                model_current = CurrentModel(session_id, location, unit)
                model_daily = DailyModel(session_id, location, unit)
                model_current.save()
                model_daily.save()
                basic = model_current.get_basic()
                daily = model_daily.get()

                if (basic and daily):
                    dt = model_current.process_basic(basic)
                    data = model_current.get_detail(basic.id)
                    detail = model_current.process_detail(data)
                    return render_template('weather.html', form=form, dt=dt,
                                           basic=basic, detail=detail,
                                           daily=daily.daily_list)
                else:
                    flash('Cannot find city:{}!'.format(location))
                    return render_template('index.html', form=form)
            else:
                return render_template('index.html', form=form)
        elif form.history.data:
            model_history = HistoryModel(session_id)
            history = model_history.get()
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
    if form.validate_on_submit():
        description = form.description.data
        model_current = CurrentModel(location)
        basic = model_current.get_basic()
        if basic:
            model_current.update_description(basic, description)
            basic = model_current.get_basic()
            dt = model_current.process_basic(basic)
            data = model_current.get_detail(basic.id)
            detail = model_current.process_detail(data)

            model_daily = DailyModel(location)
            daily = model_daily.get()
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
