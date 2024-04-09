import os
from flask import Flask, redirect, render_template, request, Response, flash, g, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_wtf.csrf import CSRFProtect
from wtforms import form, fields, validators
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed, Permission
from flask_babelex import Babel
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.sqla import ModelView

import forms
import bcrypt
import time
import secrets
import bcrypt


from models import Producto, db, Medida
# from models import Usuarios, Insumo, Users, Proveedor, Insumo_Inventario, Pedidos_Proveedor, Merma_Inventario, Receta
from models import User, Insumo, Proveedor, Insumo_Inventario, Merma_Inventario, Receta, Medida
# from views import MermaInventarioView, Pedidos_ProveedorView, Insumo_InventarioView
from views import MermaInventarioView, Insumo_InventarioView, InsumoView, ProveedorView, RecetaView, MedidaView, ProductoView
from models import  Insumo,  Proveedor, Insumo_Inventario, Merma_Inventario, Receta, Medida,Abastecimiento,Compra,Detalle_Compra
# from views import MermaInventarioView, Pedidos_ProveedorView, Insumo_InventarioView
from views import MermaInventarioView, Insumo_InventarioView, InsumoView, ProveedorView,AbastecimientoView,CompraView
from config import DevelopmentConfig

# Create Flask application
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

csrf=CSRFProtect()

cors = CORS(app, resources={r"/*": {"origins": ["*"]}})

# load the extension
principals = Principal(app)



# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Flask views
@app.route('/')
def index():
    form = LoginForm(request.form)
    return redirect('/admin')


@app.route('/login/', methods=['POST'])
def login_vista():
    # handle user login
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        login.login_user(user)
    if login.current_user.is_authenticated:
        return redirect("/admin")
    return render_template('index.html',form=form)
    

    
# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, name='Galletos Delight', index_view=MyAdminIndexView(), base_template='my_master.html', template_mode='bootstrap4')

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))
# admin = Admin(app, name='pruebainsumos')
admin.add_view(MedidaView(Medida, db.session))
admin.add_view(InsumoView(Insumo, db.session))
admin.add_view(AbastecimientoView(Abastecimiento, db.session))
admin.add_view(CompraView(Compra,  db.session))
admin.add_view(ProveedorView(Proveedor, db.session))
# admin.add_view(MedidaView(Medida, db.session))
admin.add_view(ProductoView(Producto, db.session))
admin.add_view(Insumo_InventarioView(Insumo_Inventario, db.session, 'Inventario Insumos'))

# admin.add_view(Pedidos_ProveedorView(Pedidos_Proveedor, db.session))
admin.add_view(MermaInventarioView(Merma_Inventario, db.session, 'Merma Insumos'))
admin.add_view(RecetaView(name='Recetas', endpoint='recetas'))
# admin.add_view(ModelView(Receta, db.session))

app.config['SECRET_KEY'] = secrets.token_hex(16)
secretkey=app.config['SECRET_KEY']


if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)

