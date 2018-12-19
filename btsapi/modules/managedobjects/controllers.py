from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response, send_file
from btsapi.modules.managedobjects.models import ManagedObject, ManagedObjectSchema, ManagedObjectsMASchema, \
    NormalizedManagedObjectsSchema
from btsapi.extensions import db
import datetime
from datatables import DataTables, ColumnDT
from sqlalchemy import  text, Table, MetaData
import json
from btsapi import app
from flask_login import login_required
import csv

mod_managedobjects = Blueprint('managedobjects', __name__, url_prefix='/api/managedobjects')


@mod_managedobjects.route('/tree/<int:parent_pk>/', methods=['GET'])
@login_required
def get_aci_tree_data(parent_pk):
    """Get aci tree data for managed objects"""
    vendor_pk = request.args.get('vendor_pk', None)
    tech_pk = request.args.get('tech_pk', None)
    swversion_pk = request.args.get('swversion_pk', None)
    search_term = request.args.get('search_term', None)

    mo_aci_entries = []
    query = None

    metadata = MetaData()
    ManagedObject = Table('normalized_managedobjects', metadata, autoload=True, autoload_with=db.engine)

    if vendor_pk is not None and tech_pk is not None and search_term is not None and len(search_term) == 0:
        query = db.session.query(ManagedObject).filter_by(vendor_pk=vendor_pk,tech_pk=tech_pk)

    if vendor_pk is not None and tech_pk is not None and search_term is not None and len(search_term) > 0:
        query = db.session.query(ManagedObject).filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).\
            filter(ManagedObject.c.name.ilike('%{}%'.format(search_term))).filter(ManagedObject.c.pk != parent_pk)


    if query is None:
        return jsonify([])

    for mo in query.all():
        mo_aci_entries.append(dict(id=mo.pk, label=mo.name, inode=False, open=True))

    # @TODO: Add pagination
    return jsonify(mo_aci_entries)


@mod_managedobjects.route('/<vendor>/<tech>', methods=['GET'])
@login_required
def get_mos(vendor, tech):
    metadata = MetaData()
    managedobject_table = Table('normalized_managedobjects', metadata, autoload=True, autoload_with=db.engine)

    managedobjects = None

    if vendor.lower() == 'ericsson' and tech.lower() == 'gsm':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=1, tech_pk=1).all()

    if vendor.lower() == 'ericsson' and tech.lower() == 'umts':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=1, tech_pk=2).all()

    if vendor.lower() == 'ericsson' and tech.lower() == 'lte':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=1, tech_pk=3).all()

    if vendor.lower() == 'huawei' and tech.lower() == 'gsm':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=2, tech_pk=1).all()

    if vendor.lower() == 'huawei' and tech.lower() == 'umts':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=2, tech_pk=2).all()

    if vendor.lower() == 'huawei' and tech.lower() == 'lte':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=2, tech_pk=3).all()


    if vendor.lower() == 'zte' and tech.lower() == 'gsm':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=3, tech_pk=1).all()

    if vendor.lower() == 'zte' and tech.lower() == 'umts':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=3, tech_pk=2).all()

    if vendor.lower() == 'zte' and tech.lower() == 'lte':
        managedobjects = db.session.query(managedobject_table).filter_by(vendor_pk=3, tech_pk=3).all()


    if managedobjects is None:
        return jsonify([])

    mo_schema = NormalizedManagedObjectsSchema()

    return jsonify([mo_schema.dump(v).data for v in managedobjects],)


@mod_managedobjects.route('/tree/cached', methods=['GET'])
@login_required
def get_cached_mo_tree():
    """Get aci tree data from precomputed tree from the db"""
    vendor_pk = request.args.get("vendor_pk", None)
    tech_pk = request.args.get('tech_pk', None)

    metadata = MetaData()
    cache_table = Table('cache', metadata, autoload=True, autoload_with=db.engine, schema='public')

    # vendor = Ericsson, technology = UMTS or LTE
    if int(vendor_pk) == 1 and int(tech_pk) == 2:
        response = app.response_class(
            response=db.session.query(cache_table).filter_by(name="mo_aci_tree").first().data,
            status=200,
            mimetype='application/json'
        )
        return response

    return jsonify([])


