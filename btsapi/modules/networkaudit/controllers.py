from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.networkaudit.models import AuditCategory, AuditRule
from btsapi.extensions import db
import datetime
from datatables import DataTables, ColumnDT
from flask_login import login_required

mod_networkaudit = Blueprint('netaudit', __name__, url_prefix='/api/networkaudit')


def get_audit_tree():
    """Get network audit category and audit tree"""
    search_term = request.args.get('search_term',None)
    search_categories = request.args.get('search_term', True)
    search_rules = request.args.get('search_term', True)


    pass
