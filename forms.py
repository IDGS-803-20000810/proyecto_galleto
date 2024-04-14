import wtforms
from wtforms import (
    HiddenField,
    StringField,
    SelectField,
    RadioField,
    EmailField,
    IntegerField,
    PasswordField,
    DecimalField,
)
from wtforms import Form
from wtforms import validators
from flask_wtf.recaptcha import RecaptchaField


class LoginForm(Form):
    username = StringField(
        "usuario",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=20, message="ingresa un usuario valido"),
        ],
    )
    password = PasswordField(
        "contraseña",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=20, message="ingresa una contraseña valida"),
        ],
    )
    recaptcha = RecaptchaField()


class RegistroForm(Form):
    nombre = StringField(
        "nombre",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=50, message="ingresa un nombre válido"),
        ],
    )
    username = StringField(
        "usuario",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=20, message="ingresa un usuario valido"),
        ],
    )
    password = PasswordField(
        "contraseña",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=20, message="ingresa una contraseña valida"),
        ],
    )
    permisos = SelectField(
        "Selecciona el nivel de permisos",
        choices=[(0, "Usuario"), (1, "Administrador")],
    )
    recaptcha = RecaptchaField()


class ProductoForm(Form):
    nombre = StringField(
        "nombre",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.length(min=3, max=20, message="ingresa un usuario valido"),
        ],
    )
    precio = DecimalField(
        "precio",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.number_range(min=0.1, max=99999999, message="valor no valido"),
        ],
    )
    stock = IntegerField(
        "stock",
        [
            validators.DataRequired(message="el campo es requerido"),
            validators.number_range(min=1, max=9999999999, message="valor no valido"),
        ],
    )
    id = IntegerField("id")

class RecetaForm(Form):
    nombre = StringField(
        "Nombre",
        [
            validators.DataRequired(message="El campo es requerido"),
            validators.length(min=1, max=100, message="Se Requiere un nombre valido"),
        ],
    )
    descripcion = StringField(
        "Descripcion",
        [
            validators.DataRequired(message="Una descripcion es requerida"),
            validators.length(min=1, max=255, message="valor no valido"),
        ],
    )
    producto = SelectField(
        "Producto",
        [
            validators.DataRequired(message="Este campo es requerido"),
        ],
    )
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, message="ingresa un usuario valido"),
        ],
        default=1
    )

class IngredientesRecetaForm(Form):
    insumo = SelectField(
        "Insumo",
        [
            validators.DataRequired(message="Este campo es requerido"),
        ],
    )
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, message="ingresa un usuario valido"),
        ],
        default=1
    )

class ProduccionForm(Form):
    receta = SelectField(
        "Receta",
        [
            validators.DataRequired(message="Este campo es requerido"),
        ],
    )
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, message="ingresa un usuario valido"),
        ],
        default=1
    )

class MermaProductoForm(Form):
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, message="ingresa una cantidad valido"),
        ],
        default=1
    )
    descripcion = StringField(
        "Descripción",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, ),
        ],
    )
    producto_inventario = HiddenField(
        "Presentacion",
        [
            validators.DataRequired(message="Se requiere este campo"),
        ],
        default=1
    )

    def __init__(self, *args, **kwargs):
        super(MermaProductoForm, self).__init__(*args, **kwargs)
        self.cantidad.validators[1] = validators.length(min=1)

class DetalleVentaForm(Form):
    cantidad = IntegerField(
        "Cantidad",
        [
            validators.DataRequired(message="Se requiere este campo"),
            validators.length(min=1, message="ingresa una cantidad valido"),
        ],
        default=1
    )
    presentacion_id = HiddenField(
        "presentacion_id",
        [
            validators.DataRequired(message="Se requiere este campo"),
        ],
        default=1
    )