@mod_managedobjects.route('/fields/<int:mo_pk>/', methods=['GET'])
@login_required
def get_fields_in_mo_table(mo_pk):
    """Get the column files in the managed objects cm data table"""

    fields = []

    # Get the vendor and technology pk's
    metadata = MetaData()
    managedobject_table = Table('normalized_managedobjects', metadata, autoload=True, autoload_with=db.engine)
    managedobject = db.session.query(managedobject_table).filter_by(pk=mo_pk).first()

    vendor_pk = managedobject.vendor_pk
    tech_pk = managedobject.tech_pk
    mo_name = managedobject.name

    # Get the schema
    managedobject_schema = ManagedObjectSchema.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()
    schema_name = managedobject_schema.name.lower()

    if vendor_pk == 2: schema_name = 'huawei_cm'

    mo_table_name = "{0}.{1}".format(schema_name,mo_name)
    # app.logger.info(mo_table_name)

    metadata = MetaData()
    mo_data_table = Table(mo_name, metadata, autoload=True,autoload_with=db.engine, schema=schema_name)

    fields = [c.name for c in mo_data_table.columns]

    return jsonify(fields)


@mod_managedobjects.route('/dt/<int:mo_pk>/', methods=['GET'])
@login_required
def get_dt_data(mo_pk):
    """Get managed objects values in jQuery datatables format"""

    # Get the vendor and technology pk's
    # managedobject = ManagedObject.query.filter_by(pk=mo_pk).first()
    metadata = MetaData()
    managedobject_table = Table('normalized_managedobjects', metadata, autoload=True, autoload_with=db.engine)
    managedobject = db.session.query(managedobject_table).filter_by(pk=mo_pk).first()

    vendor_pk = managedobject.vendor_pk
    tech_pk = managedobject.tech_pk
    mo_name = managedobject.name

    # Get the schema
    managedobject_schema = ManagedObjectSchema.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()
    schema_name = managedobject_schema.name.lower()

    if vendor_pk == 2: schema_name = 'huawei_cm'

    # app.logger.info(schema_name)
    mo_data_table = Table(mo_name, metadata, autoload=True, autoload_with=db.engine, schema=schema_name)

    columns = []
    column_index = 0
    for c in mo_data_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(mo_data_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_managedobjects.route('/download/<int:mo_pk>/', methods=['GET'])
# @login_required
def download_managed_object_data(mo_pk):
    """Download managed object data"""

    # Get the vendor and technology pk's
    metadata = MetaData()
    managedobject_table = Table('normalized_managedobjects', metadata, autoload=True, autoload_with=db.engine)
    managedobject = db.session.query(managedobject_table).filter_by(pk=mo_pk).first()

    vendor_pk = managedobject.vendor_pk
    tech_pk = managedobject.tech_pk
    mo_name = managedobject.name

    # Get the schema
    managedobject_schema = ManagedObjectSchema.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()
    schema_name = managedobject_schema.name.lower()

    if vendor_pk == 2: schema_name = 'huawei_cm'
    
    # app.logger.info(schema_name)
    mo_data_table = Table(mo_name, metadata, autoload=True, autoload_with=db.engine, schema=schema_name)

    sanitized_filename = "{}".format(mo_name )
    filename = "{}.csv".format(sanitized_filename)
    path_to_file = '/tmp/{}'.format(filename)

    outfile = open( path_to_file, 'wb')
    outcsv = csv.writer(outfile)
    records = db.session.query(mo_data_table).all()

    # columns to skip
    columns_to_skip = []

    outcsv.writerow([column.name for column in filter(lambda c: c.name not in columns_to_skip, mo_data_table.columns ) ])

    [outcsv.writerow([getattr(curr, column.name) for column in filter(lambda c: c.name not in columns_to_skip, mo_data_table.columns ) ]) for curr in records]

    outfile.close()

    return send_file(path_to_file, attachment_filename=filename, mimetype='application/octet-stream', as_attachment=True,)