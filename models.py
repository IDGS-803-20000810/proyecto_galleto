from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime

db=SQLAlchemy()

class Usuarios(db.Model):
    __tablename__='usuarios'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(250))
    permisos=db.Column(db.Integer)
    producciones_usuario = relationship("Produccion", back_populates="usuario")
    ventas_usuario = relationship("Venta", back_populates="usuario")
    compras_usuario = relationship("Compra", back_populates="usuario")

class Insumo(db.Model):
    __tablename__='insumo'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(80))
    insumo_inventario = relationship("Insumo_Inventario", back_populates="insumo")
    insumo_ingredientes = relationship("Ingredientes_Receta", back_populates="insumo")
    medida_id = mapped_column(ForeignKey("medida.id"))
    medida = relationship("Medida", back_populates="insumo")  
    insumo_merma_produccion = relationship("Merma_Produccion", back_populates="insumo")
    abastecimiento = relationship("Abastecimiento", back_populates="insumo")  
    def __str__(self):
        return self.nombre

class Proveedor(db.Model):
    __tablename__='proveedor'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80))
    direccion=db.Column(db.String(90))
    telefono=db.Column(db.String(10))
    proveedor_compras = relationship("Compra", back_populates="proveedor")
    # proveedor_inventario = relationship("Insumo_Inventario", back_populates="proveedor")
    # proveedor = db.relationship("Pedidos_Proveedor", back_populates="proveedor")
    def __str__(self):
        return self.nombre
    
class Insumo_Inventario(db.Model):
    __tablename__='insumo_inventario'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    # anaquel=db.Column(db.String(30))
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="insumo_inventario")  
    detalle_id = mapped_column(ForeignKey("detalle_compra.id"))
    detalle = relationship("Detalle_Compra", back_populates="insumo_inventario")    
    merma_inventario = relationship("Merma_Inventario", back_populates="insumo_inventario")
    def __str__(self):
        out = str(self.insumo) + ' ' + str(self.proveedor) #+ ' '  + str(self.anaquel)
        return out

# class Pedidos_Proveedor(db.Model):
#     __tablename__='pedidos_proveedor'
#     id=db.Column(db.Integer, primary_key=True)
#     cantidad=db.Column(db.Float)
#     precioActual=db.Column(db.Float) 
#     periodicidad=db.Column(db.Integer)
#     insumo_id = db.Column(db.Integer, db.ForeignKey("insumo.id")) 
#     insumo = relationship(Insumo, back_populates="pedidos_insumo")
#     proveedor_id = db.Column(fdb.Integer, db.ForeignKey("proveedor.id")) 
#     proveedor = db.relationship(Proveedor, back_populates="proveedor")

class Compra(db.Model):
    __tablename__='compra'
    id=db.Column(db.Integer,primary_key=True)
    fecha=db.Column(db.DateTime,default=datetime.datetime.now)
    usuario_id = mapped_column(ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="compras_usuario")  
    proveedor_id = mapped_column(ForeignKey("proveedor.id"))
    proveedor = relationship("Proveedor", back_populates="proveedor_compras")  
    detalles_compra = relationship("Detalle_Compra", back_populates="compra")
    total =db.Column(db.Float)

class Detalle_Compra(db.Model):
    __tablename__='detalle_compra'
    id=db.Column(db.Integer,primary_key=True)
    compra_id = mapped_column(ForeignKey("compra.id"))
    compra = relationship("Compra", back_populates="detalles_compra")  
    insumo_inventario = relationship("Insumo_Inventario", back_populates="detalle")
    abastecimiento_id = mapped_column(ForeignKey("abastecimiento.id"))
    abastecimiento = relationship("Abastecimiento", back_populates="detalle_abastecimiento")  
    caducidad=db.Column(db.DateTime,default=datetime.datetime.now)
    subtotal=db.Column(db.Float)
    cantidad=db.Column(db.Float)

class Merma_Inventario(db.Model):
    __tablename__='merma_inventario'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    insumo_inventario_id = mapped_column(ForeignKey("insumo_inventario.id"))
    insumo_inventario = relationship("Insumo_Inventario", back_populates="merma_inventario")  
    descripcion=db.Column(db.String(300))

class Receta(db.Model):
    __tablename__='receta'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(50))
    descripcion=db.Column(db.String(300))
    ingredientes_receta = relationship("Ingredientes_Receta", back_populates="receta")
    producciones = relationship("Produccion_Detalle", back_populates="receta")
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto_receta = relationship("Producto", back_populates="receta")
    cantidad_producto = db.Column(db.Integer)
    def __str__(self):
        return self.nombre

