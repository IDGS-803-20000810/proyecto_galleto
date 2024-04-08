from flask_admin.contrib.sqla import ModelView
from models import Proveedor, Insumo, Insumo_Inventario,Abastecimiento, Compra,Detalle_Compra
# from models import Proveedor, Insumo, Insumo_Inventario, Pedidos_Proveedor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField, PasswordField, DecimalField

db=SQLAlchemy()

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

class RecetaView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','descripcion', 'insumo', 'proveedor' ]  # Campos a mostrar en el formulario de edición

class InsumoView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','medida']  # Campos a mostrar en el formulario de edición

class ProveedorView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','direccion', 'telefono']  # Campos a mostrar en el formulario de edición

class MedidaView(ModelView):
    column_auto_select_related = True
    form_columns = ['medida','direccion', 'telefono']  # Campos a mostrar en el formulario de edición

class EquivalenciaMedidaView(ModelView):
    column_auto_select_related = True
    form_columns = ['nombre','direccion', 'telefono']  # Campos a mostrar en el formulario de edición

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
    create_template = 'crear_compra.html'
