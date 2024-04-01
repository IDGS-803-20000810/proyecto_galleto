from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
import time
from flask_wtf.csrf import CSRFProtect
import forms
import bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed, Permission


from models import db
from models import Usuarios, Insumo, Users, Proveedor, Insumo_Inventario, Pedidos_Proveedor, Merma_Inventario, Receta
from views import MermaInventarioView, Pedidos_ProveedorView, Insumo_InventarioView

app = Flask(__name__)
from config import DevelopmentConfig
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()
import secrets
cors = CORS(app, resources={r"/*": {"origins": ["*"]}})
login_manager = LoginManager()
login_manager.init_app(app)
# load the extension
principals = Principal(app)



# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))
admin = Admin(app, name='pruebainsumos')
admin.add_view(ModelView(Insumo, db.session))
admin.add_view(ModelView(Proveedor, db.session))
admin.add_view(Insumo_InventarioView(Insumo_Inventario, db.session))
admin.add_view(Pedidos_ProveedorView(Pedidos_Proveedor, db.session))
admin.add_view(MermaInventarioView(Merma_Inventario, db.session))
admin.add_view(ModelView(Receta, db.session))




app.config['SECRET_KEY'] = secrets.token_hex(16)
secretkey=app.config['SECRET_KEY']




# load the extension
principals = Principal(app)


# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(id):
    return Users.query.get(id)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('401.html'),401

@app.errorhandler(403)
def page_not_found(e):
    session['redirected_from'] = request.url
    return render_template('403.html'),403

@app.before_request
def before_request():
    verificar_inactividad()

@app.after_request
def after_request(response):
    return response

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'permisos'):
        if current_user.permisos == 1:
            # for role in current_user.role:
            identity.provides.add(RoleNeed('admin'))
        else:
            identity.provides.add(RoleNeed('user'))



# En cada solicitud (antes de procesar la solicitud)
def verificar_inactividad():
    tiempo_actual = time.time()
    tiempo_inactivo = tiempo_actual - session.get('tiempo', tiempo_actual)
    umbral_inactividad_segundos = 60
    if tiempo_inactivo > umbral_inactividad_segundos:
        session.clear() 
        session.modified = True
        form=forms.LoginForm()
        return render_template("login.html", form=form) 
    session['tiempo'] = tiempo_actual
    return None  

def password_check(passwd):
    SpecialSym =['$', '@', '#', '%']
    val = True
    mensaje = ""
    if len(passwd) < 9:
        mensaje="la contraseña debe de tener una logitud minima de 9"
        val = False

    if not any(char.isdigit() for char in passwd):
        mensaje = "La contraseña debe de tener al menos un numero"
        val = False

    if not any(char.isupper() for char in passwd):
        mensaje = "La contraseña debe de tener al menos una mayuscula"
        val = False

    if not any(char.islower() for char in passwd):
        mensaje = "La contraseña debe de tener al menos una minuscula"
        val = False

    if not any(char in SpecialSym for char in passwd):
        mensaje = "La contraseña debe de tener al menos un caracter especial '$','@','#' "
        val = False

    return {'valido':val,'mensaje':mensaje}



@app.route("/registro", methods = ["GET","POST"])
def registro():
    mensaje = ""
    form = forms.RegistroForm(request.form)
    print(form.nombre.data)
    if request.method == "POST" and form.validate() :
        print(form.nombre.data)
        nombre = sanitizar(form.nombre.data)
        username=form.username.data
        password=form.password.data
        username = sanitizar(username)
        password = sanitizar(password)
        permisos = sanitizar(form.permisos.data)
        resCheck = password_check(password)
        
        if username in password:
            mensaje = "La contraseña no debe de contener el nombre de usuario"
            return render_template("registro.html",form=form,mensaje=mensaje)
        
        if not resCheck['valido']:
            mensaje = resCheck['mensaje']
            return render_template("registro.html",form=form,mensaje=mensaje)
        
        usu=Usuarios(nombre=nombre,username=username,password=bcrypt.hashpw( password=password.encode('utf-8'),salt=bcrypt.gensalt()),permisos=permisos)
        db.session.add(usu)
        db.session.commit()
        return redirect("/login")
    return render_template("registro.html",form=form,mensaje=mensaje)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm(request.form)
    res = ""
    if request.method == "POST":
        data = request.get_json()
        res = loginCompare(data["user"], data["password"])
        if res == "wronguser":
            return jsonify(fail=1)
        elif res == "wrongpass":
            return jsonify(fail=2)
        elif res == "success":
            return jsonify(success=1)
        elif res == "usuario con caracteres no validos '<', '>":
            return jsonify(fail=3)
    if request.method == "GET":
        return render_template("login.html", form=form)

def loginCompare(username, password):
    username = sanitizar(username)
    password = sanitizar(password)
    user = Users.query.filter_by(
                username=username).first()
    
    if "<" in user or ">" in user :
        return "usuario con caracteres no validos '<', '>'"
    
    if user is not None:
        # if user.password == password:
        if bcrypt.checkpw(password=password.encode('utf-8'),hashed_password=user.password.encode('utf-8')):
            login_user(user)
            session['tiempo'] = time.time()
            return "success"
        else:
            return "wrongpass"
    return "wronguser"

def sanitizar(palabra):
    palabra=str(palabra)
    if ";" in palabra or "delete" in palabra or "update" in palabra or "select" in palabra or "'" in palabra or '"' in palabra:
        palabra = palabra.replace(';', '')
        palabra = palabra.replace('delete', '')
        palabra = palabra.replace('update', '')
        palabra = palabra.replace('select', '')
        palabra = palabra.replace("'", '')
        palabra = palabra.replace('"', '')
    return palabra

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))




if __name__ == "__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0',debug=True)