class Ingredientes_Receta(db.Model):
    __tablename__='ingredientes_receta'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Integer)
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="insumo_ingredientes")  
    receta_id = mapped_column(ForeignKey("receta.id"))
    receta = relationship("Receta", back_populates="ingredientes_receta")  

class Produccion(db.Model):
    __tablename__='produccion'
    id=db.Column(db.Integer,primary_key=True)
    fecha_hora=db.Column(db.DateTime,default=datetime.datetime.now)
    usuario_id = mapped_column(ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="producciones_usuario")  
    # detalles = relationship("Produccion_Detalle", back_populates="produccion")
    #nuevos campos de detalle
    cantidad=db.Column(db.Float)
    receta_id = mapped_column(ForeignKey("receta.id"))
    receta = relationship("Receta", back_populates="producciones")  
    produccion_id = mapped_column(ForeignKey("produccion.id"))
    produccion = relationship("Produccion", back_populates="detalles")  
    mermas = relationship("Merma_Produccion", back_populates="detalle_produccion")  
    produccion_detalle = relationship("Producto_Inventario", back_populates="produccion_detalle")


class Produccion_Detalle(db.Model):
    __tablename__='produccion_detalle'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    receta_id = mapped_column(ForeignKey("receta.id"))
    receta = relationship("Receta", back_populates="producciones")  
    produccion_id = mapped_column(ForeignKey("produccion.id"))
    produccion = relationship("Produccion", back_populates="detalles")  
    mermas = relationship("Merma_Produccion", back_populates="detalle_produccion")  
    produccion_detalle = relationship("Producto_Inventario", back_populates="produccion_detalle")

class Merma_Produccion(db.Model):
    __tablename__='merma_produccion'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    detalle_produccion_id = mapped_column(ForeignKey("produccion_detalle.id"))
    detalle_produccion = relationship("Produccion_Detalle", back_populates="mermas")  
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="insumo_merma_produccion")  
    descripcion=db.Column(db.String(300))

class Producto(db.Model):
    __tablename__='producto'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(255))
    receta = relationship("Receta", back_populates="producto_receta")  
    inventario = relationship("Producto_Inventario", back_populates="producto")  
    orden = relationship("Orden", back_populates="producto")  
    detalle_venta = relationship("Detalle_Venta", back_populates="producto")
    peso =db.Column(db.Float)

class Producto_Inventario(db.Model):
    __tablename__='producto_inventario'
    id=db.Column(db.Integer,primary_key=True)
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="inventario")  
    precio =db.Column(db.Float)
    peso =db.Column(db.Float)
    produccion_detalle_id = mapped_column(ForeignKey("produccion_detalle.id"))
    produccion_detalle = relationship("Produccion_Detalle", back_populates="producto_inventario")
    merma = relationship("Merma_Producto", back_populates="producto")  

class Merma_Producto(db.Model):
    __tablename__='merma_producto'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    hora=db.Column(db.DateTime,default=datetime.datetime.now)
    producto_id = mapped_column(ForeignKey("producto_inventario.id"))
    producto = relationship("Producto_Inventario", back_populates="merma")  
    descripcion=db.Column(db.String(300))

class Orden(db.Model):
    __tablename__='orden'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    hora=db.Column(db.DateTime,default=datetime.datetime.now)
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="orden")  
    terminado=db.Column(db.Boolean)

class Venta(db.Model):
    __tablename__='venta'
    id=db.Column(db.Integer,primary_key=True)
    hora=db.Column(db.DateTime,default=datetime.datetime.now)
    usuario_id = mapped_column(ForeignKey("usuarios.id"))
    usuario = relationship("Usuarios", back_populates="ventas_usuario")  
    total_venta =db.Column(db.Float)

class Detalle_Venta(db.Model):
    __tablename__='detalle_venta'
    id=db.Column(db.Integer,primary_key=True)
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="detalle_venta")  
    subtotal=db.Column(db.Float)
    cantidad=db.Column(db.Float)

class Medida(db.Model):
    __tablename__='medida'
    id=db.Column(db.Integer,primary_key=True)
    medida=db.Column(db.String(100))
    insumo = relationship("Insumo", back_populates="medida")
    def __str__(self):
        return self.medida

class Abastecimiento(db.Model):
    __tablename__='abastecimiento'
    id=db.Column(db.Integer,primary_key=True)
    descripcion=db.Column(db.String(255))
    detalle_abastecimiento = relationship("Detalle_Compra", back_populates="abastecimiento")  
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="abastecimiento")  
    cantidad_insumo=db.Column(db.Float)

class Users(UserMixin, Usuarios): ...