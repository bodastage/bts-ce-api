from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for, \
    jsonify, make_response
from btsapi.modules.settings.models import Setting, SettingMASchema, SupportedVendorTech
from btsapi.extensions import  db
import datetime
import math
from flask_login import login_required
from sqlalchemy import update,  Table, MetaData
from btsapi import app
from datatables import DataTables, ColumnDT

mod_settings = Blueprint('settings', __name__, url_prefix='/api/settings')


@mod_settings.route('/', methods=['GET'], strict_slashes=False)
@login_required
def get_all_settings():
    """Get all settings"""

    setting_schema = SettingMASchema()

    return jsonify( [setting_schema.dump(v).data for v in Setting.query.all()] )


@mod_settings.route('/<string:name>', methods=['GET'], strict_slashes=False)
@login_required
def get_setting_value_by_name(name):
    """Get value for a setting"""

    setting_schema = SettingMASchema()

    return jsonify(setting_schema.dump(Setting.query.filter_by(name=name).first()).data)


@mod_settings.route('/<int:id>', methods=['GET'], strict_slashes=False)
@login_required
def get_setting_value_by_id(id):
    """Get value for a setting"""

    setting_schema = SettingMASchema()

    return jsonify(setting_schema.dump(Setting.query.filter_by(pk=id).first()).data)


@mod_settings.route('/category/<cat_id>', methods=['GET'], strict_slashes=False)
@login_required
def get_settings_by_category_id(cat_id):
    """Get value for a setting"""

    setting_schema = SettingMASchema()

    return jsonify(setting_schema.dump(Setting.query.filter_by(category_id=cat_id).all(), many=True).data)


@mod_settings.route('/<int:id>',methods=['POST'], strict_slashes=False)
@login_required
def update_setting(id):
    """Update setting
       value @param String|Integer|date Setting value
       name=setting name
       data_type = string|integer|timestamp|float
    """
    content = request.get_json()

    name = content['name']
    value= content['value']
    data_type = content['data_type']

    setting = Setting.query.filter_by(pk=id).first()

    if "name" in content: setting.name = content['name']
    if "value" in content:
        if data_type == 'string': setting.string_value = content['value']
        if data_type == 'text': setting.text_value = content['value']
        if data_type == 'integer': setting.integer_value = int(content['value'])
        if data_type == 'float': setting.float_value = float(content['value'])
        if data_type == 'timestamp': setting.timestamp_value = datetime(content['value'])

    db.session.commit()

    return jsonify({})


@mod_settings.route('/cm/vendor_format_map/dt',methods=['GET'], strict_slashes=False)
@login_required
def get_supported_vendor_cm_file_format():
    """
    Get support file format for each vendor and technology
    """
    metadata = MetaData()
    table = Table('vw_vendor_cm_file_formats', metadata, autoload=True, autoload_with=db.engine)

    columns = []
    for c in table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_settings.route('/network/technologies/dt', methods=['GET'], strict_slashes=False)
def get_supported_vendor_technologies():
    """
        Get supported technologies and vendors in the network
    """

    metadata = MetaData()
    supported_vendor_tech = Table('vw_supported_vendor_tech', metadata, autoload=True, autoload_with=db.engine, schema='public')

    columns = []
    for c in supported_vendor_tech.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(supported_vendor_tech)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())



@mod_settings.route('/network/technologies', methods=['POST'], strict_slashes=False)
def add_supported_vendor_technologies():
    """
    Add supoorted vendor technlogies

    :return:
    """
    content = request.get_json()

    vendor_pk = content['vendor_pk']
    tech_pk = content['tech_pk']

    # Does the vendor to tech mapping exist?
    supported_vender_tech = SupportedVendorTech.query.filter_by(vendor_pk=vendor_pk, tech_pk=tech_pk).first()

    if supported_vender_tech != None:
        return jsonify({"message":"Mapping already exists", "status":"error", "code": 409 })

    vendor_tech = SupportedVendorTech(vendor_pk=vendor_pk, tech_pk=tech_pk)

    db.session.add(vendor_tech)
    db.session.commit()

    return jsonify({"status": "success"})

@mod_settings.route('/network/technologies/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_supported_vendor_technologies(id):
    """
    Delete vendor technology map
    :param id: Vendor technology map od

    :return:
    """

    SupportedVendorTech.query.filter_by(pk=id).delete()

    db.session.commit()

    return jsonify({"status": "success"})