from flask_sqlalchemy import SQLAlchemy
from btsapi.extensions import db, ma
import datetime
from sqlalchemy import Table, MetaData, inspect
from sqlalchemy.dialects import postgresql

metadata = MetaData()


class Report(db.Model):
    # __table__ = Table('reports', metadata, autoload=True, autoload_with=db.engine, schema='public')
    __tablename__ = 'reports'
    __table_args__ = {'schema': 'reports'}

    pk = db.Column(db.Integer, db.Sequence('seq_reports_pk', schema='reports'), primary_key=True, nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    notes = db.Column('notes', db.Text)
    query = db.Column(db.Text)
    db_connector_pk = db.Column('db_connector_pk', db.Integer)
    options = db.Column('options', postgresql.JSON)  # JSON
    category_pk = db.Column('category_pk', db.Integer)
    modified_by = db.Column(db.Integer)
    added_by = db.Column(db.Integer)
    date_added = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)


class ReportCategory(db.Model):
    __tablename__ = 'report_categories'
    __table_args__ = {'schema': 'reports'}

    pk = db.Column(db.Integer, db.Sequence('seq_report_categories_pk', schema='reports'), primary_key=True, nullable=False)
    name = db.Column('name', db.String(100), nullable=False)
    notes = db.Column('notes', db.Text)
    parent_pk = db.Column('parent_pk', db.Integer)
    modified_by = db.Column(db.Integer)
    added_by = db.Column(db.Integer)
    date_added = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)


class ReportsTaskLog(db.Model):
    __tablename__ = 'reports_task_log'
    __table_args__= {'schema': 'reports'}

    pk = db.Column(db.Integer, db.Sequence('seq_reports_task_log_pk', schema='reports'), primary_key=True, nullable=False)
    action = db.Column('action', db.String(200), nullable=False)  # reports.generate
    log = db.Column('log', db.Text)
    options = db.Column('options', postgresql.JSON)
    status = db.Column('status', db.String(200))  # FAILED,RUNNING,PENDING,STARTED,FINISHED
    modified_by = db.Column(db.Integer, default=0)
    added_by = db.Column(db.Integer, default=0)
    date_added = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    date_modified = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)


class ReportMASchema(ma.ModelSchema):
    class Meta:
        model = Report
        fields = ('name', 'notes', 'category_id','id', 'query', 'options')

    id = ma.Integer(attribute="pk")
    category_id = ma.Integer(attribute="category_pk")

class ReportCategoryMASchema(ma.ModelSchema):
    class Meta:
        model = ReportCategory


class DummyTable(db.Model):
    __tablename__ = 'dummy_table'
    dummy_pk = db.Column(db.Integer, db.Sequence('seq_dummy_table_pk', ), primary_key=True, nullable=False)