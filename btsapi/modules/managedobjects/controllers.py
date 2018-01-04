from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.managedobjects.models import ManagedObject, ManagedObjectSchema, ManagedObjectsMASchema
from btsapi import app, db
import datetime
from datatables import DataTables, ColumnDT
from sqlalchemy import  text, Table, MetaData

mod_managedobjects = Blueprint('managedobjects', __name__, url_prefix='/api/managedobjects')


@mod_managedobjects.route('/tree/<int:parent_pk>/', methods=['GET'])
def get_aci_tree_data(parent_pk):
    """Get aci tree data for managed objects"""
    vendor_pk = request.args.get('vendor_pk', None)
    tech_pk = request.args.get('tech_pk', None)
    swversion_pk = request.args.get('swversion_pk', None)
    search_term = request.args.get('search_term', None)

    mo_aci_entries = []
    query = None

    if vendor_pk is not None and tech_pk is not None and swversion_pk is None and parent_pk is None:
        query = ManagedObject.query.filter_by(vendor_pk=vendor_pk,tech_pk=tech_pk)

    if vendor_pk is not None and tech_pk is None and swversion_pk is None and parent_pk is None:
        query = ManagedObject.query.filter_by(vendor_pk=vendor_pk)

    if vendor_pk is not None and tech_pk is not None and swversion_pk is None and parent_pk is not None \
            and search_term is not None and len(search_term) == 0:
        query = ManagedObject.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk,parent_pk=parent_pk)

    if vendor_pk is not None and tech_pk is not None and swversion_pk is None and parent_pk is not None \
            and search_term is not None and len(search_term) > 0:
        query = ManagedObject.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk,parent_pk=parent_pk).\
            filter(ManagedObject.name.ilike('%ed%'))

    if query is None:
        return jsonify([])

    for mo in query.all():
        mo_aci_entries.append(dict(id=mo.pk, label=mo.name, inode=True, open=False))

    # @TODO: Add pagination
    return jsonify(mo_aci_entries)


@mod_managedobjects.route('/fields/<int:mo_pk>/', methods=['GET'])
def get_fields_in_mo_table(mo_pk):
    """Get the column files in the managed objects cm data table"""

    fields = []

    # Get the vendor and technology pk's
    managedobject = ManagedObject.query.filter_by(pk=mo_pk).first()
    vendor_pk = managedobject.vendor_pk
    tech_pk = managedobject.tech_pk
    mo_name = managedobject.name

    # Get the schema
    managedobject_schema = ManagedObjectSchema.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()
    schema_name = managedobject_schema.name.lower()
    mo_table_name = "{0}.{1}".format(schema_name,mo_name)

    metadata = MetaData()
    mo_data_table =  Table(mo_name.lower(), metadata, autoload=True,autoload_with=db.engine, schema=schema_name)

    fields = [c.name for c in mo_data_table.columns]

    return jsonify(fields)


@mod_managedobjects.route('/dt/<int:mo_pk>/', methods=['GET'])
def get_dt_data(mo_pk):
    """Get managed objects values in jQuery datatables format"""

    fields = []

    # Get the vendor and technology pk's
    managedobject = ManagedObject.query.filter_by(pk=mo_pk).first()
    vendor_pk = managedobject.vendor_pk
    tech_pk = managedobject.tech_pk
    mo_name = managedobject.name

    # Get the schema
    managedobject_schema = ManagedObjectSchema.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()
    schema_name = managedobject_schema.name.lower()
    mo_table_name = "{0}.{1}".format(schema_name, mo_name)

    metadata = MetaData()
    mo_data_table = Table(mo_name.lower(), metadata, autoload=True, autoload_with=db.engine, schema=schema_name)

    fields = [c.name for c in mo_data_table.columns]

    columns = []
    for c in mo_data_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(mo_data_table)

    app.logger.info(str(query))

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())