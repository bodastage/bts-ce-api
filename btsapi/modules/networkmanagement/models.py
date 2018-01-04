from flask_sqlalchemy import SQLAlchemy
from btsapi import db, ma
import datetime
from sqlalchemy import Table, MetaData, inspect
from sqlalchemy.orm import class_mapper, mapper


metadata = MetaData()

class LiveCell3G(db.Model):
    """Create live network UMTS cells data model"""
    __table__ = Table('umts_cells_data', metadata, autoload=True, autoload_with=db.engine, schema='live_network')
    pass


class LiveCell3GMASchema(ma.ModelSchema):
    """Live network UMTS cells marshmallow model"""
    class Meta:
        model = LiveCell3G
