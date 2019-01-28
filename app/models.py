# app/models.py
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import current_app
import json
# import rq
# import redis
from time import time
from app import db, login

basedir = os.path.abspath(os.path.dirname(__file__))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role',
                            lazy='dynamic')

    def __repr__(self):
        return '<Role: {}>'.format(self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    strains = db.relationship('Strain', backref='owner')
    baskets = db.relationship('Basket', backref='owner')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String, default=None, nullable=True)
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def __repr__(self):
        return '<User: {}>'.format(self.username)


# Set up user_loader
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    customers = db.relationship('Customer', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category: {}>'.format(self.name)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    frame_id = db.Column(db.Integer, db.ForeignKey('frame.id'))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    telephone = db.Column(db.String(255))
    send_date = db.Column(db.String(255))
    temperature_id = db.Column(db.Integer, db.ForeignKey('temperature.id'))
    receive_date = db.Column(db.String(255))
    nbr_pack = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_url = db.Column(db.String(255))
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer)
    strains = db.relationship('Strain', backref='order', lazy='dynamic')

    def total_strain(self):
        number = len(self.strains.all())
        return number


class Expedition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    frame_id = db.Column(db.Integer, db.ForeignKey('frame.id'))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    telephone = db.Column(db.String(255))
    temperature_id = db.Column(db.Integer, db.ForeignKey('temperature.id'))
    expedition_date = db.Column(db.String(255))
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer)
    strains = db.relationship('Strain', backref='expedition', lazy='dynamic')

    def total_strain(self):
        number = len(self.strains.all())
        return number


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    display_as = db.Column(db.String(120))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    address = db.Column(db.String(255))
    telephone = db.Column(db.String(140), index=True, unique=True)
    email = db.Column(db.String(255), index=True, unique=True)
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    strains = db.relationship('Strain', backref='customer', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        data = {
            'id': self.id,
            'display_as': self.display_as,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'telephone': self.telephone,
            'email': self.email,
        }
        return data

    def from_dict(self, data):
        for field in ['display_as', 'first-name', 'last_name']:
            if field in data:
                setattr(self, field, data[field])


class Origin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    strains = db.relationship('Strain', backref='origin', lazy='dynamic')

    def __repr__(self):
        return '<Origin: {}>'.format(self.name)


class Frame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    strains = db.relationship('Strain', backref='frame', lazy='dynamic')
    orders = db.relationship('Order', backref='frame', lazy='dynamic')

    def __repr__(self):
        return '<Frame: {}>'.format(self.name)


# liste des souches existantes
class StrainType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    strains = db.relationship('Strain', backref='strain_type', lazy='dynamic')

    def __repr__(self):
        return '<StrainType: {}>'.format(self.name)


# liste des souches existantes
class SampleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    strains = db.relationship('Strain', backref='sample_type', lazy='dynamic')

    def __repr__(self):
        return '<SampleType: {}>'.format(self.name)


class Phenotype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(200))
    strains = db.relationship('Strain', backref='phenotype', lazy='dynamic')

    def __repr__(self):
        return '<Phenotype: {}>'.format(self.name)


strain_hole_history = db.Table(
    'strain_hole_history',
    db.Column('strain_id', db.Integer, db.ForeignKey('strain.id')),
    db.Column('hole_id', db.Integer, db.ForeignKey('hole.id'))
)


