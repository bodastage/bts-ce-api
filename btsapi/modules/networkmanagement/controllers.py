from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response, send_file
from btsapi.modules.networkmanagement.models import LiveCell3G, LiveCell3GMASchema, LiveCell
from btsapi.extensions import  db
import datetime
import math
from sqlalchemy import Table, MetaData, or_
from sqlalchemy.orm import load_only
from datatables import DataTables, ColumnDT
from btsapi import app
from flask_login import login_required
import csv

mod_netmgt = Blueprint('networkmanagement', __name__, url_prefix='/api/network')


@mod_netmgt.route('/live/cells/3g', methods=['GET'], strict_slashes=False)
@login_required
def get_live_network_cells():
    page = request.args.get('page', 0)
    size = request.args.get('size', 10)
    search = request.args.get('search', None)

    # includes direction i.e column:asc or column:desc , default is natual order
    order_by = request.args.get('order_by', None)

    total = LiveCell3G.query.count()

    query = LiveCell3G.query.limit(size).offset(page)

    # @TODO: Add search filter
    if search is not None:
        query = query.filter(LiveCell3G.name.ilike('%{}%'.format(search)))

    if order_by is not None:
        query = query.order_by(order_by)

    cell_schema = LiveCell3GMASchema()

    pages = int(math.ceil(total/float(size)))
    return jsonify({
        "content":     [cell_schema.dump(v).data for v in query.all()],
        "size": size,
        "page": page,
        "last": ( int(page) == pages),
        "total": total,
        "pages": pages
    })


@mod_netmgt.route('/tree/cached', methods=['GET'], strict_slashes=False)
@login_required
def get_network_tree():
    """Get network pre computed live network tree"""
    source = request.args.get('source', "live") # live or plan

    # @TODO: Create model definitions
    metadata = MetaData()
    cache_table = Table('cache', metadata, autoload=True, autoload_with=db.engine, schema='public')

    response = app.response_class(
        response=db.session.query(cache_table).filter_by(name="live_network_aci_tree").first().data,
        status=200,
        mimetype='application/json'
    )
    return response


