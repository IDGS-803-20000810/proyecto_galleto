from itertools import count
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin.model.template import macro
from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify
from models import Detalle_Venta, Ingredientes_Receta, Insumo, Insumo_Inventario, Merma_Producto, Orden, Presentacion, Produccion, Producto, Producto_Inventario, Proveedor, Receta, Medida, Venta
from models import db
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from wtforms.validators import Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from forms import DetalleVentaForm, MermaProductoForm, ProduccionForm, RecetaForm, IngredientesRecetaForm
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
from flask_admin.model.template import TemplateLinkRowAction
from flask_admin.model import typefmt
from flask_principal import Principal, identity_loaded, UserNeed, RoleNeed, Permission

admin_permission = Permission(RoleNeed('cuk'))
# db=SQLAlchemy()

class MermaInventarioView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacen" or login.current_user.role == "admin"
    column_list = [ 'cantidad', 'insumo_inventario', 'descripcion']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad', 'descripcion']  # Campos editables en la lista
    form_columns = ['cantidad', 'insumo_inventario', 'descripcion']  # Campos a mostrar en el formulario de edición
    # form_extra_fields = {
    #     'medida': SelectField( choices=[(0, 'Gramos'), (1, 'KG')])
    # }
    def on_model_change(self, form, model, is_created):
        # if int(model.medida) == 1:
        #     model.cantidad = model.cantidad * 1000
        if is_created:
            # print(model.medida)
            # print(model.medida)
            # print(model.medida)
            insumo = Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).first()
            if insumo:
                nCantidad = int(insumo.cantidad) - int(model.cantidad)
                # print(nCantidad)
                # print(nCantidad)
                # print(nCantidad)
                Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).update({"cantidad": nCantidad})
                db.session.commit()

class Insumo_InventarioView(ModelView):
    column_labels = {
        'detalle.caducidad': 'Fecha de Caducidad',  # Cambia 'Fecha de Caducidad' por la etiqueta que desees
        'detalle.abastecimiento': 'Abastecimiento'  # Cambia 'Fecha de Caducidad' por la etiqueta que desees
    }
    column_auto_select_related = True
    list_template = "lista_merma.html"  # Override the default template
    column_extra_row_actions = [  # Add a new action button
        TemplateLinkRowAction("acciones_extra.mermar", "Reportar merma"),
    ]
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacen" or login.current_user.role == "admin" or login.current_user.role == "cuck"
    column_list = ['cantidad','detalle.abastecimiento', 'insumo' , 'detalle.caducidad']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad',  'insumo'] # Campos editables en la lista
    form_columns = ['cantidad',  'insumo']  # Campos a mostrar en el formulario de edición
    can_create = False
    can_edit = False
    can_delete = False
    # form_extra_fields = {
    #     'medida': SelectField( choices=[(0, 'KG'), (1, 'Gramos')])
    # }
    def on_model_change(self, form, model, is_created):
        if is_created:
            # if int(model.medida) == 0:
            #     print(model.medida)
            #     print(model.medida)
            #     print(model.medida)
                # model.cantidad
                Insumo_Inventario.query.filter_by(
                id=model.id).update({"cantidad": model.cantidad})
                db.session.commit()

    @expose("/mermar", methods=("POST",))
    def merma(self):
        return True
    

    @expose("/mermar", methods=("POST",))
    def merma(self):
        idProdInv = request.form['row_id']
        prodInv = Producto_Inventario.query.filter(Producto_Inventario.id == idProdInv).first()
        prod = Producto.query.filter(Producto.id==prodInv.producto_id)
        formMerma = MermaProductoForm(request.form)
        return self.render('merma_producto.html',formMerma=formMerma, prodInv=prodInv, prod = prod, idProdInv=idProdInv, mensajes=[])        
    

