from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response, send_file
from btsapi.modules.networkaudit.models import AuditCategory, \
    AuditRule, AuditCategoryMASchema
from btsapi.modules.reports.models import Report, ReportCategory, \
    ReportCategoryMASchema, DummyTable, ReportsTaskLog, ReportMASchema
from btsapi.extensions import db
import datetime
from datatables import DataTables, ColumnDT
from flask_login import login_required
from btsapi import  app
from sqlalchemy import Table, MetaData
import csv
import pika
import os
import json


mod_networkaudit = Blueprint('netaudit', __name__, url_prefix='/api/networkaudit')


@mod_networkaudit.route('/rules', methods=['GET'])
@login_required
def get_audit_rules():
    audit_categories = AuditCategory.query.all()
    category_schema = AuditCategoryMASchema()

    audit_rule_data = []

    indx = 0
    for c in audit_categories:
        audit_rule_data.append({"cat_id": c.pk, "cat_name": c.name, "rules": []})
        rules = AuditRule.query.filter_by(category_pk=c.pk).all()
        for r in rules:
            rule = {"id": r.pk, "name": r.name }
            audit_rule_data[indx]["rules"].append(rule)
        indx += 1
        # app.logger.info(c)

    app.logger.info(audit_rule_data)

    return jsonify(audit_rule_data)


@mod_networkaudit.route('/tree/<cat_or_rule>/<int:parent_pk>', methods=['GET'])
@login_required
def get_audit_tree(cat_or_rule, parent_pk):
    """Get network audit category and audit tree
    cat_or_rule = categories for category nodes and "rules" for rule nodes
    """
    search_term = request.args.get('search_term',"")
    search_categories = request.args.get('search_categories', "false")
    search_rules = request.args.get('search_rules', "true")

    tree_nodes = []
    query = None

    if cat_or_rule == 'categories' and search_categories == "true":
        query = AuditCategory.query.filter(AuditCategory.name.ilike('%{}%'.format(search_term))).filter_by(parent_pk=parent_pk)

    if cat_or_rule == 'categories' and search_categories == "false":
        query = AuditCategory.query.filter_by(parent_pk=parent_pk)

    if cat_or_rule == 'rules' and search_rules == "true":
        query = AuditRule.query.filter(AuditRule.name.ilike('%{}%'.format(search_term))).filter_by(category_pk=parent_pk)

    if cat_or_rule == 'rules' and search_rules == "false":
        query = AuditRule.query.filter_by(category_pk=parent_pk)

    if query is not None:
        for r in query.all():
            tree_nodes.append({
                "id": r.pk,
                "label": r.name,
                "inode": True if cat_or_rule == 'categories' else False,
                "open": False,
                "nodeType": "category" if cat_or_rule == 'categories' else "rule"
            })

    return jsonify(tree_nodes)


@mod_networkaudit.route('/rule/fields/<int:audit_id>', methods=['GET'])
@login_required
def get_rule_data_fields(audit_id):
    """Get fields in audit data table"""
    fields = []

    rule = AuditRule.query.filter_by(pk=audit_id).first()

    metadata = MetaData()
    rule_table = Table( rule.table_name, metadata, autoload=True, autoload_with=db.engine, schema='network_audit')

    fields = [c.name for c in rule_table.columns]

    return jsonify(fields)


@mod_networkaudit.route('/rule/dt/<int:audit_id>', methods=['GET'])
@login_required
def get_rule_data(audit_id):
    """Get fields in audit data table"""

    rule = AuditRule.query.filter_by(pk=audit_id).first()

    metadata = MetaData()
    rule_table = Table( rule.table_name, metadata, autoload=True, autoload_with=db.engine, schema='network_audit')

    query = db.session.query(rule_table)

    columns = []
    for c in rule_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_networkaudit.route('/download/rule/<int:rule_id>', methods=['GET'])
# @login_required
def download_rule_data(rule_id):
    """Download rule table """

    try:

        rule = db.session.query(AuditRule).filter_by(pk=rule_id).one()
        category = db.session.query(AuditCategory).filter_by(pk=rule.category_pk).one()

        sanitized_filename = "{}__{}".format(category.name.lower().replace(" ", "_"), rule.name.lower().replace(" ", "_"))
        filename = "{}.csv".format(sanitized_filename)

        metadata  =MetaData()

        query = "SELECT * FROM network_audit.{} t".format(rule.table_name)
        task_log = ReportsTaskLog()
        task_log.action = 'reports.generate'
        task_log.status = 'PENDING'
        task_log.options = {'format': 'csv', 'filename': filename, 'query': query}

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

        return jsonify({'status': 'success',
                        'message': 'Download request received.',
                        'status_url': '/api/reports/download/status/{}'.format(task_id),
                        'download_url': '/api/reports/file/{}'.format(task_id)} )
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to start download', 'error': str(e)}),404