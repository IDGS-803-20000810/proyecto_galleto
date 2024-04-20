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
from wtforms.csrf.session import SessionCSRF
from flask_admin.form import SecureForm
from flask_socketio import SocketIO, emit
from listas import Listas

import forms
import bcrypt
import time
import secrets
import bcrypt

from models import Merma_Producto, Presentacion, Produccion, Producto, Producto_Inventario, Venta, db, Medida
# from models import Usuarios, Insumo, Users, Proveedor, Insumo_Inventario, Pedidos_Proveedor, Merma_Inventario, Receta
from models import User, Insumo, Proveedor, Insumo_Inventario, Merma_Inventario, Receta, Medida
# from views import MermaInventarioView, Pedidos_ProveedorView, Insumo_InventarioView
from views import AdminRecetaView, MermaInventarioView, Insumo_InventarioView, InsumoView, MermaProductoView, PresentacionView, ProduccionCocinaView, Producto_InventarioView, ProveedorView, MedidaView, ProductoView, VentaPrincipalView, VentaView
from models import  Insumo, User, Proveedor, Insumo_Inventario, Merma_Inventario, Receta, Medida,Abastecimiento,Compra,SolicitudesProduccion
# from views import MermaInventarioView, Pedidos_ProveedorView, Insumo_InventarioView
from views import MermaInventarioView, Insumo_InventarioView, InsumoView, ProveedorView,AbastecimientoView,CompraView, UserView
from config import DevelopmentConfig, Config
from datetime import datetime
from customValidators import  agregarLog, password_check, user_check

# Create Flask application
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
socketio = SocketIO(app)
csrf=CSRFProtect()
cors = CORS(app, resources={r"/*": {"origins": ["*"]}})

# load the extension

#Iniciar traduccion
babel = Babel(app)

@babel.localeselector
def get_locale():
        return 'es'

class MyBaseForm(form.Form):
    class Meta:
        csrf = True 
        csrf_class = SessionCSRF  
        csrf_secret = Config.SECRET_KEY

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(403)
def page_not_found(e):
    session['redirected_from'] = request.url
    return render_template('403.html'),403

@socketio.on('connect')
def handle_connect():
    print('Usuario conectado')

@socketio.on('send_message')
def handle_send_message(msg):
    splitedmsg = msg.split("|")
    id = splitedmsg[0]
    cantidad = splitedmsg[1]
    solicitud = SolicitudesProduccion(producto_id=id,cantidad_solicitada=cantidad)
    db.session.add(solicitud)
    db.session.commit()
    print('mensaje : ' + msg )

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Agregar necesidades (Needs) al usuario actual
    if hasattr(login.current_user, 'id'):
        identity.user = login.current_user
        identity.provides.add(UserNeed(login.current_user.id))
        identity.provides.add(RoleNeed(login.current_user.role))


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired(),validators.Length(1,255)])
    password = fields.PasswordField(validators=[validators.InputRequired(),validators.Length(1,255)])
    def validate_login(self, field):

        print("login")
        if session.get('intentos') is None:
            print("3 intentos")

            session['intentos'] = 3

        user = self.get_user()

        if user is None:
            agregarLog("Inicio de sesión no exitoso por usuario incorrecto, usuario: " + self.login.data + ". Contraseña : " + self.password.data)  
            raise validators.StopValidation('Usuario inválido')

        if user.bloqueado==1:
            raise validators.StopValidation('Usuario bloqueado por exceso de intentos')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            agregarLog("Inicio de sesión no exitoso por contraseña incorrecta, usuario: " + self.login.data + ". Contraseña : " + self.password.data)         
            raise validators.StopValidation('Contraseña inválida')
        
        if session.get('intentos') is not None:
            print("not none")
            if session['intentos'] == 0:

                print("session['intentos']")
                print(session['intentos'])
                
                usrBloquear = db.session.query(User).filter_by(login=self.login.data).first()
                
                if usrBloquear:
                    usrBloquear.bloqueado = 1
                    db.session.add(usrBloquear)
                    db.session.commit()
                    session['intentos'] = 3

                raise validators.StopValidation('Usuario inválido')
            
            else:
                valor = session['intentos']
                valor = valor - 1
                session['intentos'] = valor
        
    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()

class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.InputRequired()])
    #role = fields.SelectField(
    #    "Selecciona el rol del usuario",
    #    choices=[("cuck", "Cocinero"), ("admin", "Administrador"),("ventas", "Vendedor"),("almacen", "Almacenista")],
    #)
    
    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Usuario duplicado')

        check = password_check(self.password.data)
        if not check['valido']:
            raise validators.ValidationError(check['mensaje'])

        check = user_check(self.login.data)
        if not check['valido']:
            raise validators.ValidationError(check['mensaje'])


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
    form_base_class = SecureForm

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
            if login.login_user(user):
                agregarLog("Inicio de sesión exitoso, usuario: " + form.login.data + ". Contraseña : " + form.password.data)   
            else:
                agregarLog("Inicio de sesión no exitoso, usuario: " + form.login.data + ". Contraseña : " + form.password.data)         
        if login.current_user.is_authenticated:
            userToUpdate = User.query.filter_by(id = user.id).first()
            userToUpdate.prevLogin = userToUpdate.lastLogin
            userToUpdate.lastLogin = datetime.now()
            db.session.add(userToUpdate)
            db.session.commit()
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? Bad for you</p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).render("login.html",form=form)
    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))
    form_base_class = SecureForm

# Flask views
@app.route('/')
def index():
    return redirect('/admin')

init_login()

admin = admin.Admin(app, name='Galletos Delight', index_view=MyAdminIndexView(), base_template='my_master.html', template_mode='bootstrap4')


admin.add_view(MedidaView(Medida, db.session,category="Insumos"))
admin.add_view(InsumoView(Insumo, db.session, category="Insumos"))
admin.add_view(AbastecimientoView(Abastecimiento, db.session, category="Almacen"))
admin.add_view(ProveedorView(Proveedor, db.session, category="Almacen"))
admin.add_view(CompraView(Compra,  db.session, category="Almacen"))
admin.add_view(AdminRecetaView(Receta,  db.session,"Recetas", category="Cocina"))
admin.add_view(ProductoView(Producto, db.session, category="Productos"))
admin.add_view(MermaProductoView(Merma_Producto, db.session, 'Merma Productos', category="Productos"))
admin.add_view(Insumo_InventarioView(Insumo_Inventario, db.session, 'Inventario Insumos', category="Cocina"))
admin.add_view(Producto_InventarioView(Producto_Inventario, db.session,'Inventario de Productos', category="Productos"))
admin.add_view(MermaInventarioView(Merma_Inventario, db.session, 'Merma Insumos', category="Cocina"))
admin.add_view(ProduccionCocinaView(name='Produccion', endpoint='produccion_cocina', category="Cocina"))
admin.add_view(PresentacionView(Presentacion,db.session,'Presentaciones', category="Ventas"))
admin.add_view(VentaPrincipalView(name='Ventas - Frente', endpoint='ventas_frente', category="Ventas"))
admin.add_view(VentaView(Venta, db.session,"Historial de ventas", category="Ventas"))
admin.add_view(UserView(User,db.session,'Usuarios', category="Amdministración del sistema"))

app.config['SECRET_KEY'] = secrets.token_hex(16)
secretkey=app.config['SECRET_KEY']


if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    socketio.run(app,host='0.0.0.0',debug=True)
    app.run(host='0.0.0.0',debug=True)

