from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField, DecimalField
from wtforms import validators
from flask_wtf.recaptcha import RecaptchaField

class LoginForm(Form):
    username = StringField('usuario', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa un usuario valido')
    ])
    password = PasswordField('contraseña',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa una contraseña valida')
    ])
    recaptcha = RecaptchaField()


class RegistroForm(Form):
    nombre = StringField('nombre', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=50, message='ingresa un nombre válido')
    ])
    username = StringField('usuario', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa un usuario valido')
    ])
    password = PasswordField('contraseña',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa una contraseña valida')
    ])
    permisos = SelectField(u'Selecciona el nivel de permisos', choices=[(0, 'Usuario'), (1, 'Administrador')])
    recaptcha = RecaptchaField()


class ProductoForm(Form):
    nombre = StringField('nombre', [
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=3, max=20, message='ingresa un usuario valido')
    ])
    precio = DecimalField('precio', [
        validators.DataRequired(message='el campo es requerido'),
       validators.number_range(min=0.1, max=99999999, message='valor no valido')
    ])
    stock =  IntegerField('stock', [
        validators.DataRequired(message='el campo es requerido'),
       validators.number_range(min=1, max=9999999999, message='valor no valido')
    ])
    id=IntegerField('id')
