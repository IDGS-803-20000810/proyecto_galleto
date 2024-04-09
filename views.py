from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin.model.template import macro
from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify
from models import Ingredientes_Receta, Insumo, Insumo_Inventario, Producto, Proveedor, Receta, Medida
from models import db
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from wtforms.validators import Length
from flask_sqlalchemy import SQLAlchemy
from forms import RecetaForm, IngredientesRecetaForm
from models import Proveedor, Insumo, Insumo_Inventario,Abastecimiento, Compra,Detalle_Compra
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField, DecimalField
from wtforms import validators
from wtforms.validators import ValidationError, DataRequired, NumberRange
import flask_login as login
from datetime import date
from flask_admin.model import typefmt

# db=SQLAlchemy()

class MermaInventarioView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated
    column_list = [ 'cantidad', 'insumo_inventario', 'descripcion']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad', 'descripcion']  # Campos editables en la lista
    form_columns = ['cantidad', 'medida', 'insumo_inventario', 'descripcion']  # Campos a mostrar en el formulario de edición
    form_extra_fields = {
        'medida': SelectField( choices=[(0, 'Gramos'), (1, 'KG')])
    }
    def on_model_change(self, form, model, is_created):
        if int(model.medida) == 1:
            model.cantidad = model.cantidad * 1000
        if is_created:
            print(model.medida)
            print(model.medida)
            print(model.medida)
            insumo = Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).first()
            if insumo:
                nCantidad = int(insumo.cantidad) - int(model.cantidad)
                print(nCantidad)
                print(nCantidad)
                print(nCantidad)
                Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).update({"cantidad": nCantidad})
                db.session.commit()

# class Pedidos_ProveedorView(ModelView):
#     column_auto_select_related = True
#     column_list = ['cantidad', 'precioActual', 'periodicidad', 'proveedor', 'insumo' ]  # Campos a mostrar en la lista
#     column_editable_list = ['cantidad', 'precioActual', 'periodicidad']  # Campos editables en la lista
#     form_columns = ['cantidad', 'medida', 'precioActual', 'periodicidad', 'proveedor', 'insumo' ]  # Campos a mostrar en el formulario de edición
#     form_extra_fields = {
#         'medida': SelectField( choices=[(0, 'KG'), (1, 'Gramos')])
#     }
#     def on_model_change(self, form, model, is_created):
#         if is_created:
#             if int(model.medida) == 0:
#                 model.cantidad = model.cantidad * 1000
#                 Pedidos_Proveedor.query.filter_by(
#                 id=model.id).update({"cantidad": model.cantidad})
#                 db.session.commit()

class Insumo_InventarioView(ModelView):
    column_auto_select_related = True
    def is_accessible(self):
        return login.current_user.is_authenticated
    column_list = ['cantidad', 'insumo' ]  # Campos a mostrar en la lista
    column_editable_list = ['cantidad',  'insumo'] # Campos editables en la lista
    form_columns = ['cantidad','medida',  'insumo']  # Campos a mostrar en el formulario de edición
    form_extra_fields = {
        'medida': SelectField( choices=[(0, 'KG'), (1, 'Gramos')])
    }
    def on_model_change(self, form, model, is_created):
        if is_created:
            if int(model.medida) == 0:
                print(model.medida)
                print(model.medida)
                print(model.medida)
                model.cantidad = model.cantidad * 1000
                Insumo_Inventario.query.filter_by(
                id=model.id).update({"cantidad": model.cantidad})
                db.session.commit()

# class RecetaView(ModelView):
#     column_auto_select_related = True
#     form_columns = ['nombre','descripcion', 'insumo', 'proveedor' ]  # Campos a mostrar en el formulario de edición
def phonelenght(form, field):
    print(field)
    if len(str(field.data)) != 10:
        print("igual ptm")
        raise ValidationError('Debe introducir un número de teléfono con 10 dígitos')  
    else:
        print("ptm")  
class ProveedorView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','direccion', 'telefono']  # Campos a mostrar en el formulario de edición
    form_args = dict(
        nombre=dict( validators=[DataRequired(message="pon algo we"), Length(min=3, max=30)]),
        direccion=dict(validators=[DataRequired(message="pon algo we"), Length(min=7, max=30)]),
        telefono=dict(validators=[DataRequired(message="pon algo we"), phonelenght])
    )
    def is_accessible(self):
        return login.current_user.is_authenticated

class ProductoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','peso']  # Campos a mostrar en el formulario de edición
    def is_accessible(self):
        return login.current_user.is_authenticated




