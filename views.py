from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import Flask, render_template, request, Response, flash, g, redirect, session, url_for, jsonify
from models import Ingredientes_Receta, Insumo, Insumo_Inventario, Orden, Presentacion, Produccion, Producto, Producto_Inventario, Proveedor, Receta, Medida
from models import db
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from forms import DetalleVentaForm, ProduccionForm, RecetaForm, IngredientesRecetaForm
from models import Proveedor, Insumo, Insumo_Inventario,Abastecimiento, Compra,Detalle_Compra
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField, DecimalField

# db=SQLAlchemy()

class MermaInventarioView(ModelView):
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

class InsumoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','medida']  #
    column_list = ['nombre','medida']  # Campos a mostrar en la lista
    column_editable_list = ['nombre','medida'] # Campos editables en la lista
    

class ProveedorView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','direccion', 'telefono']  # Campos a mostrar en el formulario de edición

class ProductoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','peso']  # Campos a mostrar en el formulario de edición

class MedidaView(ModelView):
    column_auto_select_related = True
    form_columns = ['medida']  # Campos a mostrar en el formulario de edición

class PresentacionView(ModelView):
    column_auto_select_related = True
    form_columns = ["nombre","producto","cantidad_producto","precio"]  # Campos a mostrar en el formulario de edición
    column_labels = dict(cantidad_producto='cantidad producto')

class RecetaView(BaseView):
    
    @expose('/')
    def viewReceta(self):
        session["detalle"] = []
        recetas = Receta.query.all()
        
        return self.render('recetas.html',recetas=recetas)
    
    @expose('/eliminarReceta',methods=['GET'])
    def deleteReceta(self):
        session["detalle"] = []

        id = request.args.get("id")
        receta = db.session.query(Receta).filter(Receta.id == id).first()
        db.session.delete(receta)
        db.session.commit()
        
        recetas = Receta.query.all()
        return self.render('recetas.html',recetas=recetas)
    
    @expose('/addReceta', methods=['POST','GET'])
    def addReceta(self):
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
            
            print("***********************item.cantidad****************")
            print(item.cantidad*cantidad)
            
            print("***********************insumosInv****************")
            print(insumosInv)

            print("***********************total****************")
            print(total)
                
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

    
class AbastecimientoView(ModelView):
    column_auto_select_related = True
    form_columns = ['descripcion','insumo', 'cantidad_insumo']  # Campos a mostrar en el formulario de edición

class CompraView(ModelView):
    column_auto_select_related = True
    inline_models = ((Detalle_Compra, ))
    form_columns = ['usuario','proveedor','detalles_compra']  
    create_template = 'crear_compra.html'

class DetalleCompraView(ModelView):
    column_auto_select_related = True
    form_columns = ['abastecimiento','caducidad','cantidad']  
    create_template = 'crear_compra.shtml'

class VentaPrincipalView(BaseView):

    @expose('/')
    def indexRecetas(self):
        detalleVentaForm = DetalleVentaForm(request.form)

        session['total'] = 0
        session['detalle'] = []
        
        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm)
    

    @expose('/addDetalle',methods=['POST'])
    def addDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)

        if request.method == "POST":
        
            presentacion_id = int(detalleVentaForm.presentacion_id.data)
            cantidad = int(detalleVentaForm.cantidad.data)

            #TODO: VALIDACIONES PARA REVISAR SI HAY SUFICIENTES PRODUCTOS

            presentacion = Presentacion.query.filter(Presentacion.id == presentacion_id).first()
            precio = presentacion.precio*cantidad

            total = session['total']
            total+=precio
            session['total'] = total

            detalle = session['detalle']

            detalle.append({
                "index": len(detalle) + 1,
                "presentacion_id":presentacion_id,
                "presentacion":presentacion.nombre,
                "cantidad":cantidad,
                "subtotal":precio
            })

            session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm)

    @expose('/deleteDetalle',methods=['GET'])
    def deleteDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)

        index = int(request.args.get("index"))

        #TODO: VALIDACIONES PARA REVISAR SI HAY SUFICIENTES PRODUCTOS

        detalle = session["detalle"]

        if detalle:
            detalle.pop(index - 1)

        num = 0
        total = 0

        print("**************detalle*****************")
        print(detalle)

        for det in detalle:
            num += 1
            detalle[num]["index"] = num
            precio = detalle[num]['subtotal']
            total += precio

        session['total'] = total
        session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm)
