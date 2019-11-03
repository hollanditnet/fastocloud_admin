import os

from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from app.common.epg.forms import EpgForm
from app.common.epg.entry import Epg


# routes
class EpgView(FlaskView):
    route_base = '/epg/'

    @login_required
    @route('/add', methods=['GET', 'POST'])
    def add(self):
        form = EpgForm(obj=Epg())
        if request.method == 'POST' and form.validate_on_submit():
            new_entry = form.make_entry()
            new_entry.save()
            return jsonify(status='ok'), 200

        return render_template('epg/add.html', form=form)

    @login_required
    @route('/remove', methods=['POST'])
    def remove(self):
        sid = request.form['sid']
        server = Epg.objects(id=sid).first()
        if server:
            server.delete()
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        epg = Epg.objects(id=sid).first()
        form = EpgForm(obj=epg)

        if request.method == 'POST' and form.validate_on_submit():
            server = form.update_entry(epg)
            server.save()
            return jsonify(status='ok'), 200

        return render_template('epg/edit.html', form=form)
