from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.networkbaseline.models import NetworkBaseline, NetworkBaselineView, NetworkBaselineViewSchema
from btsapi import app, db
import datetime
from datatables import DataTables, ColumnDT


mod_networkbaseline = Blueprint('networkbaseline', __name__, url_prefix='/api/networkbaseline')


@mod_networkbaseline.route('/dt/', methods=['GET'])
def get_dt_data():
    """Get baseline values in datatables format"""

    # Define columns
    columns = [
        ColumnDT(NetworkBaselineView.vendor),
        ColumnDT(NetworkBaselineView.technology),
        ColumnDT(NetworkBaselineView.mo),
        ColumnDT(NetworkBaselineView.parameter),
        ColumnDT(NetworkBaselineView.value),
        ColumnDT(NetworkBaselineView.date_added),
        ColumnDT(NetworkBaselineView.date_modified),
    ]

    query = NetworkBaselineView.query;

    # GET parameters
    params = request.args.to_dict()

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())


