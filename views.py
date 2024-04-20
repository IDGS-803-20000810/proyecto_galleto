from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin.model.template import macro
from flask import render_template, request, redirect, session
from models import Detalle_Venta,User, Ingredientes_Receta, Insumo, Insumo_Inventario, Insumos_Produccion, Merma_Producto, Orden, Presentacion, Produccion, Producto, Producto_Inventario, Producto_Inventario_Detalle, Proveedor, Receta, Medida, Venta
from models import db, Roles
from wtforms.validators import Length
from forms import DetalleVentaForm, MermaProductoForm, ProduccionForm, RecetaForm, IngredientesRecetaForm,SolicitudProduccionForm
from models import Insumo, Insumo_Inventario,Detalle_Compra
from wtforms import validators
from wtforms.validators import DataRequired, NumberRange
import flask_login as login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.model.template import TemplateLinkRowAction
from customValidators import  not_null, phonelenght

class MermaInventarioView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "almacen" or login.current_user.role.nombre== "admin"
    column_list = [ 'cantidad', 'insumo_inventario', 'descripcion']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad', 'descripcion']  # Campos editables en la lista
    form_columns = ['cantidad', 'insumo_inventario', 'descripcion']  # Campos a mostrar en el formulario de edición
    can_create = False
    can_edit = False
    can_delete = False
    def on_model_change(self, form, model, is_created):
        if is_created:
            insumo = Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).first()
            if insumo:
                nCantidad = int(insumo.cantidad) - int(model.cantidad)
                Insumo_Inventario.query.filter_by(
                id=model.insumo_inventario.id).update({"cantidad": nCantidad})
                db.session.commit()

class MermaProductoView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "almacen" or login.current_user.role.nombre== "admin"
    column_list = [ 'cantidad', 'producto', 'descripcion','hora']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad', 'descripcion']  # Campos editables en la lista
    form_columns = ['cantidad', 'producto', 'descripcion']  # Campos a mostrar en el formulario de edición
    can_create = False
    can_edit = False
    can_delete = False


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
                return login.current_user.role.nombre== "almacen" or login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck"
    column_list = ['cantidad','detalle.abastecimiento', 'insumo' , 'detalle.caducidad']  # Campos a mostrar en la lista
    column_editable_list = ['cantidad',  'insumo'] # Campos editables en la lista
    form_columns = ['cantidad',  'insumo']  # Campos a mostrar en el formulario de edición
    can_create = False
    can_edit = False
    can_delete = False

    def on_model_change(self, form, model, is_created):
        if is_created:
                Insumo_Inventario.query.filter_by(
                id=model.id).update({"cantidad": model.cantidad})
                db.session.commit()
    

    @expose("/mermar", methods=("POST",))
    def merma(self):
        idProdInv = request.form['row_id']
        prodInv = Producto_Inventario.query.filter(Producto_Inventario.id == idProdInv).first()
        prod = Producto.query.filter(Producto.id==prodInv.producto_id)
        formMerma = MermaProductoForm(request.form)
        return self.render('merma_producto.html',formMerma=formMerma, prodInv=prodInv, prod = prod, idProdInv=idProdInv, mensajes=[])        
    
class AdminRecetaView(ModelView):
    column_list = [ 'nombre','descripcion','producto_receta','cantidad_producto', 'ingredientes_receta']
    inline_models = [(Ingredientes_Receta, dict(form_columns=['id','cantidad','insumo'],                    
    form_args = dict(
        cantidad=dict(validators=[ NumberRange(min=1)]), 
        insumo=dict(validators=[not_null])
    )))]
    form_columns = ['nombre','descripcion','producto_receta','cantidad_producto']  
    form_args = dict(
        producto_receta=dict(validators=[not_null]), 
        cantidad_producto=dict(validators=[not_null]),
        nombre=dict(validators=[not_null]),
        descripcion=dict(validators=[not_null])
    )
    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck" 

class VentaView(ModelView):
    column_list = [ 'hora','user','total_venta','detalle_venta']
    inline_models = [(Detalle_Venta, dict(form_columns=['id','presentacion','producto','cantidad','subtotal'],                    
    ))]
    form_columns = ['hora','user','total_venta','detalle_venta']
    can_create = False
    can_edit = False
    can_delete = False
    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck"
        