class RecetaView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated
    
    @expose('/')
    def viewReceta(self):
        session["detalle"] = []
        recetas = Receta.query.all()
        
        return self.render('recetas.html',recetas=recetas)
    
    @expose('/eliminarReceta',methods=['GET'])
    def deleteReceta(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
        session["detalle"] = []

        id = request.args.get("id")
        receta = db.session.query(Receta).filter(Receta.id == id).first()
        db.session.delete(receta)
        db.session.commit()
        
        recetas = Receta.query.all()
        return self.render('recetas.html',recetas=recetas)
    
    @expose('/addReceta', methods=['POST','GET'])
    def addReceta(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
        if 'detalle' not in session.keys():
            session['detalle'] = []

        ingsRecetaForm = IngredientesRecetaForm(request.form)
        recetaForm = RecetaForm(request.form)
        insumos = Insumo.query.all()
        productos = Producto.query.all()
        
        lista_insumos = []

        for i in insumos:
            medida = Medida.query.filter(Medida.id == i.medida_id).first()
            lista_insumos.append((i.id, i.nombre+" - "+medida.medida))

        
        lista_productos = [(i.id, i.nombre) for i in productos]
        ingsRecetaForm.insumo.choices = lista_insumos
        recetaForm.producto.choices = lista_productos

        detalle = session["detalle"]
        
        if request.method == "GET":

            session['accion'] = request.args.get("accion")

            if session['accion'] == 'modificar':

                #MODIFICAR

                id = request.args.get("id")
                session['id'] = id
                receta = db.session.query(Receta).filter(Receta.id == id).first()

                recetaForm.nombre.data = receta.nombre
                recetaForm.descripcion.data = receta.descripcion
                recetaForm.producto.data = receta.producto_id
                recetaForm.cantidad.data = receta.cantidad_producto

                ingsReceta = db.session.query(Ingredientes_Receta).filter(Ingredientes_Receta.receta_id == id).all()

                detalle = []

                for item in ingsReceta:

                    insumo = Insumo.query.filter(Insumo.id == item.insumo_id).first()

                    detalle.append({
                    "id": item.insumo_id,
                    "nombre": insumo.nombre,
                    "cantidad": item.cantidad,
                    })

                session['detalle'] = detalle

                #MODIFICAR

            return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = detalle,mensajes=[])        
        if request.method == "POST":

            nombre = recetaForm.nombre.data
            descripcion = recetaForm.descripcion.data
            producto = int(recetaForm.producto.data)
            cantidad = int(recetaForm.cantidad.data)

            if session['accion'] == 'crear':
            # CREAR

                receta = Receta(nombre=nombre,descripcion=descripcion,producto_id=producto,cantidad_producto=cantidad)

                db.session.add(receta)
                db.session.commit()

                db.session.refresh(receta)
                
                for det in detalle:
                    ings = Ingredientes_Receta(cantidad=det['cantidad'],insumo_id=det['id'],receta_id=receta.id)
                    db.session.add(ings)
                    db.session.commit()

            else:

                # MODIFICAR

                receta = Receta.query.filter(Receta.id == session['id']).first()

                receta.nombre = nombre
                receta.descripcion = descripcion
                receta.producto_id = producto
                receta.cantidad = cantidad

                #Eliminar ingredientes para insertar los nuevos 
                Ingredientes_Receta.query.filter(Ingredientes_Receta.receta_id == session['id']).delete()
                
                db.session.add(receta)
                db.session.commit()
                
                for det in detalle:
                    ings = Ingredientes_Receta(cantidad=det['cantidad'],insumo_id=det['id'],receta_id=receta.id)
                    db.session.add(ings)
                    db.session.commit()
                
        recetas = Receta.query.all()
        return self.render('recetas.html',recetas=recetas)  
    
    @expose('/añadirDetalle', methods=['POST'])
    def addDetalle(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
        ingsRecetaForm = IngredientesRecetaForm(request.form)
        recetaForm = RecetaForm(request.form)
        insumos = Insumo.query.all()
        productos = Producto.query.all()

        lista_insumos = []

        for i in insumos:
            medida = Medida.query.filter(Medida.id == i.medida_id).first()
            lista_insumos.append((i.id, i.nombre+" - "+medida.medida))
        
        lista_productos = [(i.id, i.nombre) for i in productos]
        ingsRecetaForm.insumo.choices = lista_insumos
        recetaForm.producto.choices = lista_productos
        
        mensajes = []
        
        for i in insumos:
            medida = Medida.query.filter(Medida.id == i.medida_id).first()
            lista_insumos.append((i.id, i.nombre+" - "+medida.medida))
            
        ingsRecetaForm.insumo.choices = lista_insumos
        
        if request.method == "POST":
            cantidad_detalle = int(ingsRecetaForm.cantidad.data)
            id_insumo = int(ingsRecetaForm.insumo.data)
            insumo = Insumo.query.filter(Insumo.id == id_insumo).first()
            
            detalle = session["detalle"]
            
            if detalle:
                for det in detalle:
                    if det['id'] == insumo.id:
                        mensajes.append("Este articulo ya está agregado")
                        return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = session['detalle'],mensajes=mensajes)    

            detalle.append({
            "id": insumo.id,
            "nombre": insumo.nombre,
            "cantidad": cantidad_detalle,
            })
              
            session['detalle'] = detalle
            
            return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = session['detalle'],mensajes=mensajes)
        
        session['detalle'] = []
        return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = session['detalle'],mensajes=mensajes)

        
    @expose('/eliminarDetalle', methods=['GET'])
    def deleteDetalle(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
        ingsRecetaForm = IngredientesRecetaForm(request.form)
        recetaForm = RecetaForm(request.form)
        insumos = Insumo.query.all()
        productos = Producto.query.all()
        
        
        lista_productos = [(i.id, i.nombre) for i in productos]
        recetaForm.producto.choices = lista_productos

        insumos = Insumo.query.all()
        
        lista_insumos = []
        mensajes = []
        
        for i in insumos:
            medida = Medida.query.filter(Medida.id == i.medida_id).first()
            lista_insumos.append((i.id, i.nombre+" - "+medida.medida))
            
        ingsRecetaForm.insumo.choices = lista_insumos
        
        if request.method == "GET":
            id = int(request.args.get("id"))
            if session["detalle"]:
                detalle = session["detalle"]

            print("Detalle :")
            print(detalle)

            if detalle:
                for item in detalle:
                    if item['id'] == id:
                        detalle.remove({
                        "id": item['id'],
                        "nombre": item['nombre'],
                        "cantidad": item['cantidad'],
                        })
              
            session['detalle'] = detalle
            
            return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = session['detalle'],mensajes=mensajes)

        return self.render('recetas_detalle.html',recetaForm=recetaForm,ingsRecetaForm=ingsRecetaForm,detalle = session['detalle'],mensajes=mensajes)

