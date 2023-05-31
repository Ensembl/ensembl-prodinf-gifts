#!/usr/bin/env python
# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import os
import requests
from flask import Flask, json, jsonify, redirect, render_template, request, url_for
from json.decoder import JSONDecodeError
from flask_bootstrap import Bootstrap4
from flask_cors import CORS
from flasgger import Swagger
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

from ensembl.production.gifts.config import GIFTsConfig
from ensembl.production.gifts.forms import GIFTsSubmissionForm
from ensembl.production.core.models.hive import HiveInstance

app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(app_path, 'static')
template_path = os.path.join(app_path, 'templates')

app = Flask(__name__, static_url_path='/static', static_folder=static_path, template_folder=template_path)

app.config.from_object(GIFTsConfig)

Bootstrap4(app)

CORS(app)

Swagger(app, template_file='swagger.yml')

@app.context_processor
def inject_configs():
    return dict(script_name=GIFTsConfig.SCRIPT_NAME)

if app.env == 'development':
    # ENV dev (assumed run from builtin server, so update script_name at wsgi level)
    app.wsgi_app = DispatcherMiddleware(
        Response('Not Found', status=404),
        {GIFTsConfig.SCRIPT_NAME: app.wsgi_app}
    )

def get_gifts_api_uri(environment):
    with open(app.config["GIFTS_API_URIS_FILE"], 'r') as f:
        gifts_api_uris = json.loads(f.read())
        if environment in gifts_api_uris.keys():
            gifts_api_uri = gifts_api_uris[environment]
        else:
            raise RuntimeError('Unrecognised Environment: %s' % environment)
    return gifts_api_uri


def get_status(rest_server):
    status_uri = rest_server + '/service/status'

    try:
        status_response = requests.get(status_uri)
    except requests.ConnectionError as e:
        return f'Unable to retrieve status from GIFTs service {e}'
    try:
        pipeline_status = json.loads(status_response.text)
    except JSONDecodeError as e:
        return f'Error loading GIFTs service information {e}'

    for status, running in pipeline_status.items():
        if running:
            return status.replace('_', ' ').capitalize()

    return None


def get_hive(hive_type):
    if hive_type == 'update_ensembl':
        if app.config["HIVE_UPDATE_ENSEMBL_URI"] is None:
            raise RuntimeError('Undefined environment variable: HIVE_UPDATE_ENSEMBL_URI')
        else:
            hive = HiveInstance(app.config["HIVE_UPDATE_ENSEMBL_URI"])
    elif hive_type == 'process_mapping':
        if app.config["HIVE_PROCESS_MAPPING_URI"] is None:
            raise RuntimeError('Undefined environment variable: HIVE_PROCESS_MAPPING_URI')
        else:
            hive = HiveInstance(app.config["HIVE_PROCESS_MAPPING_URI"])
    else:
        raise RuntimeError('Unrecognised Pipeline: %s' % hive_type)
    return hive


def submit_job(payload, analysis, action):
    rest_server = get_gifts_api_uri(payload['environment'])

    status = get_status(rest_server)
    if status is not None:
        if request.is_json:
            return jsonify('Submission aborted: %s' % status)
        else:
            return display_form(status)

    if payload is None:
        payload = request.json

    payload['rest_server'] = rest_server

    job = get_hive(action).create_job(analysis, payload)

    if request.is_json:
        results = {"job_id": job.job_id}
        return jsonify(results)
    else:
        return redirect(url_for(action + '_result', job_id=str(job.job_id)))


@app.route('/', methods=['GET'])
def index():
    return render_template('submit.html')


@app.route('/update_ensembl', methods=['POST'])
def update_ensembl(payload=None):
    analysis = app.config['HIVE_UPDATE_ENSEMBL_ANALYSIS']
    return submit_job(payload, analysis, 'update_ensembl')


@app.route('/update_ensembl', methods=['GET'])
def update_ensembl_list():
    analysis = app.config['HIVE_UPDATE_ENSEMBL_ANALYSIS']
    jobs = get_hive('update_ensembl').get_all_results(analysis)

    if request.is_json:
        return jsonify(jobs)
    else:
        return render_template('list.html', submission_type='Update Ensembl', jobs=jobs)


@app.route('/update_ensembl/<int:job_id>', methods=['GET'])
def update_ensembl_result(job_id):
    job = get_hive('update_ensembl').get_result_for_job_id(job_id, progress=False)

    if request.is_json:
        return jsonify(job)
    else:
        return render_template('list.html', submission_type='Update Ensembl', jobs=[job])


@app.route('/process_mapping', methods=['POST'])
def process_mapping(payload=None):
    analysis = app.config['HIVE_PROCESS_MAPPING_ANALYSIS']
    return submit_job(payload, analysis, 'process_mapping')


@app.route('/process_mapping', methods=['GET'])
def process_mapping_list():
    analysis = app.config['HIVE_PROCESS_MAPPING_ANALYSIS']
    jobs = get_hive('process_mapping').get_all_results(analysis)

    if request.is_json:
        return jsonify(jobs)
    else:
        return render_template('list.html', submission_type='Process Mapping', jobs=jobs)


@app.route('/process_mapping/<int:job_id>', methods=['GET'])
def process_mapping_result(job_id):
    job = get_hive('process_mapping').get_result_for_job_id(job_id, progress=False)

    if request.is_json:
        return jsonify(job)
    else:
        return render_template('list.html', submission_type='Process Mapping', jobs=[job])


@app.route('/submit', methods=['GET'])
def display_form(status=None):
    form = GIFTsSubmissionForm(request.form)

    return render_template(
        'submit.html',
        form=form,
        status=status
    )


@app.route('/submit', methods=['POST'])
def submit_form():
    # Convert the form fields into a 'payload' dictionary
    # that is the required input format for the hive submission.
    form = GIFTsSubmissionForm(request.form)

    payload = {
        'ensembl_release': form.ensembl_release.data,
        'environment': form.environment.data,
        'email': form.email.data,
        'tag': form.tag.data,
        'auth_token': form.auth_token.data
    }

    if form.update_ensembl.data:
        return update_ensembl(payload)
    elif form.process_mapping.data:
        return process_mapping(payload)
    else:
        raise RuntimeError('Unrecognised submission type')


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'})
