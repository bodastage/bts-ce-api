from flask_sqlalchemy import SQLAlchemy
from btsapi.extensions import  db, ma
import datetime
from sqlalchemy import Table, MetaData
import marshmallow

metadata = MetaData()

#
# class Setting(db.Model):
#     """Settings model"""
#     __table__ = Table('settings', metadata, autoload=True, autoload_with=db.engine, schema='public')
#     pass


class CMFileFormats(db.Model):
    """
    CM file formats model
    """

    __tablename__ = 'cm_file_formats'

    pk = db.Column(db.Integer,  db.Sequence('seq_cm_file_formats_pk',), primary_key=True, nullable=False )
    name = db.Column(db.String(100), unique=True, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    vendor_pk = db.Column(db.Integer, nullable=False)
    tech_pk = db.Column(db.Integer, nullable=False)
    modified_by = db.Column(db.Integer)
    added_by = db.Column(db.Integer)
    date_added = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

class Setting(db.Model):
    """Settings model"""

    __tablename__ = 'settings'

    pk = db.Column(db.Integer,  db.Sequence('seq_settings_pk',), primary_key=True, nullable=False )
    name = db.Column(db.String(200), unique=True, nullable=False)
    data_type = db.Column(db.String(200), nullable=False)
    integer_value = db.Column(db.Integer)
    float_value = db.Column(db.Float)
    string_value = db.Column(db.String(200))
    text_value = db.Column(db.Text)
    timestamp_value = db.Column(db.TIMESTAMP)
    label = db.Column(db.String(200))
    category_id = db.Column(db.String(200))


class SettingMASchema(ma.ModelSchema):
    """Settings marshmallow schema"""
    value = marshmallow.fields.Method("get_actual_value")
    id = marshmallow.fields.Method("get_id")

    def get_id(self,model):
        return model.pk

    def get_actual_value(self,model):
        """Return a single value from the settings table for each setting"""
        if model.data_type == 'string': return model.string_value
        if model.data_type == 'integer': return model.integer_value
        if model.data_type == 'float' or model.data_type == 'double' : return model.float_value
        if model.data_type == 'long_string': return model.long_string_value
        if model.data_type == 'timestamp': return model.timestamp_value
        if model.data_type == 'text': return model.text_value
        return model.string_value

    class Meta:
        model = Setting
        fields = ('id','name', 'label', 'value', 'category_id')


class SupportedVendorTech(db.Model):
    """
    Supported vendor technologies model
    """
    __tablename__ = 'supported_vendor_tech'

    pk = db.Column(db.Integer, db.Sequence('seq_supported_vendor_tech_pk', ), primary_key=True, nullable=False)
    vendor_pk = db.Column(db.Integer, nullable=False)
    tech_pk = db.Column(db.Integer, nullable=False)
    modified_by = db.Column(db.Integer)
    added_by = db.Column(db.Integer)
    date_added = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('vendor_pk', 'tech_pk', name='unq_supported_vendor_tech'),
                      )

    def init(self, vendor_pk, tech_pk):
        self.tech_pk = tech_pk
        self.vendor_pk = vendor_pk


class CMFileFormatsMASchema(ma.ModelSchema):
    """CM File Format marshmallow schema"""
    class Meta:
        model = CMFileFormats