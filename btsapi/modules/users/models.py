from flask_sqlalchemy import SQLAlchemy
from btsapi import db, ma;
import datetime

class User(db.Model):
    """Users model"""

    __tablename__ = 'users'

    pk = db.Column(db.Integer, db.Sequence('seq_users_pk', ), primary_key=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    other_names = db.Column(db.String(255))
    job_title = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    photo = db.Column(db.Text)
    token = db.Column(db.String(255))
    is_account_non_expired = db.Column(db.Boolean, default=True)
    is_account_non_locked = db.Column(db.Boolean, default=True)
    is_enabled = db.Column(db.Boolean, default=True)


class UserSchema(ma.ModelSchema):
    """Flask Marshmallow Schema for Vendor model"""

    class Meta:
        model = User
        fields = ('pk','username','password','first_name','last_name','other_names','job_title','phone_number','photo')