class Producto_InventarioView(ModelView):
    column_auto_select_related = True
    list_template = "lista_merma.html"  
    column_list = ['producto', 'cantidad', 'produccion']  
    column_editable_list = ['producto', 'cantidad', 'produccion'] # Campos editables en la lista
    form_columns = ['producto', 'cantidad', 'produccion']  # Campos a mostrar en el formulario de edición
    
    column_extra_row_actions = [  
        TemplateLinkRowAction("acciones_extra.mermar", "Reportar merma"),
    ]

    def get_query(self):
        return self.session.query(self.model).filter(self.model.cantidad!=0)

    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "ventas" or login.current_user.role == "admin" or login.current_user.role == "cuck"
    
    @expose("/mermar", methods=("POST",))
    def merma(self):
        idProdInv = request.form['row_id']
        
        prodInv = Producto_Inventario.query.filter(Producto_Inventario.id == idProdInv).first()
        prod = Producto.query.filter(Producto.id==prodInv.producto_id)
        formMerma = MermaProductoForm(request.form)
        return self.render('merma_producto.html',formMerma=formMerma, prodInv=prodInv, prod = prod, idProdInv=idProdInv, mensajes=[])        
    
    @expose("/addMerma", methods=("POST",))
    def addMerma(self):
        idProdInv = request.form['idProdInv']
        formMerma = MermaProductoForm(request.form)

        prodInv = Producto_Inventario.query.filter(Producto_Inventario.id == idProdInv).first()
        prod = Producto.query.filter(Producto.id==prodInv.producto_id)

        if formMerma.cantidad.data > prodInv.cantidad:
             return self.render('merma_producto.html',formMerma=formMerma, prodInv=prodInv, prod = prod, idProdInv=idProdInv, mensajes=["No se puede mermar mas de lo contenido del inventario"])
            
        prodInv.cantidad = prodInv.cantidad - formMerma.cantidad.data

        db.session.add(prodInv)
        db.session.commit()
        
        mermaP = Merma_Producto(cantidad=formMerma.cantidad.data,producto_id=prodInv.id,descripcion=formMerma.descripcion.data)
        
        db.session.add(mermaP)
        db.session.commit()

        return redirect('/admin/producto_inventario/') 
    
        
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
        nombre=dict( validators=[DataRequired(message="puse algo we"), Length(min=3, max=30)]),
        direccion=dict(validators=[DataRequired(message="puse algo we"), Length(min=7, max=30)]),
        telefono=dict(validators=[DataRequired(message="puse algo we"), phonelenght])
    )
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacen" or login.current_user.role == "admin" 
    
class ProductoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','peso','precio']  # Campos a mostrar en el formulario de edición
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "cuck" or login.current_user.role == "admin"  or login.current_user.role == "ventas" 

class PresentacionView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "admin"  or login.current_user.role == "ventas" 

    column_auto_select_related = True
    form_columns = ["nombre","producto","cantidad_producto","precio"]  # Campos a mostrar en el formulario de edición
    column_labels = dict(cantidad_producto='cantidad producto')

