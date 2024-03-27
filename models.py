from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db=SQLAlchemy()

class Usuarios(db.Model):
    _tablename_='usuarios'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(250))
    permisos=db.Column(db.Integer)
    
class Productos(db.Model):
    _tablename_='productos'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    precio=db.Column(db.Double)
    stock=db.Column(db.Integer)
    
class Proveedor(db.Model):
    _tablename_='proveedores'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(255))
    direccion=db.Column(db.String(255))
    telefono=db.Column(db.String(25))

class Users(UserMixin, Usuarios): ...