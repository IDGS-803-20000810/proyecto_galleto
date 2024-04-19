from wtforms.validators import ValidationError
from datetime import datetime
from listas import Listas
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
