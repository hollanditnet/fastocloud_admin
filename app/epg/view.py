import os
import gzip
import shutil

from flask_classy import FlaskView, route
from flask import render_template, request, jsonify
from flask_login import login_required

from app.common.epg.forms import EpgForm
from app.common.epg.entry import Epg
from app.common.utils.utils import download_file
from app import app, get_epg_tmp_folder


def gunzip(file_path, output_path):
    with gzip.open(file_path, "rb") as f_in, open(output_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)


# routes
class EpgView(FlaskView):
    route_base = '/epg/'

    @route('/update_urls', methods=['GET'])
    @login_required
    def update_urls(self):
        epgs = Epg.objects()
        epg_service_in_directory = app.config.get('EPG_IN_DIRECTORY')

        result = []
        for epg in epgs:
            path, name = download_file(epg.uri, get_epg_tmp_folder())
            out_path = os.path.expanduser(os.path.join(epg_service_in_directory, name))
            status = True
            if name.endswith(".gz"):
                try:
                    gunzip(path, out_path)
                except Exception:
                    status = False
            else:
                shutil.copy(path, out_path)

            os.unlink(path)
            result.append({'path': path, 'status': status})

        return jsonify(status='ok', result=result), 200

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
        epg = Epg.objects(id=sid).first()
        if epg:
            epg.delete()
            return jsonify(status='ok'), 200

        return jsonify(status='failed'), 404

    @login_required
    @route('/edit/<sid>', methods=['GET', 'POST'])
    def edit(self, sid):
        epg = Epg.objects(id=sid).first()
        form = EpgForm(obj=epg)

        if request.method == 'POST' and form.validate_on_submit():
            epg = form.update_entry(epg)
            epg.save()
            return jsonify(status='ok'), 200

        return render_template('epg/edit.html', form=form)
