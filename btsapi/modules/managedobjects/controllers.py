from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.networkbaseline.models import NetworkBaseline, NetworkBaselineView, NetworkBaselineViewSchema
from btsapi import app, db
import datetime
from datatables import DataTables, ColumnDT

mod_managedobjects = Blueprint('managedobjects', __name__, url_prefix='/api/managedobjects')

