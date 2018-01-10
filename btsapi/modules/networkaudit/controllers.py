from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.networkaudit.models import AuditCategory, AuditRule
from btsapi.extensions import db
import datetime
from datatables import DataTables, ColumnDT
from flask_login import login_required
from btsapi import  app

mod_networkaudit = Blueprint('netaudit', __name__, url_prefix='/api/networkaudit')


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
                "open": False
            })

    return jsonify(tree_nodes)
