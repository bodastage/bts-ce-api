# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.vendors.models import Vendor, VendorSchema
from btsapi import app

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_vendors = Blueprint('vendors', __name__, url_prefix='/api/vendors')


# Set the route and accepted methods
@mod_vendors.route('/', methods=['GET'])
def get_vendors():
    """Get a list of all the vendors in the system"""

    vendor_schema = VendorSchema()

    return jsonify( [vendor_schema.dump(v).data for v in Vendor.query.all()] )


@mod_vendors.route('/<int:id>', methods=['GET'])
def get_vendor(id):
    """Get vendor details"""

    vendor_schema = VendorSchema()

    return jsonify(vendor_schema.dump(Vendor.query.get(id)).data)


@mod_vendors.route('/<int:id>', methods=['PUT'])
def update_vendor():
    """Update vendor details"""
    pass


@mod_vendors.route('/<int:id>', methods=['DELETE'])
def delete_vendor():
    """Delete vendor"""
    pass

@mod_vendors.route('/', methods=['POST'])
def add_vendor():
    """Add a vendor"""
    pass