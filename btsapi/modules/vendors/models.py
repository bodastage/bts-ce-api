from flask_sqlalchemy import SQLAlchemy
from btsapi.common.model_helpers import dump_datetime;
from btsapi import db, ma;


class Vendor(db.Model):
    """Vendors model"""

    __tablename__ = 'vendors'

    pk = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    notes = db.Column(db.Text)
    modified_by = db.Column(db.Integer)
    added_by = db.Column(db.Integer)
    date_added = db.Column(db.TIMESTAMP)
    date_modified = db.Column(db.TIMESTAMP)


class VendorSchema(ma.ModelSchema):
    """Flask Marshmallow Schema for Vendor model"""
    class Meta:
        model = Vendor