class Strain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    expedition_id = db.Column(db.Integer, db.ForeignKey('expedition.id'))
    origin_id = db.Column(db.Integer, db.ForeignKey('origin.id'))
    frame_id = db.Column(db.Integer, db.ForeignKey('frame.id'))
    strain_type_id = db.Column(db.Integer, db.ForeignKey('strain_type.id'))
    sample_type_id = db.Column(db.Integer, db.ForeignKey('sample_type.id'))
    phenotype_id = db.Column(db.Integer, db.ForeignKey('phenotype.id'))
    identity = db.Column(db.String(255), index=True)
    serial_number = db.Column(db.String(255))
    biobank_number = db.Column(db.String(255))
    mutation_type = db.Column(db.String(255))
    receive_date = db.Column(db.String)
    conservation_date = db.Column(db.String)
    status = db.Column(db.Integer)
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'))
    hole_id = db.Column(db.Integer, db.ForeignKey('hole.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('strain.id'))
    children = db.relationship("Strain", backref=db.backref('parent', remote_side=[id]))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    holes = db.relationship(
        "Hole",
        secondary=strain_hole_history,
        back_populates="strains")

    def to_json(self):
        json_strain = {
            'id': self.id,
            'customer_id': self.customer_id,
            'origin_id': self.origin_id,
            'frame_id': self.frame_id,
            'strain_type_id': self.strain_type_id,
            'strain_type_id': self.strain_type_id,
            'phenotype_id': self.phenotype_id,
            'hole_id': self.hole_id,
            'identity': self.identity,
            'serial_number': self.serial_number,
            'biobank_number': self.biobank_number,
            'mutation_type': self.mutation_type,
            'receive_date': self.receive_date,
            'conservation_date': self.conservation_date,
            'status': self.status,
            'created_at': self.created_at,
            'created_by': self.created_by
        }
        return json_strain

    def __repr__(self):
        return '<Strain: {}>'.format(self.biobank_number)


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    strains = db.relationship('Strain', backref='basket', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


# class Task(db.Model):
#     id = db.Column(db.String(36), primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     description = db.Column(db.String(128))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     complete = db.Column(db.Boolean, default=False)
#
#     def get_rq_job(self):
#         try:
#             rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
#         except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
#             return None
#         return rq_job
#
#     def get_progress(self):
#         job = self.get_rq_job()
#         return job.meta.get('progress', 0) if job is not None else 100


class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Temperature {}>'.format(self.name)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    equipments = db.relationship('Equipment', backref='room', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Room {}>'.format(self.name)

    def available(self):
        number = 0
        equipments = self.equipments
        for equipment in equipments:
            number = number + equipment.available()
        return number

    def occupied(self):
        number = 0
        equipments = self.equipments
        for equipment in equipments:
            number = number + equipment.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at
        }
        return json_post


class EquipmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    equipments = db.relationship('Equipment', backref='equipment_type', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<EquipmentType {}>'.format(self.name)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    equipment_type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'))
    name = db.Column(db.String(255))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    racks = db.relationship('Rack', backref='equipment', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Equipment {}>'.format(self.name)

    def available(self):
        number = 0
        racks = self.racks
        for rack in racks:
            number = number + rack.available()
        return number

    def occupied(self):
        number = 0
        racks = self.racks
        for rack in racks:
            number = number + rack.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'room_id': self.room_id,
            'equipment_type_id': self.equipment_type_id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class Rack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))
    name = db.Column(db.String(255))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    max_number = db.Column(db.Integer)
    status = db.Column(db.Integer)
    boxes = db.relationship('Box', backref='rack', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Rack {}>'.format(self.name)

    def available(self):
        number = 0
        boxes = self.boxes
        for boxe in boxes:
            number = number + boxe.available()
        return number

    def occupied(self):
        number = 0
        boxes = self.boxes
        for boxe in boxes:
            number = number + boxe.occupied()
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'name': self.name,
            'max_number': self.max_number,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class BoxType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    max_number = db.Column(db.Integer)
    description = db.Column(db.String(255))
    boxes = db.relationship('Box', backref='box_type', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<BoxType {}>'.format(self.name)


class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('rack.id'))
    horizontal = db.Column(db.Integer)
    vertical = db.Column(db.Integer)
    box_type_id = db.Column(db.Integer, db.ForeignKey('box_type.id'))
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)
    stores = db.relationship('Store', backref='box', lazy='dynamic')
    holes = db.relationship('Hole', backref='box', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<box {}>'.format(self.name)

    def available(self):
        number = 0
        holes = self.holes
        for hole in holes:
            if hole.status == 0:
                number = number + 1
        return number

    def occupied(self):
        number = 0
        holes = self.holes
        for hole in holes:
            if hole.status == 1:
                number = number + 1
        return number

    def to_json(self):
        json_post = {
            'id': self.id,
            'rack_id': self.rack_id,
            'box_type_id': self.box_type_id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by,
            'holes_count': self.holes.count(),
            'free_holes': self.holes.filter_by(status=0).count(),
            'used_holes': self.holes.filter_by(status=1).count()
        }
        return json_post


class Hole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'))
    strain_id = db.Column(db.Integer, db.ForeignKey('strain.id'))
    name = db.Column(db.String(255))
    status = db.Column(db.Integer)
    store_items = db.relationship('StoreItem', backref='hole', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    strains = db.relationship(
        "Strain",
        secondary=strain_hole_history,
        back_populates="holes")

    def __repr__(self):
        return '<Hole {}>'.format(self.name)

    def is_available(self):
        return self.status == 0

    def to_json(self):
        json_post = {
            'id': self.id,
            'box_id': self.box_id,
            'strain_id': self.strain_id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at,
            'author': self.created_by
        }
        return json_post


class LocationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_type = db.Column(db.String(255))
    old_location = db.Column(db.String(255))
    new_location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<LocationHistory {}>'.format(self.name)


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(255), index=True)
    box_id = db.Column(db.Integer, db.ForeignKey('box.id'))
    status = db.Column(db.Integer)
    store_items = db.relationship('StoreItem', backref='store', lazy='dynamic')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class StoreItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    strain_id = db.Column(db.Integer, db.ForeignKey('strain.id'))
    hole_id = db.Column(db.Integer, db.ForeignKey('hole.id'))
    status = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


# 1 - pushing(aliquot), 2 pulling
class Technique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    category = db.Column(db.Integer, default=1)
    out_number = db.Column(db.Integer, default=0)
    in_number = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255))
    processes = db.relationship('Process', backref='technique', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Technique {}>'.format(self.name)


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    technique_id = db.Column(db.Integer, db.ForeignKey('technique.id'))
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Process {}>'.format(self.name)


class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    volume = db.Column(db.String(120))
    description = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    aliquots = db.relationship('Aliquot', backref='support', lazy='dynamic')


class Mesure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    siggle = db.Column(db.String(120))
    description = db.Column(db.String(128))
    aliquots = db.relationship('Aliquot', backref='mesure', lazy='dynamic')


class Aliquot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(255), index=True)
    strain_id = db.Column(db.Integer, db.ForeignKey('strain.id'))
    support_id = db.Column(db.Integer, db.ForeignKey('support.id'))
    volume = db.Column(db.Integer)
    mesure_id = db.Column(db.Integer, db.ForeignKey('mesure.id'))
    status = db.Column(db.Integer)
    aliquot_items = db.relationship('AliquotItem', backref='aliquot', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Aliquot {}>'.format(self.serial)

    def nbr_aliquot(self):
        number = len(self.aliquot_items.all())
        return int(number)


class AliquotItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aliquot_id = db.Column(db.Integer, db.ForeignKey('aliquot.id'))
    serial = db.Column(db.String(255), index=True)
    volume = db.Column(db.Integer)
    status = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    prints = db.relationship('Print', backref='label', lazy='dynamic')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))


class Print(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(255), index=True)
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'))
    status = db.Column(db.Integer)
    print_items = db.relationship('PrintItem', backref='print', lazy='dynamic')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class PrintItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    print_id = db.Column(db.Integer, db.ForeignKey('print.id'))
    strain_id = db.Column(db.Integer, db.ForeignKey('strain.id'))
    status = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Seed:
    @staticmethod
    def start():
        level_list = []

        for lvl in level_list:
            db.session.add(lvl)
        db.session.commit()