class RecetaView(BaseView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "admin"  or login.current_user.role == "ventas"   or login.current_user.role == "cuck" 

    
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
        
        ingsRecetaForm.insumo.choices = lista_insumos
        lista_productos = [(i.id, i.nombre) for i in productos]
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

    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role == "admin" or login.current_user.role == "cuck" 

    def viewReceta(self):
        if not login.current_user.is_authenticated:
            return redirect("/")
    
    @expose('/')
    def viewProduccionesCocina(self):
        produccionForm = ProduccionForm(request.form)
        mensajes =[]
        lista_prod = []
        

        producciones = Produccion.query.filter(Produccion.estatus==0).all()
        for prod in producciones:
            receta = Receta.query.filter(Receta.id == prod.receta_id).first()
            lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
        
        recetas = Receta.query.all()
        lista_recetas = [(i.id, i.nombre) for i in recetas]
        produccionForm.receta.choices = lista_recetas
        
        ordenes = Orden.query.all()
        
        return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes=mensajes)
    
    @expose('/addProduccion',methods=['POST'])
    def addProduccionesCocina(self):
        produccionForm = ProduccionForm(request.form)
        cantidad = int(produccionForm.cantidad.data)
        receta_id = int(produccionForm.receta.data)

        mensajes = []
        lista_prod = []

        recetas = Receta.query.all()
        lista_recetas = [(i.id, i.nombre) for i in recetas]
        produccionForm.receta.choices = lista_recetas
        ############################

        ingredientes = Ingredientes_Receta.query.filter(Ingredientes_Receta.receta_id==receta_id).all()
            
        #Verificar si hay insumos suficientes
        for item in ingredientes:
            total = 0
            #TODO: CAMBIAR EL QUERY PROVISIONAL POR ESTE CUANDO ESTEN LAS COMPRAS
            # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
            insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).all()
            
            insumo = Insumo.query.filter(Insumo.id == item.insumo_id).first()

            for ins in insumosInv:
                total+=ins.cantidad
                
            if total < item.cantidad*cantidad:
                mensajes.append("Los insumos en el inventario no son suficientes: "+insumo.nombre)
                
                producciones = Produccion.query.filter(Produccion.estatus==0).all()
                for prod in producciones:
                    receta = Receta.query.filter(Receta.id == prod.receta_id).first()
                    lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
                ordenes = Orden.query.all()
                return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes =mensajes)
        #######################


        produccion = Produccion(cantidad=cantidad,receta_id=receta_id,estatus=0)
        
        

        db.session.add(produccion)
        db.session.commit()

        producciones = Produccion.query.filter(Produccion.estatus==0).all()
        for prod in producciones:
            receta = Receta.query.filter(Receta.id == prod.receta_id).first()
            lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
        
        ordenes = Orden.query.all()

        return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes=mensajes)
    
    @expose('/cambiarEstatus')
    def changeProduccionesCocina(self):
        produccionForm = ProduccionForm(request.form)
        
        recetas = Receta.query.all()
        lista_recetas = [(i.id, i.nombre) for i in recetas]
        produccionForm.receta.choices = lista_recetas
        
        estatus = int(request.args.get("estatus"))
        id = int(request.args.get("id"))
        mensajes = []
        lista_prod = []

        produccion = Produccion.query.filter(Produccion.id==id).first()
        produccion.estatus = estatus
        nombre = ""

        if estatus == 1:
            ingredientes = Ingredientes_Receta.query.filter(Ingredientes_Receta.receta_id==produccion.receta_id).all()
            
            #Verificar si hay insumos suficientes
            for item in ingredientes:
                total = 0
                #TODO: CAMBIAR EL QUERY PROVISIONAL POR ESTE CUANDO ESTEN LAS COMPRAS
                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).all()
                
                print("***********************item.cantidad****************")
                print(item.cantidad*produccion.cantidad)
                
                print("***********************insumosInv****************")
                print(insumosInv)
                
                insumo = Insumo.query.filter(Insumo.id == item.insumo_id).first()

                for ins in insumosInv:
                    total+=ins.cantidad

                print("***********************total****************")
                print(total)
                    
                if total < item.cantidad*produccion.cantidad:
                    mensajes.append("Los insumos en el inventario no son suficientes: "+insumo.nombre)
                    
                    producciones = Produccion.query.filter(Produccion.estatus==0).all()
                    for prod in producciones:
                        receta = Receta.query.filter(Receta.id == prod.receta_id).first()
                        lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
                    ordenes = Orden.query.all()
                    return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes =mensajes)
                    
            #Restar los insumos del inventario
            for item in ingredientes:
                print("*******************for*************************")
                
                total = 0

                #TODO: CAMBIAR EL QUERY PROVISIONAL POR ESTE CUANDO ESTEN LAS COMPRAS
                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).all()
                
                insumo = Insumo.query.filter(Insumo.id == item.insumo_id)

                item_cantidad = item.cantidad*produccion.cantidad

                for ins in insumosInv:
                    print("*******************ins Inicio*************************")
                    print(ins)
                    if ins.cantidad >= item_cantidad:
                        ins.cantidad = ins.cantidad - item_cantidad
                        db.session.add(ins)
                        db.session.commit()

                        print("*******************ins Fin*************************")
                        print(ins)
                        break
                    else:
                        item_cantidad = item_cantidad - ins.cantidad
                        ins.cantidad = 0
                        db.session.add(ins)
                        db.session.commit()

                        print("*******************ins Fin*************************")
                        print(ins)

        receta_insertar = Receta.query.filter(Receta.id == produccion.receta_id).first()
        cantidad_producto = receta_insertar.cantidad_producto*produccion.cantidad
        producto_inventario = Producto_Inventario(producto_id=receta_insertar.producto_id,cantidad = cantidad_producto,produccion_id=produccion.id)

        db.session.add(produccion)
        db.session.commit()
        
        db.session.add(producto_inventario)
        db.session.commit()

        producciones = Produccion.query.filter(Produccion.estatus==0).all()
        for prod in producciones:
            receta = Receta.query.filter(Receta.id == prod.receta_id).first()
            lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
        
        ordenes = Orden.query.all()

        return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes =[])


