from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from flask_login import UserMixin
import datetime
from datetime import date

db=SQLAlchemy()

class Roles(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    usuarios = relationship("User", back_populates="role")  
    def get_id(self):
        return self.id
    def __unicode__(self):
        return self.nombre
    def __str__(self):
        return self.nombre
    
class User(db.Model,UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(400))
    prevLogin=db.Column(db.DateTime)
    lastLogin=db.Column(db.DateTime,default=datetime.datetime.now)
    role_id = mapped_column(ForeignKey("roles.id"))
    role = relationship("Roles", back_populates="usuarios")  
    bloqueado = db.Column(db.Integer,default=0)
    producciones_user = relationship("Produccion", back_populates="user")
    ventas_user = relationship("Venta", back_populates="user")
    compras_user = relationship("Compra", back_populates="user")
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    def __unicode__(self):
        return self.login
    def __str__(self):
        return self.login
    

class Insumo(db.Model):
    __tablename__='insumo'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(80))
    insumo_inventario = relationship("Insumo_Inventario", back_populates="insumo")
    insumo_ingredientes = relationship("Ingredientes_Receta", back_populates="insumo")
    # compras = relationship("Detalle_Compra", back_populates="insumo")
    medida_id = mapped_column(ForeignKey("medida.id"))
    medida = relationship("Medida", back_populates="insumo_medida")  
    insumo_merma_produccion = relationship("Merma_Produccion", back_populates="insumo")
    abastecimiento = relationship("Abastecimiento", back_populates="insumo")  
    def __str__(self):
        return self.nombre+" ("+self.medida.medida+")"

class Proveedor(db.Model):
    __tablename__='proveedor'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80))
    direccion=db.Column(db.String(90))
    telefono=db.Column(db.BigInteger)
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
    insumos_produccion = relationship("Insumos_Produccion", back_populates="insumo_inventario")  
    def __str__(self):
        out = str(self.insumo) #+ ' ' + str(self.proveedor) #+ ' '  + str(self.anaquel)
        return out
    
class Producto_Inventario(db.Model):
    __tablename__='producto_inventario'
    id=db.Column(db.Integer,primary_key=True)
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="inventario")  
    produccion_id = mapped_column(ForeignKey("produccion.id"))
    produccion = relationship("Produccion", back_populates="producto_inventario")
    cantidad = db.Column(db.Integer)
    producto_inventario_detalle = relationship("Producto_Inventario_Detalle", back_populates="producto_inventario")  
    merma = relationship("Merma_Producto", back_populates="producto") 
    # responsable = None
    def __str__(self):
        out = str(self.producto) #+ ' ' + str(self.proveedor) #+ ' '  + str(self.anaquel)
        return out 
    
    # @property
    # def responsable(self):
    #     res = db.session.query(Producto_Inventario,text('responsable')).from_statement(text("""
    #         SELECT
    #         US.LOGIN AS Responsable
    #         FROM PRODUCTO_INVENTARIO PINV
    #         JOIN PRODUCCION PR ON PR.ID = PINV.PRODUCCION_ID
    #         JOIN USER US ON US.ID = PR.USER_ID
    #         WHERE PINV.ID = {}
    #         """.format(self.id))
            
    #     ).first()
    #     return res.Responsable


class Abastecimiento(db.Model):
    __tablename__='abastecimiento'
    id=db.Column(db.Integer,primary_key=True)
    descripcion=db.Column(db.String(255))
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="abastecimiento")  
    cantidad_insumo=db.Column(db.Float)
    detalle_compra = relationship("Detalle_Compra", back_populates="abastecimiento")
    def __str__(self):
        out = str(self.descripcion) #+ ' '  + str(self.anaquel)
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
    user_id = mapped_column(ForeignKey("user.id"))
    user = relationship("User", back_populates="compras_user")  
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
    abastecimiento = relationship("Abastecimiento", back_populates="detalle_compra")  
    caducidad=db.Column(db.Date,default=date.today())
    subtotal=db.Column(db.Float)
    cantidad=db.Column(db.Float)
    def __str__(self):
        out = str(self.abastecimiento.descripcion) +  " (Cantidad:" + str(int(self.cantidad)) + ") " + " Caduca el Día : " + str(self.caducidad) + "."
        return out

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
    producciones = relationship("Produccion", back_populates="receta")
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
    def __str__(self):
        out = str(self.insumo.nombre) +  " (Cantidad:" + str(int(self.cantidad)) + " " + self.insumo.medida.medida +")" 
        return out

class Produccion(db.Model):
    __tablename__='produccion'
    id=db.Column(db.Integer,primary_key=True)
    fecha_hora=db.Column(db.DateTime,default=datetime.datetime.now)
    user_id = mapped_column(ForeignKey("user.id"))
    user = relationship("User", back_populates="producciones_user")  
    #nuevos campos de detalle
    insumos_produccion = relationship("Insumos_Produccion", back_populates="produccion")  
    cantidad=db.Column(db.Float)
    receta_id = mapped_column(ForeignKey("receta.id"))
    receta = relationship("Receta", back_populates="producciones") 
    mermas = relationship("Merma_Produccion", back_populates="produccion")  
    producto_inventario = relationship("Producto_Inventario", back_populates="produccion")
    estatus = db.Column(db.Integer)
    def __str__(self):
        return str(self.fecha_hora)

