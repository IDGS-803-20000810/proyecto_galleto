from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify,Blueprint
from jinja2 import TemplateNotFound
from proveedorForm import ProveedorForm
from models import Proveedor
from models import db


proveedores = Blueprint('proveedores', __name__, template_folder = 'templates')

@proveedores.route('/proveedores')
def showProveedores():
    form = ProveedorForm(request.form)
    prov = db.session.query(Proveedor).all()
    return render_template('proveedores.html',form=form, proveedores=prov)