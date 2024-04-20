from wtforms.validators import ValidationError
from datetime import datetime
from listas import Listas
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func
from flask import flash
from models import db
from flask_admin.actions import action

def not_null(form, field):
    print(field)
    if field.data == None:
        print("igual ptm")
        raise ValidationError('Debe seleccionar un elemento')  
    else:
        print("ptm")  

def min_allowed(form, field):
    if field.data == None:
        raise ValidationError('Debe seleccionar un elemento')    
    if len(str(field.data)) < 0:
        raise ValidationError('Debe introducir un valor')      
    
def phonelenght(form, field):
    print(field)
    if len(str(field.data)) != 10:
        print("igual ptm")
        raise ValidationError('Debe introducir un número de teléfono con 10 dígitos')  
    else:
        print("ptm")  

def agregarLog(texto):
    archivo_texto=open('logs.txt','a')
    archivo_texto.write('\n ' + texto + ". hora: " + str(datetime.now()))
    archivo_texto.close()

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
        
    for psw in Listas.contraseñas_comunes:
        if passwd == psw:
            mensaje = "Se detectó una contraseña insegura"
            val = False
            
    return {'valido':val,'mensaje':mensaje}

def user_check(user):
    val = True
    mensaje = ""
    
    for usr in Listas.usuarios_comunes:
        if usr == user:
            mensaje = "Se detectó un usuario inseguro"
            val = False
            
    return {'valido':val,'mensaje':mensaje}

def format_date(view, context, model, name):
    date_obj = model.fecha
    
    # Diccionario para traducir meses de inglés a español
    months_translation = {
        'January': 'Enero',
        'February': 'Febrero',
        'March': 'Marzo',
        'April': 'Abril',
        'May': 'Mayo',
        'June': 'Junio',
        'July': 'Julio',
        'August': 'Agosto',
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre',
        'December': 'Diciembre'
    }
    
    # Comprobamos si date_obj es una cadena
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
    
    # Ahora date_obj debería ser un objeto datetime
    formatted_date = date_obj.strftime('%d-%B-%Y')
    
    # Traducimos el nombre del mes
    for english_month, spanish_month in months_translation.items():
        formatted_date = formatted_date.replace(english_month, spanish_month)
    
    return formatted_date


class EstatusModelView(ModelView):

    def delete_model(self, model):
        try:
            model.estatus = False
            db.session.add(model)
            db.session.commit()
        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash('Error al cambiar el estatus. Detalles: {}'.format(str(e)), 'error')
            return False
        return True

    def get_query(self):
        # Filtramos los registros según el valor de estatus sea verdadero
        return self.session.query(self.model).filter_by(estatus=True)
    
    def get_count_query(self):
        # Filtramos los conteos de registros para la paginación
        return self.session.query(func.count(self.model.id)).filter_by(estatus=True)

    @action('delete', 'Eliminar', '¿Estás seguro de que deseas cambiar el estatus a falso para este registro?')
    def action_delete(self, ids):
        try:
            for model_id in ids:
                model = self.get_one(model_id)
                if model:
                    model.estatus = False
                    db.session.add(model)
                    db.session.commit()
        except Exception as e:
            flash(str(e), 'error')
        else:
            flash('El estatus ha sido cambiado a falso para los registros seleccionados.', 'success')

def get_limited_choices(Clase):
    # Filtra las medidas con estatus=True
    return Clase.query.filter_by(estatus=True).all()