class Insumos_Produccion(db.Model):
    __tablename__='Insumos_Produccion'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    produccion_id = mapped_column(ForeignKey("produccion.id"))
    produccion = relationship("Produccion", back_populates="insumos_produccion")  
    insumo_inventario_id = mapped_column(ForeignKey("insumo_inventario.id"))
    insumo_inventario = relationship("Insumo_Inventario", back_populates="insumos_produccion")  

class Merma_Produccion(db.Model):
    __tablename__='merma_produccion'
    id=db.Column(db.Integer,primary_key=True)
    cantidad=db.Column(db.Float)
    produccion_id = mapped_column(ForeignKey("produccion.id"))
    produccion = relationship("Produccion", back_populates="mermas")  
    insumo_id = mapped_column(ForeignKey("insumo.id"))
    insumo = relationship("Insumo", back_populates="insumo_merma_produccion")  
    descripcion=db.Column(db.String(300))

class Producto(db.Model):
    __tablename__='producto'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(255))
    receta = relationship("Receta", back_populates="producto_receta")  
    presentacion = relationship("Presentacion", back_populates="producto")
    inventario = relationship("Producto_Inventario", back_populates="producto")  
    detalle_venta = relationship("Detalle_Venta", back_populates="producto")
    orden = relationship("Orden", back_populates="producto")  
    peso =db.Column(db.Float)
    precio =db.Column(db.Float)
    solicitudesProduccion = relationship("SolicitudesProduccion", back_populates="producto")
    def __str__(self):
        return self.nombre

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
    estatus=db.Column(db.Integer)

class Venta(db.Model):
    __tablename__='venta'
    id=db.Column(db.Integer,primary_key=True)
    hora=db.Column(db.DateTime,default=datetime.datetime.now)
    user_id = mapped_column(ForeignKey("user.id"))
    user = relationship("User", back_populates="ventas_user")  
    total_venta =db.Column(db.Float)
    detalle_venta = relationship("Detalle_Venta", back_populates="venta")

class Detalle_Venta(db.Model):
    __tablename__='detalle_venta'
    id=db.Column(db.Integer,primary_key=True)
    presentacion_id = mapped_column(ForeignKey("presentacion.id"),nullable=True)
    presentacion = relationship("Presentacion", back_populates="detalle_venta")
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="detalle_venta")
    venta_id = mapped_column(ForeignKey("venta.id"))
    venta = relationship("Venta", back_populates="detalle_venta")
    producto_inventario_detalle = relationship("Producto_Inventario_Detalle", back_populates="detalle_venta")  
    subtotal = db.Column(db.Float)
    cantidad = db.Column(db.Float)
    def __str__(self):
        if not self.presentacion_id:
            return self.producto.nombre+" ("+str(int(self.cantidad))+")"
        else:
            return self.presentacion.nombre+" ("+str(int(self.cantidad))+")"

# Que producto del inventatio se utilizo en el detalle
class Producto_Inventario_Detalle(db.Model):
    __tablename__='producto_inventario_detalle'
    id=db.Column(db.Integer,primary_key=True)
    producto_inventario_id = mapped_column(ForeignKey("producto_inventario.id"))
    producto_inventario = relationship("Producto_Inventario", back_populates="producto_inventario_detalle")
    detalle_venta_id = mapped_column(ForeignKey("detalle_venta.id"))
    detalle_venta = relationship("Detalle_Venta", back_populates="producto_inventario_detalle")  
    cantidad = db.Column(db.Float)

class Medida(db.Model):
    __tablename__='medida'
    id=db.Column(db.Integer,primary_key=True)
    medida=db.Column(db.String(100))
    insumo_medida = relationship("Insumo", back_populates="medida")  
    def __str__(self):
        return self.medida

class Presentacion(db.Model):
    __tablename__='presentacion'
    id=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(100))
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="presentacion")
    cantidad_producto=db.Column(db.Integer)  
    precio=db.Column(db.Float)
    detalle_venta = relationship("Detalle_Venta", back_populates="presentacion")
    def __str__(self):
        return self.medida
    
    #TODO:AÑADIR PRODUCTOS_DETALLE

class SolicitudesProduccion(db.Model):
    __tablename__='solicitudes_produccion'
    id=db.Column(db.Integer,primary_key=True)
    producto_id = mapped_column(ForeignKey("producto.id"))
    producto = relationship("Producto", back_populates="solicitudesProduccion")
    cantidad_solicitada=db.Column(db.Integer)  
    def __str__(self):
        return self.id