@mod_netmgt.route('/relations/dt', methods=['GET'], strict_slashes=False)
@login_required
def get_relations_dt_data():
    """Get relations in jQuery datatable data format"""

    metadata = MetaData()
    relations_table = Table('vw_relations', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    columns = []
    for c in relations_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(relations_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/nodes', methods=['GET'])
@login_required
def get_nodes():
    """Get a list of all the nodes in the system"""

    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    metadata = MetaData()
    nodes_table = Table('vw_nodes', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    columns = []
    column_index = 0
    for c in nodes_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(nodes_table).filter(nodes_table.columns.nodename != 'SubNetwork')

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/list/<entity>', methods=['GET'])
@login_required
def get_entity_list(entity):
    length = request.args.get("length",100)
    start = request.args.get("start", 0)
    parent_id = request.args.get("parent_id", None)

    fields = request.args.get("fields", "")
    metadata = MetaData()

    table = None
    columns = []
    data = []
    count = 0
    specific_cols = fields.split(",")
    if entity == 'node':
        table = Table('vw_nodes', metadata, autoload=True, autoload_with=db.engine, schema='live_network')
        query = db.session.query(table.columns.id, table.columns.nodename, table.columns.vendor, table.columns.technology).\
            filter(table.columns.nodename != 'SubNetwork')

    count = query.count()

    for row in query.all():
        data.append({"id": row[0], "name": row[1], "vendor": row[2], "technology": row[3]})

    return jsonify({"data": data, "total": count, "start": start, "length": length})


@mod_netmgt.route('/live/nodes/fields', methods=['GET'])
@login_required
def get_node_view_fields():
    """Get a list of all the nodes in the system"""

    metadata = MetaData()
    table = Table('vw_nodes', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/sites/fields', methods=['GET'])
@login_required
def get_site_view_fields():
    """Get a list of all the nodes in the system"""

    metadata = MetaData()
    table = Table('vw_sites', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/cells/gsm/fields', methods=['GET'])
@login_required
def get_gsm_cell_view_fields():
    """Get the list of fields in the GSM cell data view"""

    metadata = MetaData()
    table = Table('vw_gsm_cells_data', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/cells/umts/fields', methods=['GET'])
@login_required
def get_umts_cell_view_fields():
    """Get the list of fields in the UMTS cell data view"""

    metadata = MetaData()
    table = Table('vw_umts_cells_data', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/cells/lte/fields', methods=['GET'])
@login_required
def get_lte_cell_view_fields():
    """Get the list of fields in the LTE cell data view"""

    metadata = MetaData()
    table = Table('vw_lte_cells_data', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/relations/fields', methods=['GET'])
@login_required
def get_relations_view_fields():
    """Get a list of all the nodes in the system"""

    metadata = MetaData()
    table = Table('vw_relations', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/sites', methods=['GET'])
@login_required
def get_sites():
    """Get a list of all the vendors in the system"""

    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    metadata = MetaData()
    sites_table = Table('vw_sites', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    columns = []
    column_index = 0
    for c in sites_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(sites_table)

    row_table = DataTables(params, query, columns, True)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/relations', methods=['GET'])
@login_required
def get_relations():
    """Get a list of all network relations"""

    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    metadata = MetaData()
    relations_table = Table('vw_relations', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    columns = []
    column_index = 0
    for c in relations_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(relations_table)

    row_table = DataTables(params, query, columns)

    app.logger.info(params)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/cell/<int:cell_id>', methods=['GET'], strict_slashes=False)
@login_required
def get_cell_data(cell_id):

    cell_data_table = None
    metadata = MetaData()

    # cell = LiveCell.query.filter(pk=cell_id).first()
    cell = db.session.query(LiveCell).filter_by(pk=cell_id).first()

    if cell is None:
        return jsonify({}, 404)
    # UMTS Cells
    if cell.tech_pk == 2:
        cell_data_table = Table('vw_umts_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # GSM Cells
    if cell.tech_pk == 1:
        cell_data_table = Table('vw_gsm_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # LTE Cells
    if cell.tech_pk == 3:
        cell_data_table = Table('vw_lte_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    cell_data = db.session.query(cell_data_table).filter_by(cellname=cell.name).first()

    return jsonify(cell_data._asdict())


@mod_netmgt.route('/live/cellrelations/<int:cell_id>', methods=['GET'], strict_slashes=False)
@login_required
def get_cell_relations(cell_id):

    cell_data_table = None
    metadata = MetaData()

    # cell = LiveCell.query.filter(pk=cell_id).first()
    cell = db.session.query(LiveCell).filter_by(pk=cell_id).first()

    app.logger.info("cell.name {}".format(cell.name))
    if cell is None:
        return jsonify({}, 404)

    relation_table = Table('vw_relations', metadata, autoload=True, autoload_with=db.engine,
                            schema='live_network')

    cell_data = db.session.query(relation_table).filter(or_(
                                     relation_table.columns.svrcell==cell.name, \
                                     relation_table.columns.nbrcell == cell.name
                                 )).all()

    columns = [c.name for c in relation_table.columns]

    response_data = [{k: v for k, v in zip(columns, row)} for row in cell_data]

    return jsonify(response_data)


@mod_netmgt.route('/live/cells', methods=['GET'], strict_slashes=False)
@login_required
def get_cells():
    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    metadata = MetaData()

    cell_data_table = Table('cells', metadata, autoload=True, autoload_with=db.engine,
                            schema='live_network')

    columns = []
    column_index = 0
    for c in cell_data_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(cell_data_table)

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/cells/<tech>', methods=['GET'], strict_slashes=False)
@login_required
def get_cells_data(tech):
    """Get sites in jQuery datatable data format"""

    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    tech_pk = request.args.get("tech_pk", "2")  # Default is 3G

    cell_data_table = None

    metadata = MetaData()

    # UMTS Cells
    if tech == "umts":
        cell_data_table = Table('vw_umts_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # GSM Cells
    if tech == "gsm":
        cell_data_table = Table('vw_gsm_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # LTE Cells
    if tech == "lte":
        cell_data_table = Table('vw_lte_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    columns = []
    column_index = 0
    for c in cell_data_table.columns:
        search_method = 'string_contains'
        if request.args.get("columns[{}][search][regex]".format(column_index)) == 'true':
            search_method = 'regex'
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name, search_method=search_method))
        column_index += 1

    query = db.session.query(cell_data_table)

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/externals/gsm/fields', methods=['GET'])
@login_required
def get_gsm_externals_view_fields():
    """Get the list of fields in the LTE cell data view"""

    metadata = MetaData()
    table = Table('vw_gsm_external_cells', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/externals/umts/fields', methods=['GET'])
@login_required
def get_umts_externals_view_fields():
    """Get the list of fields in the LTE cell data view"""

    metadata = MetaData()
    table = Table('vw_umts_external_cells', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/externals/lte/fields', methods=['GET'])
@login_required
def get_lte_externals_view_fields():
    """Get the list of fields in the LTE cell data view"""

    metadata = MetaData()
    table = Table('vw_lte_external_cells', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    fields = [c.name for c in table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/externals/<tech>', methods=['GET'], strict_slashes=False)
@login_required
def get_external_cells_data(tech):
    """Get external cells parameter data in jQuery datatable data format"""

    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    if tech == 'gsm': tech_pk = 1
    if tech == 'umts': tech_pk = 2
    if tech == 'lte': tech_pk = 3

    cell_data_table = None

    metadata = MetaData()

    # UMTS External Cells
    if tech == "umts":
        cell_data_table = Table('vw_umts_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # GSM External Cells
    if tech == "gsm":
        cell_data_table = Table('vw_gsm_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # LTE External Cells
    if tech == "lte":
        cell_data_table = Table('vw_lte_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if cell_data_table is None:
        return jsonify([])

    columns = []
    for c in cell_data_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(cell_data_table)

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())



@mod_netmgt.route('/nodes/dt', methods=['GET'], strict_slashes=False)
@login_required
def get_nodes_dt_data():
    """Get nodes in jQuery datatable data format"""

    metadata = MetaData()
    nodes_table = Table('vw_nodes', metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    columns = []
    for c in nodes_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(nodes_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/sites/dt', methods=['GET'], strict_slashes=False)
@login_required
def get_site_dt_data():
    """Get sites in jQuery datatable data format"""

    metadata = MetaData()
    sites_table = Table('vw_sites', metadata, autoload=True, autoload_with=db.engine, schema='live_network')


    columns = []
    for c in sites_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(sites_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/cells/fields', methods=['GET'], strict_slashes=False)
@login_required
def get_network_cells_field_list():
    """Get field list"""
    fields = []

    tech_pk = request.args.get("tech_pk","2") # Default is 3G
    cell_data_table = None

    if tech_pk == "1":
        metadata = MetaData()
        cell_data_table = Table('vw_gsm_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if tech_pk == "2":
        metadata = MetaData()
        cell_data_table = Table('vw_umts_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if tech_pk == "3":
        metadata = MetaData()
        cell_data_table = Table('vw_lte_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if cell_data_table is None:
        return jsonify([])

    fields = [c.name for c in cell_data_table.columns]

    return jsonify(fields)


@mod_netmgt.route('/live/cells/dt', methods=['GET'], strict_slashes=False)
@login_required
def get_cells_dt_data():
    """Get sites in jQuery datatable data format"""

    tech_pk = request.args.get("tech_pk", "2")  # Default is 3G

    cell_data_table = None

    metadata = MetaData()

    # UMTS Cells
    if tech_pk == "2":
        cell_data_table = Table('vw_umts_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # GSM Cells
    if tech_pk == "1":
        cell_data_table = Table('vw_gsm_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # LTE Cells
    if tech_pk == "3":
        cell_data_table = Table('vw_lte_cells_data', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')


    columns = []
    for c in cell_data_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(cell_data_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/live/extcells/fields', methods=['GET'], strict_slashes=False)
@login_required
def get_network_extcells_field_list():
    """Get external cells field/parameter """
    fields = []

    tech_pk = request.args.get("tech_pk","2") # Default is 3G
    cell_data_table = None

    if tech_pk == "1":
        metadata = MetaData()
        cell_data_table = Table('vw_gsm_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if tech_pk == "2":
        metadata = MetaData()
        cell_data_table = Table('vw_umts_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if cell_data_table is None:
        return jsonify([])

    fields = [c.name for c in cell_data_table.columns]

    return jsonify(fields)



@mod_netmgt.route('/live/extcells/dt', methods=['GET'], strict_slashes=False)
@login_required
def get_external_cells_dt_data():
    """Get external cells parameter data in jQuery datatable data format"""

    tech_pk = request.args.get("tech_pk", "2")  # Default is 3G

    cell_data_table = None

    metadata = MetaData()

    # UMTS External Cells
    if tech_pk == "2":
        cell_data_table = Table('vw_umts_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    # GSM External Cells
    if tech_pk == "1":
        cell_data_table = Table('vw_gsm_external_cells', metadata, autoload=True, autoload_with=db.engine,
                                schema='live_network')

    if cell_data_table is None:
        return jsonify([])

    columns = []
    for c in cell_data_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(cell_data_table)

    # GET request parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


@mod_netmgt.route('/download/<entity_types>', methods=['GET'], strict_slashes=False)
def download_network_entities(entity_types):
    """Download  network entities """
    metadata = MetaData()

    entity_table_map = {"nodes":"nodes", "sites": "vw_sites", "relations":"vw_relations"}

    table_name = entity_types  # nodes,

    if entity_types in entity_table_map:
        table_name = entity_table_map[entity_types]  # nodes,

    table = Table( table_name, metadata, autoload=True, autoload_with=db.engine, schema='live_network')

    sanitized_filename = "{}".format(entity_types.lower().replace(" ","_") )
    filename = "{}.csv".format(sanitized_filename)
    path_to_file = '/tmp/{}'.format(filename)

    outfile = open( path_to_file, 'wb')
    outcsv = csv.writer(outfile)
    records = db.session.query(table).all()

    columns_to_skip = ['pk', 'added_by', 'modified_by','notes', 'tech_pk', 'vendor_pk']

    outcsv.writerow([column.name.upper() for column in filter(lambda c: c.name not in columns_to_skip, table.columns ) ])

    [outcsv.writerow([getattr(curr, column.name) for column in filter(lambda c: c.name not in columns_to_skip, table.columns ) ]) for curr in records]
    # [outcsv.writerow([getattr(curr, column.name) for column in rule_table.columns]) for curr in records]

    outfile.close()

    # return send_file(path_to_file, attachment_filename=filename, mimetype="text/plain")
    return send_file(path_to_file, attachment_filename=filename, mimetype='application/octet-stream', as_attachment=True,)