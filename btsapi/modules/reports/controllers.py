from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response, send_file
from btsapi.modules.reports.models import Report, ReportCategory, ReportCategoryMASchema, DummyTable, ReportsTaskLog, ReportMASchema
from btsapi.extensions import  db
import datetime
import math
from sqlalchemy import Table, MetaData, or_, text, Column, String
from sqlalchemy.orm import load_only, Query
from datatables import DataTables, ColumnDT
from btsapi import app
from flask_login import login_required
import csv
from .dttables import DataTables as DTTables
from sqlalchemy.dialects import postgresql
import pika
import json
import os

mod_reports = Blueprint('reports', __name__, url_prefix='/api/reports')


@mod_reports.route('/', methods=['GET'], strict_slashes=False)
@login_required
def get_reports():
    """Get reports"""
    report_categories = ReportCategory.query.all()

    reports = db.session.query(Report).all()

    report_data = []

    indx = 0
    for c in report_categories:
        report_data.append({"cat_id": c.pk, "cat_name": c.name, "reports": []})
        reports = db.session.query(Report).filter_by(category_pk=c.pk).all()
        for r in reports:
            report = {"id": r.pk, "name": r.name}
            report_data[indx]["reports"].append(report)
        indx += 1
    return jsonify(report_data)

@mod_reports.route('/tree/<cat_or_report>/<int:parent_pk>', methods=['GET'], strict_slashes=False)
@login_required
def get_audit_tree(cat_or_report, parent_pk):
    """Get nreport category and report
    cat_or_report = categories for category nodes and "reports" for report nodes
    """
    search_term = request.args.get('search_term',"")
    search_categories = request.args.get('search_categories', "false")
    search_reports = request.args.get('search_reports', "true")

    tree_nodes = []
    query = None

    if cat_or_report == 'categories' and search_categories == "true":
        query = ReportCategory.query.filter(ReportCategory.name.ilike('%{}%'.format(search_term))).filter_by(parent_pk=parent_pk)

    if cat_or_report == 'categories' and search_categories == "false":
        query = ReportCategory.query.filter_by(parent_pk=parent_pk)

    if cat_or_report == 'rules' and search_reports == "true":
        query = Report.query.filter(Report.name.ilike('%{}%'.format(search_term))).filter_by(category_pk=parent_pk)

    if cat_or_report == 'rules' and search_reports == "false":
        query = Report.query.filter_by(category_pk=parent_pk)

    if query is not None:
        for r in query.all():
            tree_nodes.append({
                "id": r.pk,
                "label": r.name,
                "inode": True if cat_or_report == 'categories' else False,
                "open": False,
                "nodeType": "category" if cat_or_report == 'categories' else "report"
            })

    return jsonify(tree_nodes)


@mod_reports.route('/fields/<int:report_id>', methods=['GET'])
@login_required
def get_report_data_fields(report_id):
    fields = []

    report = db.session.query(Report).filter_by(pk=report_id).first()

    fields = db.engine.execute(report.query).keys()

    return jsonify(fields)


def get_query_from_dt_request(request, report_query):
    """
    Takes are request in dt format
    :param request:
    :param report_query:
    :return:
    """
    q = Query(DummyTable)

    # #############
    table_columns = db.engine.execute(text(report_query)).keys()
    params = request.args.to_dict()
    columns = []
    for c in table_columns:
        columns.append(ColumnDT( Column(c, String(255)), column_name=c, mData=c))
    dt_table = DTTables(params, q, columns)
    # app.logger.info(dt_table.compile_query(query=dt_table.filtered_query))

    dt_sql = dt_table.compile_query()
    dt_sql = dt_sql.replace('dummy_table.dummy_pk,','')
    dt_sql = dt_sql.replace('FROM dummy_table','FROM ({}) dt '.format(report_query))
    app.logger.info(dt_sql)

    dt_filtered_sql = dt_table.compile_query(query=dt_table.filtered_query)
    dt_filtered_sql = dt_filtered_sql.replace('dummy_table.dummy_pk,','')
    dt_filtered_sql = dt_filtered_sql.replace('FROM dummy_table','FROM ({}) dt '.format(report_query))
    app.logger.info(dt_filtered_sql)

    cardinality = db.engine.execute(text(report_query)).rowcount
    cardinality_filtered = db.engine.execute(text(dt_filtered_sql)).rowcount

    result = db.engine.execute(text(dt_sql))
    data_results = [{k: v for k, v in zip(
        table_columns, row)} for row in result.fetchall()]

    output = {}
    output['draw'] = str(int(params['draw']))
    output['recordsTotal'] = str(cardinality)
    output['recordsFiltered'] = str(cardinality_filtered)
    output['data'] = data_results

    return output


