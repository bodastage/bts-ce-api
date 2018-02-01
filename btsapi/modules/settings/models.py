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
