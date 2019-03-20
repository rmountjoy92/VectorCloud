#!/usr/bin/env python3

from os.path import dirname, join, realpath
from flask import render_template, url_for, redirect, Blueprint, flash,\
    request, send_file
from vectorcloud import db
from vectorcloud.models import Status, ApplicationStore, Application, Settings
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.main.forms import SearchForm
from vectorcloud.application_store.forms import UploadPackage
from vectorcloud.application_store.utils import install_package,\
    export_package, clear_temp_folder

application_store = Blueprint('application_store', __name__)

curr_folder = dirname(realpath(__file__))
app_store_folder = join(curr_folder, 'application_store')
packages_folder = join(app_store_folder, 'packages')


@application_store.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
    clear_temp_folder()
    return response


@application_store.route("/app_store", methods=['GET', 'POST'])
def app_store():
    search_term = None
    num_results = 0
    clear_temp_folder()
    store_app_list = ApplicationStore.query.order_by(ApplicationStore.author)
    main_app_list = Application.query.all()

    for store_app in store_app_list:
        for main_app in main_app_list:
            if store_app.script_name.lower() == main_app.script_name.lower():
                store_app.installed = True
                db.session.merge(store_app)
                db.session.commit()

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()

    search_form = SearchForm()
    install_form = UploadPackage()
    settings = Settings.query.first()

    if search_form.go.data:
        settings.search_by_name = search_form.by_name.data
        settings.search_by_description = search_form.by_description.data
        settings.search_by_author = search_form.by_author.data
        db.session.merge(settings)
        db.session.commit()
        search_term = search_form.search.data
        apps_searched = []

        if search_form.by_name.data is True:
            for application in store_app_list:
                if search_term.lower() in application.script_name.lower():
                    apps_searched.append(application.script_name)

        if search_form.by_description.data is True:
            for application in store_app_list:
                if search_term.lower() in application.description.lower():
                    apps_searched.append(application.script_name)

        if search_form.by_author.data is True:
            for application in store_app_list:
                if search_term.lower() in application.author.lower():
                    apps_searched.append(application.script_name)

        store_app_list = ApplicationStore.query.filter(
            ApplicationStore.script_name.in_(apps_searched))
        apps_searched = set(apps_searched)
        num_results = len(apps_searched)

    if install_form.install.data:
        if install_form.package.data:
            install_package(install_form.package.data)

        else:
            flash('No Package Uploaded!', 'warning')
        return redirect(url_for('application_store.app_store'))

    if request.method == 'GET':
        search_form.by_name.data = settings.search_by_name
        search_form.by_description.data = settings.search_by_description
        search_form.by_author.data = settings.search_by_author

    return render_template('applications/app_store.html',
                           title='App Store',
                           vector_status=vector_status,
                           sdk_version=sdk_version,
                           app_list=store_app_list,
                           search_form=search_form,
                           search_term=search_term,
                           num_results=num_results,
                           install_form=install_form)


@application_store.route("/install_store_application/<script_id>",
                         methods=['GET', 'POST'])
def install_store_application(script_id):
    store_app = ApplicationStore.query.filter_by(id=script_id).first()
    applications = Application.query.all()

    if applications:
        for application in applications:
            if application.script_name.lower() == \
                    store_app.script_name.lower():
                flash('Application named "' + application.script_name +
                      '" already exists, please rename the existing \
                      application and try again.', 'warning')
                return redirect(url_for('application_store.app_store'))

    install_package(form_package=None,
                    store_package=store_app.zip_file,
                    override_output=True)
    store_app.installed = True
    db.session.merge(store_app)
    db.session.commit()
    flash(store_app.script_name + ' installed!', 'success')
    return redirect(url_for('application_store.app_store'))


@application_store.route("/export_application/<script_id>",
                         methods=['GET', 'POST'])
def export_application(script_id):
    zip_fn = export_package(script_id)
    return send_file(zip_fn)
    return redirect(url_for('main.home'))
