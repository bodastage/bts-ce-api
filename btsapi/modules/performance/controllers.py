from flask_login import login_required
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from sqlalchemy import Table, MetaData, or_
from sqlalchemy.orm import load_only
from datatables import DataTables, ColumnDT
from btsapi.extensions import  db

mod_pm = Blueprint('pm', __name__, url_prefix='/api/pm')


@mod_pm.route('/site_stats', methods=['GET'])
@login_required
def get_site_stats():
    """Get site statistics"""
    params = request.args.to_dict()
    params['draw']=1
    params['length'] = request.args.get("length",10)
    params['start'] = request.args.get("start", 0)

    metadata = MetaData()

    site_stats_table = Table('vw_site_stats', metadata, autoload=True, autoload_with=db.engine,
                            schema='pm')

    columns = []
    for c in site_stats_table.columns:
        columns.append(ColumnDT( c, column_name=c.name, mData=c.name))

    query = db.session.query(site_stats_table)

    row_table = DataTables(params, query, columns)

    return jsonify(row_table.output_result())