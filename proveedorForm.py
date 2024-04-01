from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField, DecimalField
from wtforms import validators
from flask_wtf.recaptcha import RecaptchaField

class ProveedorForm(Form):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=1, max=100, message='ingresa un usuario valido')
    ])
    direccion = StringField('Direccion',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=1, max=100, message='ingresa una contraseña valida')
    ])
    telefono = StringField('contraseña',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=1, max=20, message='ingresa una contraseña valida')
    ])