@mod_reports.route('/dt/<int:report_id>', methods=['GET'])
@login_required
def get_report_data(report_id):

    report = db.session.query(Report).filter_by(pk=report_id).first()

    output = get_query_from_dt_request(request, report.query)

    return jsonify(output)


@mod_reports.route('/download/<int:report_id>', methods=['GET'])
@login_required
def download_report(report_id):
    try:

        report = db.session.query(Report).filter_by(pk=report_id).one()
        category = db.session.query(ReportCategory).filter_by(pk=report.category_pk).one()

        sanitized_filename = "{}__{}".format(category.name.lower().replace(" ", "_"), report.name.lower().replace(" ", "_"))
        filename = "{}.csv".format(sanitized_filename)

        metadata  =MetaData()

        # task_log = Table('reports_task_log', metadata, autoload=True, autoload_with=db.engine, schema="reports")
        task_log = ReportsTaskLog()
        task_log.action = 'reports.generate'
        task_log.status = 'PENDING'
        task_log.options = {'format': 'csv', 'filename': filename, 'query': report.query}

        db.session.add(task_log)
        db.session.commit()
        db.session.flush()
        task_id = task_log.pk

        # Send download task to reports queue

        mq_user = os.getenv("BTS_MQ_USER", "btsuser")
        mq_pass = os.getenv("BTS_MQ_PASS", "Password@7")
        mq_host = os.getenv("BTS_MQ_HOST", "192.168.99.100")
        mq_vhost = os.getenv("BTS_MQ_VHOST", "/bs")

        credentials = pika.PlainCredentials(mq_user, mq_pass)
        parameters = pika.ConnectionParameters(mq_host, virtual_host=mq_vhost, credentials=credentials)

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue='reports', durable=True)

        data = json.dumps({'task_id': task_id})
        channel.basic_publish(exchange='',
                              routing_key='reports',
                              body=data)
        channel.close()

        return jsonify({'status': 'PENDING', # Job status
                        'message': 'Download job logged.',
                        'status_url': '/api/reports/download/status/{}'.format(task_id),
                        'download_url': '/api/reports/file/{}'.format(task_id)} )
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to start download', 'error': str(e)}),404


@mod_reports.route('/download/status/<int:job_id>')
@login_required
def get_download_status(job_id):
    task = db.session.query(ReportsTaskLog).filter_by(pk=job_id).one()
    if task is None:
        return jsonify({'message': 'Message does not exist'}), 404

    return jsonify({'status': task.status, 'log': task.log})


@mod_reports.route('/file/<int:job_id>')
def get_download_file(job_id):
    task = db.session.query(ReportsTaskLog).filter_by(pk=job_id).one()
    if task is None:
        return jsonify({'message': 'Download does not exist'}), 404

    if task.status != 'FINISHED':
        return jsonify({'message': 'Download does not exist'}), 404

    filename = task.log
    path_to_file  = '/reports/{}'.format(filename)
    try:
        return send_file(path_to_file, attachment_filename=filename, mimetype='application/octet-stream', as_attachment=True, )
    except Exception as e:
        return jsonify({'message': str(e)}), 404