def max_allowed(form, field):
    if field.data == None:
        raise ValidationError('Debe introducir un número')    
    if field.data > 50:
        raise ValidationError('Max number of interfaces exceeded')
    

class InlineaCompraView(ModelView):
    column_auto_select_related = True
    form_columns=['id','abastecimiento','caducidad','cantidad', 'subtotal']

    
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
    def after_model_change(self, form, model, is_created):
        if is_created: 
            total = 0
            for detalles in model.detalles_compra:
                print(str(detalles.abastecimiento.id))
                print("second: " + str(detalles.cantidad))
                cantidad = float(detalles.abastecimiento.cantidad_insumo) * float(detalles.cantidad)
                total += detalles.subtotal
                insumo_id = detalles.abastecimiento.insumo_id
                print("detalle id : " + str(detalles))
                detalle_id = detalles.id
                insumoInv = Insumo_Inventario(cantidad=cantidad,insumo_id = insumo_id,detalle_id = detalle_id)
                db.session.add(insumoInv)
            model.total = total
            db.session.commit()
    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role == "admin" or login.current_user.role == "almacen" 

    column_formatters = dict(price=macro('render_price'))
    column_list = [ 'user','proveedor', 'detalles_compra','fecha','total']
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

class MedidaView(ModelView):
   
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacenista" or login.current_user.role == "admin"
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return render_template('403.html'), 403
    column_auto_select_related = True
    column_list = [ 'medida']
    form_args = dict(
        medida=dict(
        validators=[DataRequired("Por favor, llena este campo"), Length(min=2, max=30)]
    ),
    )
    form_columns = ['medida']  
    
    
class AbastecimientoView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacenista" or login.current_user.role == "admin"
    column_auto_select_related = True
    form_columns = ['descripcion','insumo', 'cantidad_insumo']
    form_args = dict(
        insumo=dict(validators=[DataRequired("Por favor, llena este campo")]),
        descripcion=dict(validators=[DataRequired("Por favor, llena este campo"), Length(min=5, max=50)]),
        cantidad_insumo=dict(validators=[DataRequired("Por favor, llena este campo"), NumberRange(min=0.001)])
    )
    #def cantidad_insumo_formatter(view, context, model, name):
    #    if model.insumo:
    #        insumo = model.insumo
    #        return "Cantidad ("+insumo.medida+")"
    #    return "Cantidad "
    
    def is_accessible(self):
        return login.current_user.is_authenticated
    #column_labels = {
    #    'cantidad_insumo': str(cantidad_insumo_formatter)  # Cambia 'Fecha de Caducidad' por la etiqueta que desees
    #}
    
class InsumoView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "almacenista" or login.current_user.role == "admin"
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