class Producto_InventarioView(ModelView):
    column_auto_select_related = True
    list_template = "lista_merma.html"  
    column_list = ['producto', 'cantidad', 'produccion','responsable','proveedores']  
    column_editable_list = ['producto', 'cantidad', 'produccion'] # Campos editables en la lista
    form_columns = ['producto', 'cantidad', 'produccion']  # Campos a mostrar en el formulario de edición
    
    
    column_extra_row_actions = [  
        TemplateLinkRowAction("acciones_extra.mermar", "Reportar merma"),
    ]
    can_create = False
    can_edit = False
    can_delete = False
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "ventas" or login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck"
    
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
                return login.current_user.role.nombre== "almacen" or login.current_user.role.nombre== "admin" 
    
class ProductoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','peso','precio']  # Campos a mostrar en el formulario de edición
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "cuck" or login.current_user.role.nombre== "admin"  or login.current_user.role.nombre== "ventas" 

class PresentacionView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "admin"  or login.current_user.role.nombre== "ventas" 

    column_auto_select_related = True
    form_columns = ["nombre","producto","cantidad_producto","precio"]  # Campos a mostrar en el formulario de edición
    column_labels = dict(cantidad_producto='cantidad producto')

class RecetaView(BaseView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "admin"  or login.current_user.role.nombre== "ventas"   or login.current_user.role.nombre== "cuck" 

class ProduccionesView(ModelView):
    column_list = [ 'fecha_hora','user','receta','cantidad',"completado"]
    can_create = False
    can_edit = False
    can_delete = False

    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck" 
    
    


class ProduccionCocinaView(BaseView):

    def is_accessible(self):
        if not login.current_user.is_authenticated:
            return False
        else:
            return login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "cuck" 

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

        produccion = Produccion(cantidad=cantidad,receta_id=receta_id,estatus=0,user_id=login.current_user.id)
        
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
            
                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).all()
                
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


                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).all()
                
                insumo = Insumo.query.filter(Insumo.id == item.insumo_id)

                item_cantidad = item.cantidad*produccion.cantidad

                db.session.add(produccion)
                db.session.commit()
                db.session.refresh(produccion)

                for ins in insumosInv:
                    print("*******************ins Inicio*************************")
                    print(ins)
                    if ins.cantidad >= item_cantidad:
                        ins.cantidad = ins.cantidad - item_cantidad
                        db.session.add(ins)
                        db.session.commit()

                        insProd = Insumos_Produccion(insumo_inventario_id=ins.id,produccion_id=produccion.id,cantidad=item_cantidad)
                        db.session.add(insProd)
                        db.session.commit()


                        print("*******************ins Fin*************************")
                        print(ins)
                        break
                    else:
                        item_cantidad = item_cantidad - ins.cantidad
                        ins.cantidad = 0
                        db.session.add(ins)
                        db.session.commit()

                        insProd = Insumos_Produccion(insumo_inventario_id=ins.id,produccion_id=produccion.id,cantidad=ins.cantidad)
                        db.session.add(insProd)
                        db.session.commit()

                        print("*******************ins Fin*************************")
                        print(ins)

        receta_insertar = Receta.query.filter(Receta.id == produccion.receta_id).first()
        cantidad_producto = receta_insertar.cantidad_producto*produccion.cantidad
        producto_inventario = Producto_Inventario(producto_id=receta_insertar.producto_id,cantidad = cantidad_producto,produccion_id=produccion.id)

        
        
        db.session.add(producto_inventario)
        db.session.commit()

        producciones = Produccion.query.filter(Produccion.estatus==0).all()
        for prod in producciones:
            receta = Receta.query.filter(Receta.id == prod.receta_id).first()
            lista_prod.append({"id":prod.id,"receta":receta.nombre,"cantidad":prod.cantidad})
        
        ordenes = Orden.query.all()

        return self.render('produccion_cocina.html',produccionForm=produccionForm,producciones=lista_prod,ordenes=ordenes,mensajes =[])



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
            return login.current_user.role.nombre== "admin" or login.current_user.role.nombre== "almacen" 

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
                return login.current_user.role.nombre== "almacenista" or login.current_user.role.nombre == "admin"
    
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
                return login.current_user.role.nombre== "almacenista" or login.current_user.role.nombre== "admin"
    column_auto_select_related = True
    form_columns = ['descripcion','insumo', 'cantidad_insumo']
    form_args = dict(
        insumo=dict(validators=[DataRequired("Por favor, llena este campo")]),
        descripcion=dict(validators=[DataRequired("Por favor, llena este campo"), Length(min=5, max=50)]),
        cantidad_insumo=dict(validators=[DataRequired("Por favor, llena este campo"), NumberRange(min=0.001)])
    )

