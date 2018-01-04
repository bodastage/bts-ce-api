from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.networkmanagement.models import LiveCell3G, LiveCell3GMASchema
from btsapi import app, db
import datetime
import math

mod_netmgt = Blueprint('networkmanagement', __name__, url_prefix='/api/network')


@mod_netmgt.route('/live/cells/3g', methods=['GET'], strict_slashes=False)
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