@mod_reports.route('/create/fields', methods=['POST'])
def get_new_report_columns():
    """Get the list of columns/fields in the new report query"""
    content = request.get_json()
    qry = content['qry']

    try:
        fields = db.engine.execute(text(qry)).keys()
        return jsonify(fields)
    except Exception as e:
        return str(e), 400


@mod_reports.route('/create/dt', methods=['POST'])
def get_new_report_data():
    """Takes a post request with the report name and SQL. Returns report data"""
    content = request.get_json()

    try:
        output = get_query_from_dt_request(request, content['qry'])
        return jsonify(output)

    except Exception as e:
        return str(e), 400


@mod_reports.route('/create', methods=['POST'])
def create_or_update_report():
    content = request.get_json()

    try:
        if 'report_id' not in content:
            report = Report(name=content['name'],
                            category_pk=content['category_id'],
                            query=content['qry'],
                            notes=content['notes'],
                            options=content['options'])

            db.session.add(report)
            db.session.commit()
        else:
            report = db.session.query(Report).filter_by(pk=content['report_id']).first()
            report.name = content['name']
            report.category_pk = content['category_id']
            report.notes = content['notes']
            report.query = content['qry']
            report.options = content['options']
            db.session.commit()

        return jsonify({}), 201
    except Exception as e:
        return str(e), 400


@mod_reports.route('/create/<int:report_id>', methods=['POST'])
def update_report(report_id):
    content = request.get_json()

    try:
        report = db.session.query(Report).filter_by(pk=report_id).first()
        report.name = content['name']
        report.category_pk = content['category_id']
        report.notes = content['notes']
        report.query = content['qry']
        report.options = content['options']
        db.session.commit()

        return jsonify({}), 201
    except Exception as e:
        return str(e), 400


@mod_reports.route('/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):

    try:
        db.session.query(Report).filter_by(pk=report_id).delete()

        db.session.commit()

        return jsonify({}), 200
    except Exception as e:
        return jsonify(str(e)), 400


@mod_reports.route('/<int:report_id>')
def get_report(report_id):

    try:

        report_schema = ReportMASchema()

        return jsonify(report_schema.dump(db.session.query(Report).get(report_id)).data)
    except Exception as e:
        return jsonify(str(e)), 400


@mod_reports.route('/categories', methods=['POST'])
def create_category():
    content = request.get_json()

    try:
        category = ReportCategory(name=content['name'],
                                notes=content['notes'])

        db.session.add(category)
        db.session.commit()

        return jsonify({}), 201
    except Exception as e:
        return str(e), 400


@mod_reports.route('/categories/<int:id>', methods=['POST'])
def update_category(id):
    content = request.get_json()

    try:
        category = db.session.query(ReportCategory).filter_by(pk=id).first()
        category.name = content['name']
        category.notes = content['notes']
        db.session.commit()

        return jsonify({}), 201
    except Exception as e:
        return str(e), 400


@mod_reports.route('/categories/<int:id>', methods=['GET'])
def get_category(id):
    content = request.get_json()

    try:
        category = db.session.query(ReportCategory).filter_by(pk=id).one()
        ma_schema = ReportCategoryMASchema()

        return jsonify(ma_schema.dump(category).data)

        return jsonify({}), 201
    except Exception as e:
        return str(e), 400


@mod_reports.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    try:

        # First delete the reports under the category
        db.session.query(Report).filter_by(category_pk=id).delete()

        db.session.query(ReportCategory).filter_by(pk=id).delete()

        db.session.commit()

        return jsonify({}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 400


@mod_reports.route('/graphdata/<int:report_id>', methods=['GET'])
@login_required
def get_graph_data(report_id):
    """
    Get graph data for report of type Graph

    :param report_id:
    :return:
    """
    report = db.session.query(Report).filter_by(pk=report_id).first()

    #@TODO: Add check for report type

    table_columns = db.engine.execute(text(report.query)).keys()
    result = db.engine.execute(text(report.query))

    data_results = [{k: v for k, v in zip(
        table_columns, row)} for row in result.fetchall()]

    return jsonify(data_results)