class VentaPrincipalView(BaseView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role == "ventas" or login.current_user.role == "admin"
    @expose('/')
    def indexVentas(self):
        detalleVentaForm = DetalleVentaForm(request.form)

        session['total'] = 0
        session['detalle'] = []
        
        presentaciones = Presentacion.query.all()
        productos = Producto.query.all()
        for prod in productos:
            stock = 0
            productos_inventario=Producto_Inventario.query.filter(Producto_Inventario.producto_id == prod.id).all()
            for producto_inv in productos_inventario:
                stock+=producto_inv.cantidad
            productos[productos.index(prod)].stock = stock
        productos.sort(key=lambda x: x.stock, reverse=True)
                


        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=[])
    

    @expose('/addDetalle',methods=['POST'])
    def addDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()
        print("detalle presentacion *******************++")
        if request.method == "POST":
            mensaje = []
            presentacion_id = int(detalleVentaForm.presentacion_id.data)
            cantidad = int(detalleVentaForm.cantidad.data)
            print("cantidad "+str(cantidad))
            print("presentacion id "+str(presentacion_id))
            presentacion = Presentacion.query.filter(Presentacion.id == presentacion_id).first()
            producto = Producto.query.filter(Producto.id == presentacion.producto_id).first()

            #Verificar si hay insumos suficientes

            total = 0

            # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
            cantidad_detalle = presentacion.cantidad_producto*cantidad
            detalle = session['detalle']

            for det in detalle:
                if det['producto_id'] == producto.id:
                    cantidad_detalle+=det['cantidad']

            productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == presentacion.producto_id)      

            for pInv in productosInv:
                total+=pInv.cantidad

            if total < cantidad_detalle:
                mensaje.append("Los productos en el inventario no son suficientes: "+producto.nombre)
                print(mensaje[0])
                productos = Producto.query.all()
                presentaciones = Presentacion.query.all()

                return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=mensaje)
        
            ##AQUI VA

            precio = presentacion.precio*cantidad

            total = session['total']
            total+=precio
            session['total'] = total

            
            detalle.append({
                "index": len(detalle) + 1,
                "presentacion_id":presentacion_id,
                "producto_id":producto.id,
                "nombre":presentacion.nombre,
                "cantidad":cantidad,
                "subtotal":precio
            })

            session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,productos=productos,mensaje=mensaje)

    @expose('/addDetalleProd',methods=['POST'])
    def addDetalleProd(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()
        print("detalle producto *******************++")
        if request.method == "POST":
            mensaje = []
            producto_id = int(detalleVentaForm.presentacion_id.data)
            cantidad = int(detalleVentaForm.cantidad.data)
            producto = Producto.query.filter(Producto.id == producto_id).first()
            print("cantidad "+str(cantidad))
            print("producto id "+str(producto_id))
            #Verificar si hay insumos suficientes

            total = 0
            detalle = session['detalle']
            cantidad_total = cantidad

            for det in detalle:
                if det['producto_id'] == producto.id:
                    cantidad_total+=det['cantidad']
            # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
            productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == producto.id)
            
            for pInv in productosInv:
                total+=pInv.cantidad

            if total < cantidad_total:
                mensaje.append("Los productos en el inventario no son suficientes: "+producto.nombre)
                presentaciones = Presentacion.query.all()
                productos = Producto.query.all()
                print(mensaje[0])
                return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,productos=productos,mensaje=mensaje)
        
            precio = producto.precio*cantidad

            total = session['total']
            total += precio
            session['total'] = total


            detalle.append({
                "index": len(detalle) + 1,
                "presentacion_id":0,
                "producto_id":producto_id,
                "presentacion":producto.nombre,
                "cantidad":cantidad,
                "subtotal":precio
            })

            session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=mensaje)

    @expose('/deleteDetalle',methods=['GET'])
    def deleteDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()

        index = int(request.args.get("index"))

        detalle = session["detalle"]

        if detalle:
            detalle.pop(index - 1)

        num = 0
        total = 0

        for det in detalle:
            detalle[num]["index"] = num+1
            precio = detalle[num]['subtotal']
            total += precio
            num += 1

        session['total'] = total
        session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],productos=productos,presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,mensaje=[])
    
    @expose('/guardarCompra',methods=['GET'])
    def guardarCompra(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()

        detalle = session["detalle"]

        for item in detalle:

            if item['presentacion_id'] != 0:

                presentacion = Presentacion.query.filter(Presentacion.id == item['presentacion_id']).first()
                producto = Producto.query.filter(Producto.id == presentacion.producto_id).first()

                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == presentacion.producto_id)      

                item_cantidad = item['cantidad']*presentacion.cantidad_producto

            else:
                producto = Producto.query.filter(Producto.id == item['producto_id']).first()
                productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == producto.id)
                item_cantidad = item['cantidad']


            for pInv in productosInv:

                if pInv.cantidad >= item_cantidad:
                    pInv.cantidad = pInv.cantidad - item_cantidad
                    db.session.add(pInv)
                    db.session.commit()

                    print("*******************p Fin*************************")
                    print(pInv)
                    break
                else:
                    item_cantidad = item_cantidad - pInv.cantidad
                    pInv.cantidad = 0
                    db.session.add(pInv)
                    db.session.commit()

                    print("*******************'p' Fin*************************")
                    print(pInv)

        venta = Venta(total_venta=session['total'],user_id=login.current_user.id)

        db.session.add(venta)
        db.session.commit()

        db.session.refresh(venta)
        
        for det in detalle:
            if det['presentacion_id'] == 0:
                detVent = Detalle_Venta(cantidad=det['cantidad'],producto_id=det['producto_id'],subtotal=det['subtotal'],venta_id=venta.id)
            else:
                detVent = Detalle_Venta(cantidad=det['cantidad'],producto_id=det['producto_id'],presentacion_id=det['presentacion_id'],subtotal=det['subtotal'],venta_id=venta.id)
            db.session.add(detVent)
            db.session.commit()

        session['detalle'] = []
        session['total'] = 0

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=['Venta Completada : '])