class ProduccionCocinaView(BaseView):
    
    @expose('/')
    def viewReceta(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
        
        session["detalle"] = []
        recetas = Receta.query.all()
        
        return self.render('recetas.html',recetas=recetas)
    

class AbastecimientoView(ModelView):
    column_auto_select_related = True
    form_columns = ['descripcion','insumo', 'cantidad_insumo']  # Campos a mostrar en el formulario de edición
    def is_accessible(self):
        return login.current_user.is_authenticated

class InlineaCompraView(ModelView):
    column_auto_select_related = True
    form_columns=['id','abastecimiento','caducidad','cantidad', 'subtotal']


def max_allowed(form, field):
    if field.data == None:
        raise ValidationError('Debe introducir un número')    
    if field.data > 50:
        raise ValidationError('Max number of interfaces exceeded')
    
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
    

def date_format(view, value):
    return value.strftime('%d.%m.%Y')

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
        type(None): typefmt.null_formatter,
        date: date_format
    })
   

class CompraView(ModelView):
   
    def is_accessible(self):
        return login.current_user.is_authenticated
    column_formatters = dict(price=macro('render_price'))
    column_list = [ 'user','proveedor', 'detalles_compra','total']
    inline_models = [(Detalle_Compra, dict(form_columns=['id','abastecimiento','caducidad','cantidad', 'subtotal'],                    
    form_args = dict(
        cantidad=dict(validators=[ NumberRange(min=1, max=100)]), 
        subtotal=dict(validators=[ NumberRange(min=2, max=10000)]),
        abastecimiento=dict(validators=[not_null])
    )))]
    form_columns = ['user','proveedor','detalles_compra']  
    form_args = dict(
        usuario=dict(validators=[not_null]), 
        proveedor=dict(validators=[not_null])
    )
    def on_model_change(self, form, model, is_created):
        if is_created: 
            print(model.user)
            total = 0
            for detalles in model.detalles_compra:
                cantidad = float(detalles.abastecimiento.cantidad_insumo) * float(detalles.cantidad)
                total += detalles.subtotal
                insumo_id = detalles.abastecimiento.insumo_id
                detalle_id = detalles.id
                insumoInv = Insumo_Inventario(cantidad=cantidad,insumo_id = insumo_id,detalle_id = detalle_id)
                db.session.add(insumoInv)
            model.total = total
            db.session.commit()
    
class MedidaView(ModelView):
   
    def is_accessible(self):
        return login.current_user.is_authenticated
    column_auto_select_related = True
    column_list = [ 'medida']
    form_args = dict(
        medida=dict(
        validators=[DataRequired("Por favor, llena este campo"), Length(min=2, max=30)]
    ),
    )
    form_columns = ['medida']  
    
    
class AbastecimientoView(ModelView):
    column_auto_select_related = True
    form_columns = ['descripcion','insumo', 'cantidad_insumo']
    form_args = dict(
        insumo=dict(validators=[DataRequired("Por favor, llena este campo")]),
        descripcion=dict(validators=[DataRequired("Por favor, llena este campo"), Length(min=5, max=50)])
    )
    def is_accessible(self):
        return login.current_user.is_authenticated

class InsumoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','medida']  #
    form_args = dict(
        nombre=dict( validators=[DataRequired(message="pon algo we"), Length(min=2, max=30)]  ),
        medida=dict(validators=[DataRequired(message="pon algo we")])
    )
    column_list = ['nombre','medida']  # Campos a mostrar en la lista
    column_editable_list = ['nombre','medida'] # Campos editables en la lista
    def is_accessible(self):
        return login.current_user.is_authenticated