class ProduccionView(ModelView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "cuck" or login.current_user.role.nombre== "admin"
    column_auto_select_related = True
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
                return login.current_user.role.nombre== "almacenista" or login.current_user.role.nombre== "admin"
    column_auto_select_related = True
    form_columns = ['nombre','medida']  
    form_args = dict(
        nombre=dict( validators=[DataRequired(message="pon algo we"), Length(min=2, max=30)]  ),
        medida=dict(validators=[DataRequired(message="pon algo we")])
    )
    column_list = ['nombre','medida'] 
    column_editable_list = ['nombre','medida'] 
    def is_accessible(self):
        return login.current_user.is_authenticated

class VentaPrincipalView(BaseView):
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "ventas" or login.current_user.role.nombre== "admin"
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
                
        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=[])
    

    @expose('/addDetalle',methods=['POST'])
    def addDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()
        for prod in productos:
            stock = 0
            productos_inventario=Producto_Inventario.query.filter(Producto_Inventario.producto_id == prod.id).all()
            for producto_inv in productos_inventario:
                stock+=producto_inv.cantidad
            productos[productos.index(prod)].stock = stock
        print("detalle presentacion *******************++")
        if request.method == "POST":
            mensaje = []
            presentacion_id = int(detalleVentaForm.presentacion_id.data)
            cantidad = int(detalleVentaForm.cantidad.data)
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

            print("DETALLE")
            print(detalle)

            for det in detalle:
                for prod in productos:
                    if det['producto_id']== prod.id:
                        productos[productos.index(prod)].stock = prod.stock - det['cantidad']
            session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,productos=productos,mensaje=mensaje)

    @expose('/addDetalleProd',methods=['POST'])
    def addDetalleProd(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()
        for prod in productos:
            stock = 0
            productos_inventario=Producto_Inventario.query.filter(Producto_Inventario.producto_id == prod.id).all()
            for producto_inv in productos_inventario:
                stock+=producto_inv.cantidad
            productos[productos.index(prod)].stock = stock
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
                "nombre":producto.nombre,
                "cantidad":cantidad,
                "subtotal":precio
            })
            for det in detalle:
                for prod in productos:
                    if det['producto_id']== prod.id:
                        productos[productos.index(prod)].stock = prod.stock - det['cantidad']
            session['detalle'] = detalle
            
        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=mensaje)

    @expose('/deleteDetalle',methods=['GET'])
    def deleteDetalle(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()
        for prod in productos:
            stock = 0
            productos_inventario=Producto_Inventario.query.filter(Producto_Inventario.producto_id == prod.id).all()
            for producto_inv in productos_inventario:
                stock+=producto_inv.cantidad
            productos[productos.index(prod)].stock = stock
        
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

        for det in detalle:
            for prod in productos:
               if det['producto_id']== prod.id:
                    productos[productos.index(prod)].stock = prod.stock - det['cantidad']
        session['detalle'] = detalle
        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],productos=productos,presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,mensaje=[])
    
    @expose('/guardarVenta',methods=['GET'])
    def guardarCompra(self):
        detalleVentaForm = DetalleVentaForm(request.form)
        productos = Producto.query.all()

        detalle = session["detalle"]
        
        venta = Venta(total_venta=session['total'],user_id=login.current_user.id)

        db.session.add(venta)
        db.session.commit()

        db.session.refresh(venta)

        for item in detalle:

            if item['presentacion_id'] != 0:

                presentacion = Presentacion.query.filter(Presentacion.id == item['presentacion_id']).first()
                producto = Producto.query.filter(Producto.id == presentacion.producto_id).first()

                # insumosInv = Insumo_Inventario.query.filter(Insumo_Inventario.insumo_id == item.insumo_id, Insumo_Inventario.cantidad != 0).join(Detalle_Compra).join(Compra).order_by(asc(Compra.fecha)).all()
                productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == presentacion.producto_id)      

                item_cantidad = item['cantidad']*presentacion.cantidad_producto

                detVent = Detalle_Venta(cantidad=item['cantidad'],producto_id=item['producto_id'],presentacion_id=item['presentacion_id'],subtotal=item['subtotal'],venta_id=venta.id)
                db.session.add(detVent)
                db.session.commit()
                db.session.refresh(detVent)

            else:
                producto = Producto.query.filter(Producto.id == item['producto_id']).first()
                productosInv = Producto_Inventario.query.filter(Producto_Inventario.producto_id == producto.id)
                item_cantidad = item['cantidad']
                detVent = Detalle_Venta(cantidad=item['cantidad'],producto_id=item['producto_id'],subtotal=item['subtotal'],venta_id=venta.id)
                db.session.add(detVent)
                db.session.commit()
                db.session.refresh(detVent)


            for pInv in productosInv:

                if pInv.cantidad >= item_cantidad:
                    pInv.cantidad = pInv.cantidad - item_cantidad
                    db.session.add(pInv)
                    db.session.commit()

                    insInvDet = Producto_Inventario_Detalle(producto_inventario_id=pInv.id,detalle_venta_id=detVent.id,cantidad=item_cantidad)
                    db.session.add(insInvDet)
                    db.session.commit()

                    print("*******************p Fin*************************")
                    print(pInv)
                    break
                else:
                    item_cantidad = item_cantidad - pInv.cantidad
                    pInv.cantidad = 0
                    db.session.add(pInv)
                    db.session.commit()

                    insInvDet = Producto_Inventario_Detalle(producto_inventario_id=pInv.id,detalle_venta_id=detVent.id,cantidad=pInv.cantidad)
                    db.session.add(insInvDet)
                    db.session.commit()

                    print("*******************'p' Fin*************************")
                    print(pInv)

        session['detalle'] = []
        session['total'] = 0

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,productos=productos,detalleVentaForm=detalleVentaForm,mensaje=['Venta Completada'])

    @expose('/addSolicitud',methods=['POST'])
    def addSolicitud(self):
        detalleVentaForm = SolicitudProduccionForm(request.form)
        productos = Producto.query.all()
        for prod in productos:
            stock = 0
            productos_inventario=Producto_Inventario.query.filter(Producto_Inventario.producto_id == prod.id).all()
            for producto_inv in productos_inventario:
                stock+=producto_inv.cantidad
            productos[productos.index(prod)].stock = stock
        print("detalle presentacion *******************++")
        if request.method == "POST":
            mensaje = []
            producto_id = int(detalleVentaForm.producto_id.data)
            cantidad = int(detalleVentaForm.cantidad.data)
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

            for det in detalle:
                for prod in productos:
                    if det['producto_id']== prod.id:
                        productos[productos.index(prod)].stock = prod.stock - det['cantidad']
            session['detalle'] = detalle

        presentaciones = Presentacion.query.all()

        return self.render('venta_principal.html',detalle=session['detalle'],total=session['total'],presentaciones=presentaciones,detalleVentaForm=detalleVentaForm,productos=productos,mensaje=mensaje)


class UserView(ModelView):
    column_list = [ 'first_name', 'last_name', 'login','prevLogin', 'role']  
    column_auto_select_related = True
    form_columns = ['first_name','last_name', 'login', 'role', 'password']  
    def after_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)
        user = model
        db.session.add(user)
        db.session.commit()
    def is_accessible(self):
            if not login.current_user.is_authenticated:
                return False
            else:
                return login.current_user.role.nombre== "admin"